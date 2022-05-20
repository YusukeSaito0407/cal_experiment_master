# 数値実験を行うための実行ファイル
# アルゴリズムやソルバーを他のファイルから読み込むためのファイル

# 実験データについては、先行研究では実際のネットワークを基に、枝の損傷具合をパラメータとして与えていた
# とりあえず模擬データでいいのでは？

import glob
import os
import re
import csv
import solve.exact_solution as exact

# complete or random (complete == 0, random == 1)
COMPLETE_RANDOM = 1

# マシン台数のリスト
MACHINE_LIST = [1,3,5,10]

# 変数の数および制約の数を出力するファイル
if COMPLETE_RANDOM == 0:
    count_result = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", "exact_complete_count.csv")
else:
    count_result = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", "exact_random_count.csv")

# データファイルを取得

if COMPLETE_RANDOM == 0:
    data_list = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_data", "complete", "*.txt"))
else:
    data_list = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_data", "random", "*.txt"))


with open(count_result, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["data file path", "# of machine", "# of node", "formulation", "# of variables", "# of constraint"])
    for data_file in data_list:
        file_name_without_txt = os.path.splitext(os.path.basename(data_file))[0]
        node_seed = file_name_without_txt.split("_")
        node_number = re.sub(r"\D", "", node_seed[0])
        seed_number = re.sub(r"\D", "", node_seed[1])
        for machine in MACHINE_LIST:
            for form_p in [0,1]:
                if form_p == 0:
                    print("=========node:{} seed:{} machine:{} formulation:single_flow".format(node_number, seed_number, machine))
                else:
                    print("=========node:{} seed:{} machine:{} formulation:multi_flow".format(node_number, seed_number, machine))
                

                # 緩めな納期

                loose_dealine = int(node_number) * 100 // ( 3 * machine)
                # loose_dealine = int(node_number) * 100 // ( 2 * machine)
                loose_log_filename = "node{}_seed{}_machine{}_loose_formulation{}.log".format(node_number, seed_number, machine, form_p)
                if COMPLETE_RANDOM == 0:
                    loose_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_log", "complete", loose_log_filename)
                else:
                    loose_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_log", "random", loose_log_filename)
                
                v, c = exact.optimal(dot_file_path=data_file, deadline=loose_dealine, machine=machine, log_path=loose_log_path, formulation=form_p)
                

                # csvに書き込み
                writer.writerow([data_file, machine, node_number, form_p, v, c])

                # きつめな納期
                tight_dealine = int(node_number) * 100 // ( 5 * machine)
                # tight_dealine = int(node_number) * 100 // ( 4 * machine)
                tight_log_filename = "node{}_seed{}_machine{}_tight_formulation{}.log".format(node_number, seed_number, machine, form_p)
                if COMPLETE_RANDOM == 0:
                    tight_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_log", "complete", tight_log_filename)
                else:
                    tight_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_log", "random", tight_log_filename)

                v, c = exact.optimal(dot_file_path=data_file, deadline=tight_dealine, machine=machine, log_path=tight_log_path, formulation=form_p)        

                # csvに書き込み
                writer.writerow([data_file, machine, node_number, form_p, v, c])
