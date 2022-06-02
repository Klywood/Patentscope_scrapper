import json
import os

"""
You can copy last IPC classification from:
https://www.wipo.int/classifications/ipc/en/ITsupport/Version20220101/index.html

"""


res = {}
for fl in os.listdir('classes'):
    fl = os.path.join('classes', fl)
    with open(fl, 'r', encoding='utf8') as file:
        data = file.readlines()
        for i in data:
            #  разделяем имя класса и определение
            cls, key = i.strip().split('\t')
            if len(cls) <= 4:
                #  ключи - ПРОПИСНЫЕ слова, разделенные символом ';'
                key = [i for i in key.split('; ') if i == i.upper()]
                if len(key) > 0:
                    res[cls] = key

print(res)
print(len(res))
with open('IPC.json', 'w', encoding='utf-8') as ipc:
    json.dump(res, ipc, indent=2)
