# 完全グラフのサンプルデータを作成するプログラム
import numpy as np
import os

# NODE_NUMBER_LIST = [10, 30, 50, 70]
NODE_NUMBER_LIST = [20, 40, 60, 80]
WEIGHT_MAX = 100
PROCESSING_TIME_MAX = 100

for NODE_NUMBER in NODE_NUMBER_LIST:
    for i in range(10):
        f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "approx_data", "random", "node{}_seed{}.txt".format(NODE_NUMBER, i+NODE_NUMBER)), 'w')
        np.random.seed(i+NODE_NUMBER) # 乱数を固定させる
        for v1 in range(NODE_NUMBER):
            for v2 in range(v1, NODE_NUMBER):
                if v1 != v2:
                    if np.random.rand() <= 0.5:
                        weight = np.random.randint(0, WEIGHT_MAX+1)
                        process_time = np.random.randint(0, PROCESSING_TIME_MAX+1)
                        edge_information = "{} {} {} {}\n".format(v1, v2, weight, process_time)
                        f.write(edge_information)
        f.close()
print("データ作成完了")