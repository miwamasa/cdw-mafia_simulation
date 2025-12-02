# Abstract Illicit Ecology Model (AIEM)

逸脱的ネットワークの生態系モデリングと政策評価シミュレータ

## 概要

このプロジェクトは、社会科学研究・政策評価を目的とした抽象化されたエージェントベースモデル（ABM）シミュレータです。逸脱的ネットワーク（組織化された違法活動集団の抽象化）を社会・経済環境と相互作用する「生態系」としてモデル化し、政策介入や予防策の効果を比較評価します。

**重要**: 本システムは学術研究および政策立案の支援を目的としており、具体的な違法行為の手法や実行方法は含まれていません。すべてのモデルは抽象化されており、戦術・運用レベルの詳細は意図的に排除されています。

## 想定ユーザー

- 社会科学研究者
- 政策立案者
- 司法・公的予防機関
- 市民安全研究チーム（非営利／学術）

## 主な機能

- **エージェントベースモデリング**: Leader, Operative, Broker, Facilitator, CommunityMember, Authority の6種類のエージェントタイプ
- **ネットワーク構造**: Watts-Strogatz小世界モデルによる社会ネットワーク
- **政策介入シミュレーション**: 監視強化、経済支援、コミュニティ関与の3種類の介入
- **シナリオベース実験**: YAMLファイルによる柔軟なシナリオ定義
- **データ収集**: 時系列データのCSV出力による分析サポート

## インストール

### 必要な環境

- Python 3.8以上
- pip

### セットアップ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使い方

### 基本的な実行

```bash
# デフォルト設定で実行（100ステップ）
python mesa_abm_aiem.py

# ステップ数を指定して実行
python mesa_abm_aiem.py --steps 200

# ランダムシードを指定して実行
python mesa_abm_aiem.py --steps 200 --seed 42
```

### シナリオを使った実行

```bash
# ベースラインシナリオ（介入なし）
python mesa_abm_aiem.py --scenario scenarios/baseline.yaml

# 監視強化シナリオ
python mesa_abm_aiem.py --scenario scenarios/enhanced_monitoring.yaml

# 経済支援シナリオ
python mesa_abm_aiem.py --scenario scenarios/economic_support.yaml

# 混合介入シナリオ
python mesa_abm_aiem.py --scenario scenarios/mixed_intervention.yaml

# サンプルシナリオ
python mesa_abm_aiem.py --scenario scenarios/example.yaml
```

### 出力先の指定

```bash
# 出力ファイル名を指定
python mesa_abm_aiem.py --scenario scenarios/baseline.yaml --output outputs/baseline_run.csv
```

## プロジェクト構造

```
cdw-mafia_simulation/
├── README.md                  # このファイル
├── requirements.txt           # 依存パッケージ
├── instructions.md            # プロジェクト指示書
├── mesa_abm_aiem.py          # メインスクリプト
├── spec/                      # 仕様ドキュメント
│   ├── spcification.md       # 詳細仕様書
│   └── prototype.md          # プロトタイプ説明
├── src/                       # ソースコード
│   ├── __init__.py
│   ├── agents.py             # エージェントクラス
│   └── model.py              # モデルクラス
├── scenarios/                 # シナリオファイル
│   ├── baseline.yaml
│   ├── enhanced_monitoring.yaml
│   ├── economic_support.yaml
│   ├── mixed_intervention.yaml
│   └── example.yaml
└── outputs/                   # 出力ファイル（実行時に生成）
```

## シナリオファイルの作成

YAMLファイルで独自のシナリオを定義できます：

```yaml
name: "カスタムシナリオ"
description: "シナリオの説明"

steps: 200

model_params:
  n_leaders: 5
  n_operatives: 30
  n_brokers: 10
  n_facilitators: 8
  n_community_members: 50
  n_authorities: 3
  network_k: 4
  network_p: 0.3
  initial_monitoring_capacity: 0.5
  economic_stress_level: 0.6

interventions:
  - step: 50
    type: "monitoring"  # または "economic_support", "community_engagement"
    intensity: 0.6      # 0.0 ~ 1.0
```

## 出力データの分析

実行後、CSV形式で時系列データが出力されます。以下の指標が含まれます：

- `ActiveLeaders`: アクティブなリーダー数
- `ActiveOperatives`: アクティブな実行者数
- `ActiveBrokers`: アクティブな仲介者数
- `ActiveFacilitators`: アクティブなファシリテーター数
- `TotalResources`: 総資源量
- `AverageDetectionExposure`: 平均検出露出度
- `ArrestsThisStep`: 当該ステップでの逮捕数
- `ReportsThisStep`: 当該ステップでの通報数
- `NetworkDensity`: ネットワーク密度
- `AverageClustering`: 平均クラスタリング係数

## モデルの抽象化原則

1. **役割の抽象化**: 機能的・社会的役割で表現し、具体的手口はモデル化しない
2. **資源の抽象化**: 資金の「流動量」、信頼の「社会資本スコア」などの抽象指標
3. **出力の限定**: 政策評価指標（被害想定、ネットワーク脆弱性、検出可能性）に限定

## エージェントタイプ

- **Leader**: 組織的統制要素、戦略決定に関与
- **Operative**: 実行者、個人行動の主体
- **Broker**: 仲介者、異なるサブネット間の接続媒介
- **Facilitator**: フロント／合法的接点
- **CommunityMember**: 一般市民、被害感受性と通報可能性を持つ
- **Authority**: 法執行・規制機関

## 政策介入タイプ

1. **monitoring**: 監視強化 - 当局の監視能力を向上
2. **economic_support**: 経済支援 - 経済的ストレスを軽減し参加動機を減少
3. **community_engagement**: コミュニティ関与 - 市民の通報傾向を向上

## 倫理的配慮

- 本研究ツールは学術・政策研究目的に限定されています
- 実際の違法行為の手法最適化につながる仕様は含まれていません
- データは原則として公開データまたは合成データを使用します
- 個人特定情報（PII）は扱いません

## ライセンス

本プロジェクトは学術研究・政策評価目的に限定して使用されることを前提としています。

## 参考文献

詳細な理論的背景と設計思想については、`spec/spcification.md` を参照してください。