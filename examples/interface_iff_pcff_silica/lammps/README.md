# LAMMPS inputs

このディレクトリには、計算段階ごとに重複を統合した LAMMPS 入力だけを置く。
同じ段階で実行内容が分岐する場合は、別ファイルを増やさず `MODE` で切り替える。

| 段階 | ファイル | `MODE` | 役割 |
|---|---|---|---|
| ① | `in.01_bulk_relax.lmp` | `shake` | SHAKE を用いた高温バルク緩和 |
| ① | `in.01_bulk_relax.lmp` | `generic` | 材料非依存の通常バルク緩和 |
| ② | `in.02_surface_create.lmp` | `create` | z 周期境界を開いて自由表面を作成 |
| ② | `in.02_surface_create.lmp` | `relax` | 材料非依存の表面作成・緩和を一括実行 |
| ③・④ | `in.03_surface_relax.lmp` | `reference` | バイアスなしの自由表面緩和 |
| ③・④ | `in.03_surface_relax.lmp` | `branch` | 同一 reference から control/bias を分岐 |
| ③・④ | `in.03_surface_relax.lmp` | `pilot` | reference を作らない短縮比較 |
| ⑤ | `in.05_merge.lmp` | — | polymer と substrate の data をマージ |
| ⑥ | `in.06_interface_relax.lmp` | — | 基板上で加圧・高温緩和・冷却・除荷 |
| ⑦ | `in.07_interaction.lmp` | `sample` | GPU で室温 trajectory を採取 |
| ⑦ | `in.07_interaction.lmp` | `rerun` | CPU PPPM で保存 frame の相互作用を分解 |
| ⑦ | `in.07_interaction.lmp` | `direct` | CPU で trajectory と相互作用を同時計算 |
| ⑧ | `in.08_smd.lmp` | `frames` | SMD 用の初期 restart を生成 |
| ⑧ | `in.08_smd.lmp` | `pull` | 各 restart から定速 SMD 引張 |

④は独立した必須ファイルではない。自由表面偏析を比較するときだけ
`in.03_surface_relax.lmp -var MODE branch` を使用する。現在の推奨 production
経路は③のバイアスなし表面緩和後に⑤で基板とマージし、⑥を単一路線で実行する。
界面バイアス条件および強バイアス診断は含めない。

## 実行例

各ファイルの `variable ... index ...` は既定値であり、コマンドラインから
上書きできる。

```bash
lmp -in lammps/in.03_surface_relax.lmp \
  -var MODE reference \
  -var RESTART surface_start.restart \
  -var T_HIGH 500.0 \
  -var N_REF 1000000
```

実行スクリプトは既定でこのディレクトリを参照する。互換性のある別入力セットは
環境変数で差し替えられる。

```bash
POLYCE_LAMMPS_INPUT_DIR=/path/to/lammps-inputs ./run_interface_40k.sh
```

入力ファイルには実行ディレクトリの絶対パスを固定せず、data/restart 名、温度、
圧力、ステップ数、原子数、型番号は `-var` で渡す。
