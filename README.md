# 全域木設計スケジューリング問題に対するMIPおよび近似解法

[全域木設計スケジューリング問題](https://orsj.org/nc2022s/wp-content/uploads/sites/12/2022/03/2022s-2-B-4.pdf)に対する2種類の混合整数定式化および近似解法((2,1)-近似解法)を実装したソースコードである。

## 環境

著者の環境なので、あくまでも参考にしてください。ライブラリおよびソルバーについては用意しないとプログラムは動かないので注意。

- OS: Windows 11 Home
- CPU: Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz
- RAM: 16.00GB
- 言語: Python 3.9.9
  - ライブラリ: Networkx 2.5.1, PuLP 2.5.1, NumPy 1.19.5
- ソルバー: CPLEX 20.1.0.0
  - [ここを参考にインストール](https://qiita.com/nanametal_/items/ab9492193bf48e29b5ea)

##  ディレクトリ構造

```
|  data_process_approx.py  -> 数値実験のデータ加工用
│  data_process_solver.py  -> 数値実験のデータ加工用
│  data_product_complete_graph.py  -> 数値実験のデータ作成用
│  data_product_random_graph.py  -> 数値実験のデータ作成用
│  README.md  -> 本ドキュメント
│  test_approx.py  -> 数値実験実行プログラム
│  test_exact.py  -> 数値実験実行プログラム
│  variable_constraint_count.py -> 結果集計用プログラム
│
└─solve  -> アルゴリズム格納ディレクトリ
    │  approximation_algorithm.py  -> 近似解法
    │  exact_solution.py  -> MIPを解くプログラム
    │  sample_data_product.py  -> サンプルデータ作成プログラム
    │
    └─data  -> サンプルデータ
          sample_complete_graph.txt
```



## 動作確認

アルゴリズムが実際に動作しているかを確認するため、以下の手順で確認してください。(これは著者の環境での実行コマンドなので、あくまでも参考に)

1. `solve`ディレクトリに移動

   ```
   cd solve
   ```

2. サンプルデータを作成

   ```
   python sample_data_product.py
   ```

3. 近似解法の実行

   ```
   python approximation_algorithm.py
   ```

   このような出力が出てれば、実行できています(数値はあくまでも具体例)。

   ```
   input graph path:.\data\sample_complete_graph.txt deadline:50 machine:10
   z_star:0.2727272727272727 l(z_star):266.18181818181813
   greedy allocation complete!
   tree weight:264.0 makespan:75.0
   calculation time:0.01994633674621582
   ```

4. MIPを解くプログラムを実行

   ```
   python exact_solution.py
   ```

   CPLEXのログが出てくれば成功してます。実行には少し時間がかかるかも。