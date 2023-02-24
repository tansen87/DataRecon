'''
Author: tansen
Date: 2023-02-04 21:26:17
LastEditors: Please set LastEditors
LastEditTime: 2023-02-24 21:55:03
'''

import os
from typing import Union

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame


class DataRaptorRecon:
    def __init__(
        self,
        path_gl: str,  # GL file path
        path_tb: str,  # TB file path
        save_name: Union[str, int],  # save file name
        save_path: str  # save file path
    ) -> None:
        self.path_gl = path_gl
        self.path_tb = path_tb
        self.save_name = save_name
        self.save_path = save_path
        self.pivot_data()

    def read_file(self, file_path: str) -> DataFrame:
        """ 读取文件 """
        try:
            data = pd.read_excel(file_path, dtype={"科目编号": object})
        except:
            data = pd.read_csv(file_path, dtype={"科目编号": object})
        return data

    def handle_gl(self) -> DataFrame:
        try:
            # read GL
            data = self.read_file(self.path_gl)
            # add columns: Account, TB opeing, TB closing
            data["Account"] = data["被审计单位"] + "_" + data["科目编号"]
            data["TB opening"] = None
            data["TB closing"] = None
            # get Amount for GL
            try:
                data["GL amount"] = data["借方发生额"] - data["贷方发生额"]
            except:
                data["借方发生额"] = data["借方发生额"].astype("float32")
                data["贷方发生额"] = data["贷方发生额"].astype("float32")
                data["GL amount"] = data["借方发生额"] - data["贷方发生额"]
            print(
                f"step 1 -> read GL: {os.path.basename(self.path_gl)} successfully.")
            return data.loc[:, ["Account", "TB opening", "TB closing", "GL amount"]]
        except Exception as e:
            print(f"read GL Error: {e}.")

    def handle_tb(self) -> DataFrame:
        try:
            # read TB
            data = self.read_file(self.path_tb)
            # add column: Account, TB opening, TB closing, GL amount
            data["Account"] = data["被审计单位"] + "_" + data["科目编号"]
            try:
                data["TB opening"] = data.apply(
                    lambda x: x["期初数"] if x["借贷方向"] == "借" else x["期初数"]*-1, axis=1)
                data["TB closing"] = data.apply(
                    lambda y: y["期末数"] if y["借贷方向"] == "借" else y["期末数"]*-1, axis=1)
            except:
                data["期初数"] = data["期初数"].astype("float32")
                data["期末数"] = data["期末数"].astype("float32")
                data["TB opening"] = data.apply(
                    lambda x: x["期初数"] if x["借贷方向"] == "借" else x["期初数"]*-1, axis=1)
                data["TB closing"] = data.apply(
                    lambda y: y["期末数"] if y["借贷方向"] == "借" else y["期末数"]*-1, axis=1)
            data["GL Amount"] = None
            print(
                f"step 2 -> read TB: {os.path.basename(self.path_tb)} successfully.")
            return data.loc[:, ["Account", "TB opening", "TB closing", "GL amount"]]
        except Exception as e:
            print(f"read TB Error {e}.")

    def merge_data(self) -> DataFrame:
        """ merege GL and TB """
        gl = self.handle_gl()
        tb = self.handle_tb()
        try:
            # merge GL and TB
            rt = pd.concat([gl, tb], axis=0, ignore_index=False, sort=False)
            rt["TB opening"] = rt["TB opening"].astype("float32")
            rt["TB closing"] = rt["TB closing"].astype("float32")
            rt["GL amount"] = rt["GL amount"].astype("float32")
            print("step 3 -> merge completed.")
            return rt
        except Exception as e:
            print(f"merge data Error: {e}.")

    def pivot_data(self) -> None:
        rt = self.merge_data()
        # pivot
        pt = pd.pivot_table(rt, index=['Account'], values=[
                            'TB opening', 'TB closing', 'GL amount'], aggfunc=np.sum)
        print(f"step 4 -> pivot completed.")
        # insert column
        pt.insert(loc=0, column="account", value=pt.index)
        # reset index
        pt.reset_index(drop=True, inplace=True)
        # calculate diff
        pt["Diff"] = pt["TB opening"] - pt["TB closing"] + pt["GL amount"]
        try:
            pt.to_excel(f"{self.save_path}/{self.save_name}.xlsx",
                        index=False, encoding="gbk")
            print(f"save path -> '{self.save_path}\\{self.save_name}.xlsx'")
        except Exception as e:
            print(f"pivot Error: {e}")
