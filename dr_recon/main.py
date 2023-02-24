'''
Author: tansen
Date: 2023-02-05 10:31:13
LastEditors: tansen
LastEditTime: 2023-02-05 11:11:50
'''

from dr_recon import DataRecon


config_args = {
    "path_gl": r"C:\Users\Desktop\dr\gl.xlsx",  # 序时账的路径
    "path_tb": r"C:\Users\Desktop\dr\tb.xlsx",  # 余额表的路径
    "save_name": "test1",  # 保存的文件名(不用写后缀名)
    "save_path": r"C:\Users\Desktop\dr",  # 保存文件的路径
}


if __name__ == "__main__":
    print("start running...")
    data_recon = DataRecon(
        path_gl=config_args["path_gl"],
        path_tb=config_args["path_tb"],
        save_name=config_args["save_name"],
        save_path=config_args["save_path"]
    )
    print("end of run.")
