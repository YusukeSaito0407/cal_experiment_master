import csv
import os
import glob
import re
import numpy as np

# complete or random (complete == 0, random == 1)
COMPLETE_RANDOM = 1

MACHINE_LIST = [1, 3, 5, 10]

# ログファイルの在りか
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result")
if COMPLETE_RANDOM == 0:
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_log", "complete")
    RESULT_CSV = os.path.join(RESULT_DIR, "approx_complete.csv")
    RESULT_AVE_CSV = os.path.join(RESULT_DIR, "approx_ave_complete.csv")
    NODE_LIST = [20, 40, 60, 80]
else:
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_log", "random")
    RESULT_CSV = os.path.join(RESULT_DIR, "approx_random.csv")
    RESULT_AVE_CSV = os.path.join(RESULT_DIR, "approx_ave_random.csv")
    NODE_LIST = [20, 40, 60, 80]


# ログファイルのパスをリスト形式で取得
solver_file_list = glob.glob(os.path.join(LOG_DIR, "solver", "*.log"))
approx_file = os.path.join(LOG_DIR, "algorithm", "approx.csv")

# csv用にファイルごとにデータを加工
with open(RESULT_CSV, "w", newline='') as g:
    writer = csv.writer(g)
    writer.writerow(["#node", "#seed", "#machine", "loose or tight", "solver calculation time", "algorithm calculation time", "approx ratio"])
    for solver_file_path in solver_file_list:
        solver_file_name = os.path.splitext(os.path.basename(solver_file_path))[0]
        info_list = solver_file_name.split("_")
        # print(info_list)
        info = []
        for i in range(len(info_list)-1):
            if i != 3:
                info.append(re.sub(r"\D", "", info_list[i]))
        info.append(info_list[3])
        with open(solver_file_path) as f:
            for line in f:
                if "Total (root+branch&cut)" in line:
                    m = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                    info.append(m[0])
                    break
        # print(info)
        with open(approx_file, encoding='utf8', newline='') as g:
            csvreader = csv.reader(g)
            header = next(csvreader)
            for row in csvreader:
                node_seed = os.path.splitext(os.path.basename(row[0]))[0].split("_")
                # print(row)
                # break
                if re.sub(r"\D", "", node_seed[0]) == info[0] and re.sub(r"\D", "", node_seed[1]) == info[1] and row[1] == info[2] and row[2] == info[3]:
                    info.append(row[10])
                    if row[9] == "" or float(row[5]) < 0:
                        info.append(None)
                    else:
                        info.append(float(row[9])/float(row[3]))
        # print(info)
        writer.writerow(info)
        # break

# 生データをaverageに変換
with open(RESULT_AVE_CSV, "w", newline='') as h:
    writer = csv.writer(h)
    writer.writerow(["#machine", "#node", "solver calculation time", "#solver valid data", "approx calculation time", "approx ratio ave", "approx ratio worst", "#approx ratio valid"])
    for m in MACHINE_LIST:
        for v in NODE_LIST:
            solver_ave_list = []
            approx_ave_list = []
            solver_valid_c = 0
            with open(RESULT_CSV, encoding='utf8', newline='') as g:
                csvreader = csv.reader(g)
                header = next(csvreader)
                for row in csvreader:
                    if row[0] == str(v) and row[2] == str(m):
                        # ソルバーデータに組み込むものを選別
                        if float(row[4]) >= 3600:
                            row[4] = 3600
                            solver_valid_c += 1
                        solver_ave_list.append(row)
                        # 近似アルゴリズムに含めるかを選別
                        if row[6] != "":
                            approx_ave_list.append(row)
                      
            ave_data = [m, v]
            # ソルバー平均計算時間
            ave_data.append(np.average([float(a[4]) for a in solver_ave_list]))
            # ソルバーの有効データ数
            ave_data.append(len(solver_ave_list) - solver_valid_c)
            if approx_ave_list == []:
                ave_data.append(None)
                ave_data.append(None)
                ave_data.append(None)
            else:
                # 近似アルゴリズムの平均計算時間
                ave_data.append(np.average([float(a[5]) for a in approx_ave_list]))
                # 近似アルゴリズムの平均近似率
                ave_data.append(np.average([float(a[6]) for a in approx_ave_list]))
                # 近似アルゴリズムの最悪近似率
                ave_data.append(max([float(a[6]) for a in approx_ave_list]))
            # 近似アルゴリズムの有効データ数
            ave_data.append(len(approx_ave_list))
            # csvに書き込み
            writer.writerow(ave_data)



print("csv書き込み完了")