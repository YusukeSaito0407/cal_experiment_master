import networkx as nx
import matplotlib.pyplot as plt
import pulp
import sys
import numpy as np
import itertools
import copy
import logging
import time
# import Yamada.yamada as yamada
# import Yamada.yamada_ver_cost as yamada_c


def z2slope(G, z, deadline=6, machine=1):
    # コストの追加 c = w+z*p
    for e in list(G.edges(data=True)):
        G[e[0]][e[1]]["cost"] = G[e[0]][e[1]]["weight"] + z * G[e[0]][e[1]]["process_time"]
        # print("w:{} p:{} z:{}".format(G[e[0]][e[1]]["weight"], G[e[0]][e[1]]["process_time"],z))
    T = nx.minimum_spanning_tree(G, weight='cost')
    slope =  - deadline * machine
    intercept = 0
    for e in list(T.edges(data=True)):
        slope += e[2]["process_time"]
        intercept += e[2]["weight"]

    return slope, intercept

# 本来はラグランジュ緩和問題を解く部分だが、z_starを探索するだけ
def lagrange_relaxation(G, deadline=6, machine=1):
    z_min = 0
    z_max = 1 # 便宜上おく

    # zの上界を計算する
    # コストの追加 c = w+z*p
    slope_max, intercept_max = z2slope(G, z=z_max, deadline=deadline, machine=machine)
    slope_min, intercept_min = z2slope(G, z=z_min, deadline=deadline, machine=machine)
    
    while slope_max > 0:
        z_max = z_max * 2
        slope_max, intercept_max = z2slope(G, z=z_max, deadline=deadline, machine=machine)
        # print("z_max:{} slope:{}".format(z_max,slope_max))
        # 発散するケースは除外
        if z_max > 10000000000:
            return -100
    

    # z_starを求める 探索範囲は、[z_min,z_max]
    if slope_min == 0:
        z = z_min
    elif slope_max == 0:
        z = z_max
    
    # ラグランジュ乗数が存在しない場合
    elif slope_min < 0:
        return 0
    else:
        while True:
            z = - (intercept_max - intercept_min) / (slope_max - slope_min)
            slope, intercept = z2slope(G, z=z, deadline=deadline, machine=machine)
            if z == z_min or z == z_max:
                break
            else:
                if slope > 0:
                    z_min = z
                    slope_min, intercept_min = z2slope(G, z=z_min, deadline=deadline, machine=machine)
                else:
                    z_max = z
                    slope_max, intercept_max = z2slope(G, z=z_max, deadline=deadline, machine=machine)
    
    # print("lagrange relaxation complete!")
    # print("z_star:{}".format(z))
    return z

# マシンに枝を割り当てていく関数        
def greedy_allocation(tree, schedule, machine=1):
    print("greedy allocation complete!")
    # マシンの現時点での処理時間の辞書(便宜上保持する)
    machine_time = {}
    for m in range(machine):
        machine_time["machine{}".format(m)] = 0
        if schedule["machine{}".format(m)] != []:
            for e in schedule["machine{}".format(m)]:
                machine_time["machine{}".format(m)] += e[2]["process_time"]

    # 最小負荷のマシンに枝を順次割り当てていく
    for e in tree:
        m_min = min(machine_time, key=machine_time.get)
        schedule[m_min].append(e)
        machine_time[m_min] += e[2]["process_time"]

    # print("処理時間:{}".format(machine_time[max(machine_time, key=machine_time.get)]))
    return schedule, machine_time[max(machine_time, key=machine_time.get)]

# データなしスケジュールに変換
def schedule2schedule_without_data(schedule):
    schedule_without_data = {}
    for k,v in schedule.items():
        schedule_without_data[k] = []
        for e in v:
            schedule_without_data[k].append((e[0],e[1]))

    return schedule_without_data

# 枝集合を与えた時のmakespanの最小値を計算(全列挙) ただし、pは枝集合を表すタプル
def min_makespan(p, machine=2):
    makespan = sum([e[2]["process_time"] for e in p])
    best_schedule = {}  
    for c in itertools.product(range(machine), repeat=len(p)):
        # print(c)
        schedule = {}
        machine_time = {}
        for m in range(machine):
            schedule["machine{}".format(m)] = []
            machine_time["machine{}".format(m)] = 0
        for i in range(len(c)):
            schedule["machine{}".format(c[i])].append(p[i])
            machine_time["machine{}".format(c[i])] += p[i][2]["process_time"]
        if machine_time[max(machine_time, key=machine_time.get)] < makespan:
            makespan = machine_time[max(machine_time, key=machine_time.get)]
            best_schedule = schedule
    
    return makespan, best_schedule

