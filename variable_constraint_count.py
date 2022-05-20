import csv
import os
import glob
import numpy as np
import re

# complete or random (complete == 0, random == 1)
COMPLETE_RANDOM = 1

# マシン台数のリスト
MACHINE_LIST = [1,3,5,10]

# 変数の数および制約の数が入力されているファイル
if COMPLETE_RANDOM == 0:
    count_result = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", "exact_complete_count.csv")
    NODE_LIST = [10, 20, 30, 50]
else:
    count_result = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", "exact_random_count.csv")
    NODE_LIST = [10, 30, 50, 70]

# 変数の数および制約の数の平均を出力するファイル
if COMPLETE_RANDOM == 0:
    count_result_ave = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", "exact_complete_count_ave.csv")
else:
    count_result_ave = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", "exact_random_count_ave.csv")

# 指定のcsvに書き込む
with open(count_result_ave, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["# of machine", "# of node", "formulation", "# of variables", "# of constraint"])
    for m in MACHINE_LIST:
        for n in NODE_LIST:
            for form_p in [0,1]:
                data_list = []
                with open(count_result, encoding='utf8', newline='') as g:
                    csvreader = csv.reader(g)
                    header = next(csvreader)
                    for row in csvreader:
                        if row[1] == str(m) and row[2] == str(n) and row[3] == str(form_p):
                            data_list.append(row)
                ave_list = [m, n, form_p]
                ave_list.append(np.average([float(a[4]) for a in data_list]))
                ave_list.append(np.average([float(a[5]) for a in data_list]))
                writer.writerow(ave_list)
        
