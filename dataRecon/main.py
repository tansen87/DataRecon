'''
Author: tansen
Date: 2023-02-13 09:49:54
LastEditors: tansen
LastEditTime: 2023-02-13 10:29:35
'''
from read_yaml import ReadYaml
from data_recon import DataRecon


if __name__ == "__main__":
    print("\033[35mstart running...\033[0m")
    yaml_path = "config/kingdee.yaml"
    yaml_file = ReadYaml(yaml_path)
    content = yaml_file.read()
    recon = DataRecon(
        path_gl=content["path_gl"],
        path_tb=content["path_tb"],
        save_name=content["save_name"],
        save_path=content["save_path"],
        opening=content["opening"],
        closing=content["closing"],
        debit=content["debit"],
        credit=content["credit"],
        company_gl=content["company_gl"],
        company_tb=content["company_tb"],
        account_gl=content["account_gl"],
        account_tb=content["account_tb"],
        position=content["position"],
        is_direction=content["is_direction"],
        is_lastAccount=content["is_lastAccount"],
        is_openDebit=content["is_openDebit"],
        open_oth=content["open_oth"],
        close_oth=content["close_oth"],
        symbol=content["symbol"],
        direction=content["direction"]
    )
    recon.pivot_data()
    print("\033[35mend of run.\033[0m")

    