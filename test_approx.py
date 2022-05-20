# 数値実験を行うための実行ファイル
# アルゴリズムやソルバーを他のファイルから読み込むためのファイル

# 実験データについては、先行研究では実際のネットワークを基に、枝の損傷具合をパラメータとして与えていた
# とりあえず模擬データでいいのでは？

import glob
import os
import re
import solve.exact_solution as exact
import solve.approximation_algorithm as approx
import csv

# マシン台数のリスト
MACHINE_LIST = [1,3,5,10]



# データファイルを取得
data_list = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_data", "random", "*.txt"))


# # 近似アルゴリズム
approx_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_log", "random", "algorithm", "approx.csv")
with open(approx_csv_path, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["data", "#machine", "loose or tight", "deadline", "#node", "z_star", "l(z_star)", "tree_exists", "satisfied_tree_W", "makespan", "calculation time"])
    for data_file in data_list:
        file_name_without_txt = os.path.splitext(os.path.basename(data_file))[0]
        node_seed = file_name_without_txt.split("_")
        node_number = re.sub(r"\D", "", node_seed[0])
        seed_number = re.sub(r"\D", "", node_seed[1])
        for machine in MACHINE_LIST:
            #### 緩めな納期
            loose_dealine = int(node_number) * 100 // ( 4 * machine)

            # 近似アルゴリズム実行
            schedule, z_star, LR, tree_exists, satisfied_tree_W, makespan, calculation_time = approx.two_opt(dot_file_path=data_file, deadline=loose_dealine, machine=machine)

            # csvに書き込み
            writer.writerow([data_file, machine, "loose", loose_dealine, node_number, z_star, LR, tree_exists, satisfied_tree_W, makespan, calculation_time])

            ##### きつめな納期
            tight_dealine = int(node_number) * 100 // ( 6 * machine)

            # 近似アルゴリズム実行
            schedule, z_star, LR, tree_exists, satisfied_tree_W, makespan, calculation_time = approx.two_opt(dot_file_path=data_file, deadline=tight_dealine, machine=machine)

            # csvに書き込み
            writer.writerow([data_file, machine, "tight", tight_dealine, node_number, z_star, LR, tree_exists, satisfied_tree_W, makespan, calculation_time])


# ソルバー
# for data_file in data_list:
#     file_name_without_txt = os.path.splitext(os.path.basename(data_file))[0]
#     node_seed = file_name_without_txt.split("_")
#     node_number = re.sub(r"\D", "", node_seed[0])
#     seed_number = re.sub(r"\D", "", node_seed[1])
#     for machine in MACHINE_LIST:
#         ######### 緩めな納期
#         loose_dealine = int(node_number) * 100 // ( 4 * machine)
#         # loose_dealine = int(node_number) * 100 // ( 2 * machine)
#         # ソルバーログパス指定
#         loose_log_filename = "node{}_seed{}_machine{}_loose_exact.log".format(node_number, seed_number, machine)
#         loose_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_log", "random", "solver", loose_log_filename)
        
#         # ソルバーの実行
#         exact.optimal(dot_file_path=data_file, deadline=loose_dealine, machine=machine, log_path=loose_log_path, formulation=0)
        
#         ########## きつめな納期
#         tight_dealine = int(node_number) * 100 // ( 6 * machine)
#         # tight_dealine = int(node_number) * 100 // ( 4 * machine)
#         # ソルバーログパス指定
#         tight_log_filename = "node{}_seed{}_machine{}_tight_exact.log".format(node_number, seed_number, machine)
#         tight_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_log", "random", "solver", tight_log_filename)

#         # ソルバーの実行
#         exact.optimal(dot_file_path=data_file, deadline=tight_dealine, machine=machine, log_path=tight_log_path, formulation=0)


