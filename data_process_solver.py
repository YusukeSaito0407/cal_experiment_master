import csv
import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt

# ログファイルの在りか
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_log", "random")

# 結果を出力するディレクトリ
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result")

# ログファイルのパスをリスト形式で取得
file_list = glob.glob(os.path.join(LOG_DIR, "*"))

# csv用にファイルごとにデータを加工
with open(os.path.join(RESULT_DIR, "exact_random.csv"), "w", newline='') as g:
    writer = csv.writer(g)
    writer.writerow(["file_path", "#node", "#seed", "#machine", "#formulation", "loose or tight", "caluculation time"])
    for file_path in file_list:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        info_list = file_name.split("_")
        info = [] # [file_path, #node, #seed, #machine, loose or tight, #formulation, caluculation time]
        info.append(file_path)
        for i in range(len(info_list)):
            if i != 3:
                info.append(re.sub(r"\D", "", info_list[i]))
        info.append(info_list[3])
        with open(file_path) as f:
            for line in f:
                if "Total (root+branch&cut)" in line:
                    m = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                    info.append(m[0])
                    break
            writer.writerow(info)

NODE_LIST = [10, 30, 50, 70]
MACHINE_LIST = [1, 3, 5, 10]
FORMULATION_LIST = [0, 1]

# 生データをaverageに変換
with open(os.path.join(RESULT_DIR, "exact_random_ave.csv"), "w", newline='') as h:
    writer = csv.writer(h)
    writer.writerow(["#machine", "#node", "formulation0 time", "formulation1 time"])
    for m in MACHINE_LIST:
        for v in NODE_LIST:
            for f in FORMULATION_LIST:
                ave_list = []
                with open(os.path.join(RESULT_DIR, "exact_random.csv"), encoding='utf8', newline='') as g:
                    csvreader = csv.reader(g)
                    header = next(csvreader)
                    for row in csvreader:
                        if row[1] == str(v) and row[3] == str(m) and row[4] == str(f):
                            ave_list.append(row)
                if f == 0:
                    ave_data = [m, v]
                # print(f, numpy.average([float(a[6]) for a in ave_list]))
                ave_data.append(np.average([float(a[6]) for a in ave_list]))
            writer.writerow(ave_data)

# with open(os.path.join(RESULT_DIR, "exact_ave.csv")) as f:
#     print(f.read())

# グラフを作成する
fig, axes = plt.subplots(2, 2, figsize=(4,6))
# 余白を設定
plt.subplots_adjust(wspace=0.4, hspace=0.6)
for j in range(len(MACHINE_LIST)):
    formulation0_data = [0, 0, 0, 0]
    formulation1_data = [0, 0, 0, 0]
    with open(os.path.join(RESULT_DIR, "exact_random_ave.csv"), encoding='utf8', newline='') as g:
        csvreader = csv.reader(g)
        header = next(csvreader)
        for row in csvreader:
            for i in range(len(NODE_LIST)):
                if row[0] == str(MACHINE_LIST[j]) and row[1] == str(NODE_LIST[i]):
                    formulation0_data[i] = float(row[2])
                    formulation1_data[i] = float(row[3])
    print(formulation0_data)
    axes[j//2, j%2].set_title("k={}".format(MACHINE_LIST[j]))
    axes[j//2, j%2].set_xlabel("# of nodes")
    axes[j//2, j%2].set_ylabel("calculation time (s)")
    axes[j//2, j%2].plot(NODE_LIST, formulation0_data, color = 'red', marker = 'o', label="SCF")
    axes[j//2, j%2].plot(NODE_LIST, formulation1_data, color = 'blue', marker = 'v', label="MCF")
    axes[j//2, j%2].legend()

plt.show()



print("csv書き込み完了")