# T_minを求める
def solve_T_min(G, T):
    # z_starにおける枝の辞書式順序を求める
    edge_lex_order = sorted(list(G.edges(data=True)), key=lambda x:(x[2]["cost"], x[2]["process_time"]))

    T_list = sorted(list(T.edges(data=True)), key=lambda x:(x[2]["cost"], x[2]["process_time"]))

    # T_minを求める
    T_min = copy.deepcopy(T_list)
    for e in T_list:
        c = 0
        for e_ in T_min:
            if e[0] == e_[0] and e[1] == e_[1]:
                continue
            c += 1
        if c == len(T_min):
            continue
        edge_lex_order_without_T_eq = []
        for e_ in edge_lex_order:
            if e[2]["cost"] == e_[2]["cost"] and e[2]["process_time"] > e_[2]["process_time"]:
                edge_lex_order_without_T_eq.append(e_)
        if edge_lex_order_without_T_eq == []:
            continue
        for e_ in edge_lex_order_without_T_eq:
            # print(T_list_copy)
            # print(e)
            T_min.remove(e)
            T_min.append(e_)
            H = nx.Graph()
            H.add_nodes_from(range(len(T_list)+1))
            H.add_edges_from(T_min)
            if nx.is_tree(H):
                # print("treeになる")
                break
            else:
                # print("treeにならない")
                T_min.remove(e_)
                T_min.append(e) 

    return T_min

# T_maxを求める
def solve_T_max(G, T):
    # z_starにおける枝の辞書式順序を求める
    edge_lex_order = sorted(list(G.edges(data=True)), key=lambda x:(x[2]["cost"], x[2]["process_time"]), reverse=True)

    T_list = sorted(list(T.edges(data=True)), key=lambda x:(x[2]["cost"], x[2]["process_time"]), reverse=True)

    # T_maxを求める
    T_max = copy.deepcopy(T_list)
    for e in T_list:
        c = 0
        for e_ in T_max:
            if e[0] == e_[0] and e[1] == e_[1]:
                continue
            c += 1
        if c == len(T_max):
            continue
        edge_lex_order_without_T_eq = []
        for e_ in edge_lex_order:
            if e[2]["cost"] == e_[2]["cost"] and e[2]["process_time"] < e_[2]["process_time"]:
                edge_lex_order_without_T_eq.append(e_)
        if edge_lex_order_without_T_eq == []:
            continue
        for e_ in edge_lex_order_without_T_eq:
            # print(T_list_copy)
            # print(e)
            T_max.remove(e)
            T_max.append(e_)
            H = nx.Graph()
            H.add_nodes_from(range(len(T_list)+1))
            H.add_edges_from(T_max)
            if nx.is_tree(H):
                # print("treeになる")
                break
            else:
                # print("treeにならない")
                T_max.remove(e_)
                T_max.append(e) 

    return T_max

# 定理を満たす全域木を見つける
def find_satisfied_tree(T_min, T_max, machine, deadline):
    # T_minの処理時間の合計について以下の不等式が成り立つならば、全域木の重みはl(z_star)以下になる
    process_time_T_min = 0
    for e in T_min:
        process_time_T_min += e[2]["process_time"]
    if process_time_T_min >= machine * deadline:
        satisfied_tree = T_min
        return satisfied_tree
    else:
        T_max_not_T_min = []
        for e in T_max:
            c = 0
            for e_ in T_min:
                if e[0] == e_[0] and e[1] == e_[1]:
                    break
                c += 1
            if c == len(T_max):
                T_max_not_T_min.append(e)
        satisfied_tree = copy.deepcopy(T_min)
        for e in T_max_not_T_min:
            edge_cost_eq = []
            for e_ in satisfied_tree:
                if e[2]["cost"] == e_[2]["cost"] and e[2]["process_time"] > e_[2]["process_time"]:
                    edge_cost_eq.append(e_)
            if edge_cost_eq == []:
                continue
            for e_ in edge_cost_eq:
                satisfied_tree.remove(e_)
                satisfied_tree.append(e)
                H = nx.Graph()
                H.add_nodes_from(range(len(satisfied_tree)+1))
                H.add_edges_from(satisfied_tree)
                if nx.is_tree(H):
                    # print("treeになる")
                    process_time_satisfied_tree = 0
                    for e__ in satisfied_tree:
                        process_time_satisfied_tree += e__[2]["process_time"]
                    if process_time_satisfied_tree >= machine * deadline:
                        return satisfied_tree
                    else:
                        break
                else:
                    # print("treeにならない")
                    satisfied_tree.remove(e)
                    satisfied_tree.append(e_) 

