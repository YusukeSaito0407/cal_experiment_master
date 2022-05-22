import networkx as nx
import matplotlib.pyplot as plt
import pulp
import sys
import os


def multi_optimal_solution(Graph, deadline=6, machine=2, log_path="sample_log.log"):
    # 重みwと処理時間pのデータ保持
    w = {}
    p = {}
    for e in list(Graph.edges(data=True)):
        w[e[0:2]] = e[2]['weight']
        p[e[0:2]] = e[2]['process_time']

    # 繰り返し使うものをあらかじめ導出
    edge_list = list(Graph.edges())
    node_list = list(Graph.nodes())
    number_of_node = len(node_list)

    # 数理最適化問題を宣言
    lrp = pulp.LpProblem("MIP_problem", pulp.LpMinimize)

    ## 変数宣言
    variable_number = 0
    # 枝を全域木で使用するか否か
    x = {}
    for e in edge_list:
        x[e] = pulp.LpVariable("x_{}".format(e), 0, 1, "Binary")
        variable_number += 1

    # フロー変数
    f = {}
    for e in edge_list:
        f[e] = pulp.LpVariable("f_{}".format(e), 0, sys.maxsize, "Continuous")
        variable_number += 1
        rev_e = tuple((e[1], e[0]))
        f[rev_e] = pulp.LpVariable("f_{}".format(rev_e), 0, sys.maxsize, "Continuous")
        variable_number += 1

    # どのマシンでどの枝を処理するか
    z = {}
    for e in edge_list:
        for k in range(machine):
            machine_edge_tuple = tuple([k, e[0], e[1]])
            z[machine_edge_tuple] = pulp.LpVariable("z_{}_{}".format(k,e), 0, 1, "Binary")
            variable_number += 1

    ## 定式化
    # 目的関数を宣言
    lrp += pulp.lpSum(w[e] * x[e] for e in edge_list), "Objective"
    
    # 制約条件を宣言
    constraint_number = 0
    # 全域木は|V|-1
    lrp += pulp.lpSum(x[e] for e in edge_list) == number_of_node - 1, "Consraint1"
    constraint_number += 1

    # 始点のフロー量|V|-1
    f_0 = {}
    f_rev_0 = {}
    for e, f_v in f.items():
        if e[0] == 0:
            f_0[e] = f_v
        
    lrp += pulp.lpSum(f[e] for e in f_0) == number_of_node - 1, "Consraint2"
    constraint_number += 1

    # フロー量は1ずつ減少
    for v in node_list:
        if v!= 0:
            f_rev_i = {}
            f_i = {}
            for e, f_v in f.items():
                if e[1] == v:
                    f_rev_i[e] = f_v
                if e[0] == v:
                    f_i[e] = f_v                
            lrp += pulp.lpSum(f[e] for e in f_rev_i) - pulp.lpSum(f[e] for e in f_i) == 1, "Constraint3_{}".format(v)
            constraint_number += 1   

    # 容量制約
    for e in edge_list:
        lrp += f[e] <= (number_of_node - 1)*x[e], "Constraint4_{}".format(e)
        constraint_number += 1
        e_rev = tuple([e[1], e[0]])
        lrp += f[e_rev] <= (number_of_node - 1)*x[e], "Constraint4_rev_{}".format(e)
        constraint_number += 1


    # 納期制約
    for k in range(machine):
        lrp += pulp.lpSum(p[e] * z[tuple([k, e[0], e[1]])] for e in edge_list) <= deadline, "Constraint5_{}".format(k)
        constraint_number += 1

    # 1つの枝を複数台のマシンで処理しない
    for e in edge_list:
        lrp += pulp.lpSum(z[tuple([k, e[0], e[1]])] for k in range(machine)) == x[e], "Constraint6_{}".format(e)
        constraint_number += 1

    print("問題作成完了")

    # ソルバー
    solver = pulp.CPLEX_CMD(threads=8, timeLimit=3600, logPath=log_path)

    # 問題を解く
    result = lrp.solve(solver)
    return x, variable_number, constraint_number
    # print(result)

