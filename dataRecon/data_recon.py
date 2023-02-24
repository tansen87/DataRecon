'''
Author: tansen
Date: 2023-02-09 23:46:35
LastEditors: tansen
LastEditTime: 2023-02-24 22:25:29
'''

import os
from typing import Union

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame


class DataRecon:
    def __init__(
            self, 
            path_gl: str,  # gl path
            path_tb: str,  # tb path
            save_name: str,  # file save name
            save_path: str,  # file save path
            opening: str,  # opening balance
            closing: str,  # closing balance
            debit: str,  # debit amount
            credit: str,  # credit amount
            company_gl: str,  # gl company name
            company_tb: str,  # tb company name
            account_gl: str,  # gl account code
            account_tb: str,  # tb account code
            position: int,  # position
            is_direction=False,  # 是否有借贷方向,默认无
            is_lastAccount=False,  # 是否取末级科目,默认无
            is_openDebit=False,  # tb是否有借贷,默认无
            open_oth: Union[str, None] = None,  # opening credit
            close_oth: Union[str, None] = None,  # closing credit
            symbol: Union[str, None] = None,  # 借方符号,默认无
            direction: Union[str, None] = None  # 借贷方向column name,默认无
        ) -> None:
        self.path_gl = path_gl
        self.path_tb = path_tb
        self.save_name = save_name
        self.save_path = save_path
        self.opening = opening
        self.closing = closing
        self.debit = debit
        self.credit = credit
        self.company_gl = company_gl
        self.company_tb = company_tb
        self.position = position
        self.account_gl = account_gl
        self.account_tb = account_tb
        self.is_direction = is_direction
        self.is_lastAccount = is_lastAccount
        self.is_openDebit = is_openDebit
        self.open_oth = open_oth
        self.close_oth = close_oth
        self.symbol = symbol
        self.direction = direction

    def read_file(self, file_path: str) -> DataFrame:
        """ read file """
        try:
            data = pd.read_excel(file_path)
        except:
            data = pd.read_csv(file_path)
        return data

    def handle_gl(self):
        """ handle GL """
        try:
            # read GL
            data = self.read_file(self.path_gl)
            data = data.fillna(0)
            # add column: Account, TB opening, TB closing, GL amount
            data["Account"] = data[self.company_gl] + "_" + data[self.account_gl]
            data["TB opening"] = None
            data["TB closing"] = None

            try:
                data["GL amount"] = data[self.debit] - data[self.credit]
            except:
                # if the type of debit and credit is not float, convert it's type to float32
                data[self.debit] = data[self.debit].astype("float32")
                data[self.credit] = data[self.credit].astype("float32")
                data["GL amount"] = data[self.debit] - data[self.credit]

            print(f"\033[36mstep 1 -> read GL {os.path.basename(self.path_gl)} successfully.\033[0m")  
            return data.loc[:, ["Account", "TB opening", "TB closing", "GL amount"]]

        except Exception as e:
            print(f"read GL Error: {e}.")
    
    def handle_tb(self) -> DataFrame:
        """ handle TB """
        try:
            # read TB
            data = self.read_file(self.path_tb)
            data["Account"] = data[self.company_tb] + "_" + data[self.account_tb]
            # get non-empty data
            data = data.loc[~data[self.account_tb].isnull()]

            # if end-level account is selected
            if self.is_lastAccount:
                data = self.get_last_account(data)
                data = data.fillna(0)
                data[self.opening] = data[self.opening].astype("float32")
                data[self.closing] = data[self.closing].astype("float32")
                # if TB contains debit or credit
                if self.is_openDebit:
                    data["TB opening"] = data[self.opening] - data[self.open_oth]
                    data["TB closing"] = data[self.closing] - data[self.close_oth]
                # if TB doesn't contain debit or credit
                if not self.is_openDebit:
                    data = self.get_direction(data)
            # if not end-levelaccount
            if not self.is_lastAccount:
                data[self.opening] = data[self.opening].astype("float32")
                data[self.closing] = data[self.closing].astype("float32")
                data = self.get_direction(data)
            data["GL amount"] = None
            print(f"\033[36mstep 2 -> read TB {os.path.basename(self.path_tb)} successfully.\033[0m")
            return data.loc[:, ["Account", "TB opening", "TB closing", "GL amount"]]

        except Exception as e:
            print(f"read TB Error: {e}.")

    def merge_data(self) -> DataFrame:
        """ merge gl and tb table"""
        gl = self.handle_gl()
        tb = self.handle_tb()
        try:
            rt = pd.concat([gl, tb], axis=0, ignore_index=False, sort=False)
            rt["TB opening"] = rt["TB opening"].astype("float32")
            rt["TB closing"] = rt["TB closing"].astype("float32")
            rt["GL amount"] = rt["GL amount"].astype("float32")
            print(f"\033[36mstep 3 -> merge {os.path.basename(self.path_gl)} and {os.path.basename(self.path_tb)} completed.\033[0m")
            return rt

        except Exception as e:
            print(f"merge data Error: {e}")

    def pivot_data(self) -> None:
        """ data pivot and recon """
        rt = self.merge_data()
        pt = pd.pivot_table(
            rt, index=['Account'], 
            values=['TB opening', 'TB closing', 'GL amount'], 
            aggfunc=np.sum)
        print(f"\033[36msetp 4 -> pivot completed.\033[0m")
        pt.insert(loc=0, column="Account", value=pt.index)
        pt["Diff"] = pt["TB opening"] - pt["TB closing"] + pt["GL amount"]
        try:
            pt.to_excel(f"{self.save_path}/{self.save_name}.xlsx", index=False, encoding="gbk")
            print(f"\033[36msave path -> '{self.save_path}\\{self.save_name}.xlsx'\033[0m")

        except Exception as e:
            print(f"pivot Error: {e}")

    def df_screen(self, df: DataFrame, cd: dict) -> DataFrame:
        """ data screen """
        df_cy = df.copy() 
        idx_z = [ True for i in df_cy.index]
        orcom  = lambda a, b: [ any([a[i],b[i]]) for i in range(len(a))]
        addcom  = lambda a, b: [ all([a[i],b[i]]) for i in range(len(a))]
        for z in cd:
            if isinstance(cd[z], list):
                for index,c in enumerate(cd[z]):
                    if index!=0:
                        idx_c = orcom(idx_c, list(df_cy[z] == c))
                    else:
                        idx_c = list(df_cy[z] == c)    
            else:
                idx_c = list(df_cy[z] == cd[z])
            idx_z = addcom(idx_z, idx_c)
        return df_cy.loc[idx_z, :]

    def get_last_account(self, data: DataFrame) -> DataFrame:
        """ get last account """
        cell = 0
        last_acc = []
        df_col = [col for col in data.columns]
        data_fr = pd.DataFrame(data, columns=df_col)
        while cell < len(data)-1:
            try:
                if data.iloc[cell, self.position-1] == data.iloc[cell+1, self.position-1][:len(data.iloc[cell, self.position-1])]:
                    pass
                else:
                    last_acc.append(data.iloc[cell, data.columns.get_loc("Account")])
                cell += 1
            except:
                break
        last_acc.append(data.iloc[len(data)-1, self.position-1])
        cd = {
            "Account": last_acc
        }
        data = self.df_screen(data_fr, cd)
        return data
    
    def get_direction(self, data: DataFrame) -> DataFrame:
        if self.is_direction:
            data["TB opening"] = data.apply(lambda x: x[self.opening] if x[self.direction] == self.symbol else x[self.direction] * -1, axis=1)
            data["TB closing"] = data.apply(lambda x: x[self.closing] if x[self.direction] == self.symbol else x[self.direction] * -1, axis=1)
        if not self.is_direction:
            data["TB opening"] = data[self.opening]
            data["TB closing"] = data[self.closing]
        return data