# 2近似アルゴリズム
def two_opt(dot_file_path=".\data\sample_graph.txt", deadline=6, machine=1):
    tree_exists = 1

    # 実行時間計測開始
    start = time.time()    
    
    print("input graph path:{} deadline:{} machine:{}".format(dot_file_path, deadline, machine))
    
    # 無向グラフの作成
    G = nx.MultiGraph()

    # ファイルの読み込み
    G = nx.read_edgelist(dot_file_path, nodetype=int, data=(("process_time", float),("weight", float),))

    # 枝のラベル追加
    for e in list(G.edges(data=True)):
        # G[e[0]][e[1]]['label'] = str(e[0]) + ' ' + str(e[1])
        G[e[0]][e[1]]["label"] = tuple([e[0],e[1]])

    # 2-optじゃなければ、使用する枝の組合せ集合をここで作る

    # deadlineを超える枝の削除
    for e in list(G.edges(data=True)):
        if e[2]["process_time"] > deadline:
            G.remove_edges_from([e])
    
    # ラグランジュ緩和問題を解く(z_star>= 0)
    z_star = lagrange_relaxation(G, deadline=deadline, machine=machine)
    
    # 最小全域木が制約を満たしてしまっている場合
    if z_star == 0:
        T = nx.minimum_spanning_tree(G, weight='weight')
        satisfied_tree_W = 0
        for e in list(T.edges(data=True)):
            satisfied_tree_W += e[2]["weight"]
        LR = satisfied_tree_W

        # 得られた全域木をマシンに割り当てる
        schedule = {} # 2近似の場合は空で、PTASの場合は事前に計算しているものを入れる
        for m in range(machine):
            schedule["machine{}".format(m)] = []
        schedule, makespan = greedy_allocation(list(T.edges(data=True)), schedule, machine=machine)
        print("tree weight:{} makespan:{}".format(satisfied_tree_W, makespan))
        calculation_time = time.time() - start
        print("calculation time:{}".format(calculation_time))

    # アルゴリズムの本筋
    else:
        # コストの追加 c = w+z_star*p
        for e in list(G.edges(data=True)):
            G[e[0]][e[1]]["cost"] = G[e[0]][e[1]]["weight"] + z_star * G[e[0]][e[1]]["process_time"]

        # LR(最適値の上界)を求める
        T = nx.minimum_spanning_tree(G, weight='cost')
        T_value = 0
        for e in list(T.edges(data=True)):
            T_value += e[2]["cost"]
        LR = T_value - z_star * machine * deadline
        
        # print("z_star:{} 最適値の上界(LR):{}".format(z_star, LR))
        print("z_star:{} l(z_star):{}".format(z_star, LR))

        # T_minとT_max(枝のリストになっている)
        T_min = solve_T_min(G, T)
        T_max = solve_T_max(G, T)

        # 定理を満たす全域木を見つける
        satisfied_tree = find_satisfied_tree(T_min, T_max, machine, deadline)

        # 計算機の性質上どうしても条件を満たす全域木が見つけられない場合
        schedule = {}
        if satisfied_tree is None:
            tree_exists = 0
            satisfied_tree_W = None
            makespan = None
            calculation_time = None
            print("there is no satisfied tree!")
            return schedule, z_star, LR, tree_exists, satisfied_tree_W, makespan, calculation_time

        satisfied_tree_W = 0
        for e in satisfied_tree:
            satisfied_tree_W += e[2]["weight"]

        # 得られた全域木をマシンに割り当てる
        # schedule = {} # 2近似の場合は空で、PTASの場合は事前に計算しているものを入れる
        for m in range(machine):
            schedule["machine{}".format(m)] = []
        schedule, makespan = greedy_allocation(satisfied_tree, schedule, machine=machine)
        
        schedule = schedule2schedule_without_data(schedule)
        print("tree weight:{} makespan:{}".format(satisfied_tree_W, makespan))
        # logger.info("schedule:{}".schedule)

        calculation_time = time.time() - start
        print("calculation time:{}".format(calculation_time))

    return schedule, z_star, LR, tree_exists, satisfied_tree_W, makespan, calculation_time