def multi_optimal_solution_ver_MCF(Graph, deadline=6, machine=2, log_path="sample_log.log"):
    # 重みwと処理時間pのデータ保持
    w = {}
    p = {}
    for e in list(Graph.edges(data=True)):
        w[e[0:2]] = e[2]['weight']
        p[e[0:2]] = e[2]['process_time']

    # 繰り返し使うものをあらかじめ導出
    edge_list = list(Graph.edges())
    node_list = list(Graph.nodes())
    number_of_node = len(node_list)

    # 数理最適化問題を宣言
    lrp = pulp.LpProblem("MIP_problem", pulp.LpMinimize)

    ## 変数宣言
    variable_number = 0
    # 枝を全域木で使用するか否か
    print("変数宣言開始")
    x = {}
    for e in edge_list:
        x[e] = pulp.LpVariable("x_{}".format(e), 0, 1, "Binary")
        variable_number += 1

    # フロー変数
    f = {}
    for l in range(1, number_of_node):
        for e in edge_list:
            tuple_e = tuple((l, e[0], e[1]))
            f[tuple_e] = pulp.LpVariable("f_{}_{}".format(l, e), -1, 1, "Continuous")
            variable_number += 1
            rev_e = tuple((l, e[1], e[0]))
            f[rev_e] = pulp.LpVariable("f_{}_{}".format(l, rev_e), -1, 1, "Continuous")
            variable_number += 1

    # どのマシンでどの枝を処理するか
    z = {}
    for e in edge_list:
        for k in range(machine):
            machine_edge_tuple = tuple([k, e[0], e[1]])
            z[machine_edge_tuple] = pulp.LpVariable("z_{}_{}".format(k,e), 0, 1, "Binary")
            variable_number += 1

    print("定式化開始")
    ## 定式化
    # 目的関数を宣言
    lrp += pulp.lpSum(w[e] * x[e] for e in edge_list), "Objective"
    
    # 制約条件を宣言
    constraint_number = 0
    # 全域木は|V|-1
    lrp += pulp.lpSum(x[e] for e in edge_list) == number_of_node - 1, "Consraint1"
    constraint_number += 1

    # フロー量のバランス制約
    for v in node_list:
        if v == 0:
            for l in range(1, number_of_node):
                f_0 = {}
                f_rev_0 = {}
                for e, f_v in f.items():
                    if e[1] == 0 and e[0] == l:
                        f_0[e] = f_v
                    if e[2] == 0 and e[0] == l:
                        f_rev_0[e] = f_v
                lrp += pulp.lpSum(f[e] for e in f_0) - pulp.lpSum(f[e] for e in f_rev_0) == 1, "Consraint2_{}".format(l)
                constraint_number += 1
        if v!= 0:
            for l in range(1, number_of_node):
                f_rev_i = {}
                f_i = {}
                for e, f_v in f.items():
                    if e[1] == v and e[0] == l:
                        f_i[e] = f_v
                    if e[2] == v and e[0] == l:
                        f_rev_i[e] = f_v
                if v != l:               
                    lrp += pulp.lpSum(f[e] for e in f_i) - pulp.lpSum(f[e] for e in f_rev_i) == 0, "Constraint3_{}_{}".format(l, v)
                    constraint_number += 1    
                if v == l:               
                    lrp += pulp.lpSum(f[e] for e in f_i) - pulp.lpSum(f[e] for e in f_rev_i) == -1, "Constraint3_{}_{}".format(l, v)
                    constraint_number += 1
    
    
    # 容量制約
    for l in range(1, number_of_node):
        for e in edge_list:
            tuple_e = tuple((l, e[0], e[1]))
            lrp += f[tuple_e] <= x[e], "Constraint4u_{}_{}".format(l,e)
            constraint_number += 1
            lrp += f[tuple_e] >= -x[e], "Constraint4d_{}_{}".format(l,e)
            constraint_number += 1
            e_rev = tuple([l, e[1], e[0]])
            lrp += f[e_rev] <= x[e], "Constraint4u_rev_{}_{}".format(l,e)
            constraint_number += 1
            lrp += f[e_rev] >= -x[e], "Constraint4d_rev_{}_{}".format(l,e)
            constraint_number += 1


    # 納期制約
    for k in range(machine):
        lrp += pulp.lpSum(p[e] * z[tuple([k, e[0], e[1]])] for e in edge_list) <= deadline, "Constraint5_{}".format(k)
        constraint_number += 1

    # 1つの枝を複数台のマシンで処理しない
    for e in edge_list:
        lrp += pulp.lpSum(z[tuple([k, e[0], e[1]])] for k in range(machine)) == x[e], "Constraint6_{}".format(e)
        constraint_number += 1

    print("問題作成完了")

    # ソルバー
    solver = pulp.CPLEX_CMD(threads=8, timeLimit=3600, logPath=log_path)

    # 問題を解く
    result = lrp.solve(solver)
    return x, variable_number, constraint_number

# formulationは、0なら単品種、1なら多品種
def optimal(dot_file_path=".\data\sample_graph.txt", deadline=6, machine=1, log_path="sample.log", formulation=0):
    # 無向グラフの作成
    G = nx.Graph()

    # ファイルの読み込み
    G = nx.read_edgelist(dot_file_path, nodetype=int, data=(("process_time", float),("weight", float),))

    # deadlineを超える枝の削除
    for e in list(G.edges(data=True)):
        if e[2]['process_time'] > deadline:
            G.remove_edges_from([e])
    
    # 最適解を求める
    if formulation == 0:
        # 単品種フロー定式化
        x, v, c = multi_optimal_solution(G, deadline=deadline, machine=machine, log_path=log_path)
    else:
        # 多品種フロー定式化
        x, v, c = multi_optimal_solution_ver_MCF(G, deadline=deadline, machine=machine, log_path=log_path)

    print("変数の数:{} 制約の数:{}".format(v,c))

    # 確認用
    T = nx.minimum_spanning_tree(G, weight='weight')
    T_weight = 0
    for e in T.edges(data=True):
        T_weight += e[2]['weight']
    print("minimum spanning tree real value: {}".format(T_weight))
    print(nx.is_tree(T))   

    
    print("optimal success")

    return v, c

def main():
    optimal(dot_file_path=".\data\sample_complete_graph.txt", deadline=50, machine=10)
    print("main process")


if __name__ == '__main__':
    # ライブラリ動作確認用
    main()