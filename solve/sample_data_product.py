# 完全グラフのサンプルデータを作成するプログラム
# 作成されるデータは、（頂点番号1, 頂点番号2, 枝の重み, 枝の処理時間)

import numpy as np

NODE_NUMBER = 30
WEIGHT_MAX = 100
PROCESSING_TIME_MAX = 100

f = open('data\sample_complete_graph.txt', 'w')

for v1 in range(NODE_NUMBER):
    for v2 in range(v1, NODE_NUMBER):
        if v1 != v2:
            weight = np.random.randint(1, WEIGHT_MAX)
            process_time = np.random.randint(1, PROCESSING_TIME_MAX)
            edge_information = "{} {} {} {}\n".format(v1, v2, weight, process_time)
            f.write(edge_information)
f.close()
print("データ作成完了")