# 1+epsilon近似アルゴリズム
def PTAS(dot_file_path=".\data\sample_graph.txt", deadline=6, machine=2, epsilon=0.5):
    # 無向グラフの作成
    G = nx.MultiGraph()

    # ファイルの読み込み
    G = nx.read_edgelist(dot_file_path, nodetype=int, data=(("process_time", float),("weight", float),))

    # 枝のラベル追加
    for e in list(G.edges(data=True)):
        # G[e[0]][e[1]]['label'] = str(e[0]) + ' ' + str(e[1])
        G[e[0]][e[1]]["label"] = tuple([e[0],e[1]])
    
    # deadlineを超える枝の削除
    for e in list(G.edges(data=True)):
        if e[2]["process_time"] > deadline:
            G.remove_edges_from([e])

    # ラグランジュ緩和問題を解く(z_star>= 0)
    z_star = lagrange_relaxation(G, deadline=deadline, machine=machine)

    # コストの追加 c = w+z_star*p
    for e in list(G.edges(data=True)):
        G[e[0]][e[1]]["cost"] = G[e[0]][e[1]]["weight"] + z_star * G[e[0]][e[1]]["process_time"]

    # LR(最適値の上界)を求める
    T = nx.minimum_spanning_tree(G, weight='cost')
    T_value = 0
    for e in list(T.edges(data=True)):
        T_value += e[2]["cost"]
    LR = T_value - z_star * machine * deadline

    # # p_maxを求め、kL+p_max(処理時間の上界)を求める
    # p_max = max([e[2]["process_time"] for e in list(G.edges(data=True))])
    # process_time_UB = machine * deadline + p_max
    
    # print("最適値の上界(LR):{} 処理時間の上界:{}".format(LR, process_time_UB))

    # >epsilon*Lの枝
    large_edge_number = int(np.ceil(machine / epsilon))
    large_edge_set = []
    for e in list(G.edges(data=True)):
        if e[2]["process_time"] > epsilon * deadline:
            large_edge_set.append(e)
    
    # 使用する枝の組合せ集合をここで作る
    large_edge_combination = []
    for i in range(1,large_edge_number):
        for p in itertools.combinations(large_edge_set, i):
            # 組合せの中に閉路が存在するならば、ループ終了
            try:
                H = nx.MultiGraph(p)
                cycle = nx.find_cycle(H)
                # print("閉路の数:{}".format(len(cycle)))
                continue
            except nx.exception.NetworkXNoCycle:
                # print("閉路はありません")
                pass
            # グラフにて縮約等の操作をループで行うためにコピー
            G_prime = G.copy()

            # マシンが1台の場合、deadlineを超える組合せは排除
            if machine == 1:
                if sum([e[2]["process_time"] for e in p]) <= deadline:
                    large_edge_combination.append(p)
                else:
                    continue
                makespan = sum([e[2]["process_time"] for e in p])
                schedule = {}
                schedule["machine0"] = []
                for e in p:
                    schedule["machine0"].append(e)
            # マシンが複数台の場合、deadlineを超える最小makespanならば排除
            else:
                makespan, schedule = min_makespan(p, machine=machine)
                if makespan <= deadline:
                    large_edge_combination.append(p)
                    # print("makespan:{}".format(makespan))
                else:
                    continue
            
            # 枝の縮約
            for e in p:
                G_prime_edge_list = list(G_prime.edges(data=True))
                for e_ in G_prime_edge_list:
                    if e[2]["label"] == e_[2]["label"]:
                        G_prime = nx.contracted_edge(G_prime, (e_[0], e_[1]), self_loops=False)
                        break
            
            # 枝の削除
            for e in list(G_prime.edges(data=True)):
                if e[2]["process_time"] > epsilon * deadline:
                    G_prime.remove_edges_from([e])

            # グラフが連結していないならば、ループを抜ける
            if not nx.is_connected(G_prime):
                continue

            # deadlineの更新
            deadline_prime = machine * deadline - sum([e[2]["process_time"] for e in p])

            # ラグランジュ乗数の計算
            z_star_prime = lagrange_relaxation(G_prime, deadline=deadline_prime, machine=1)
            if z_star_prime < 0:
                continue

            # コストの追加 c = w+z_star*p
            for e in list(G_prime.edges(data=True)):
                G_prime[e[0]][e[1]]["cost"] = G_prime[e[0]][e[1]]["weight"] + z_star_prime * G_prime[e[0]][e[1]]["process_time"]
            
            # print(z_star_prime)

            # # 定理を満たす全域木を求める
            p_max = max([e[2]["process_time"] for e in list(G_prime.edges(data=True))])
            satisfied_tree = MST_satisfied_with_theorem(G_prime, LR=LR- sum([e[2]["weight"] for e in p]), process_time_UB=deadline_prime+p_max)
            # 木が存在しているかどうか判定
            if satisfied_tree == []:
                continue
            W = 0
            P = 0
            for e in list(satisfied_tree.edges(data=True)):
                W += e[2]["weight"]
                P += e[2]["process_time"]
            for e in p:
                W += e[2]["weight"]
                P += e[2]["process_time"]
            print("重み:{} 処理時間:{}".format(W,P))
            break


def main():
    two_opt(dot_file_path=".\data\sample_complete_graph.txt", deadline=50, machine=10)
    # PTAS(dot_file_path=".\data\sample_complete_graph.txt", deadline=2000, machine=1, epsilon=1)


if __name__ == '__main__':
    # ライブラリ動作確認用
    main()