'''
Author: tansen
Date: 2023-02-13 09:48:07
LastEditors: tansen
LastEditTime: 2023-02-13 09:58:18
'''

import yaml


class ReadYaml:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.read()

    def read(self):
        try:
            with open(self.file_path, 'r', encoding="utf-8") as f:
                content = yaml.load(f, Loader=yaml.FullLoader)
                return content
        except Exception as e:
            print(f"Read yaml file Error: {e}")

    def get_value(self, dataOne):
        return self.data[dataOne]
