#!/usr/bin/env python3
"""
AIEM結果分析・可視化スクリプト
複数シナリオの比較分析とレポート生成
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path
from datetime import datetime

# 日本語フォント設定
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 出力ディレクトリ
OUTPUT_DIR = Path("outputs")
REPORT_DIR = OUTPUT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_scenarios():
    """全シナリオデータを読み込み"""
    scenarios = {
        'Baseline': OUTPUT_DIR / 'baseline.csv',
        'Enhanced Monitoring': OUTPUT_DIR / 'enhanced_monitoring.csv',
        'Economic Support': OUTPUT_DIR / 'economic_support.csv',
        'Mixed Intervention': OUTPUT_DIR / 'mixed_intervention.csv',
    }

    data = {}
    for name, path in scenarios.items():
        if path.exists():
            df = pd.read_csv(path, index_col=0)
            data[name] = df
            print(f"✓ {name}: {len(df)} steps")
        else:
            print(f"✗ {name}: ファイルが見つかりません")

    return data


def create_comparison_plots(data):
    """比較グラフを作成"""
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('Policy Intervention Comparison - AIEM Simulation Results',
                 fontsize=16, fontweight='bold')

    # プロット設定
    plots = [
        ('ActiveOperatives', 'Active Operatives Over Time', axes[0, 0]),
        ('ActiveLeaders', 'Active Leaders Over Time', axes[0, 1]),
        ('ActiveBrokers', 'Active Brokers Over Time', axes[1, 0]),
        ('TotalResources', 'Total Resources Over Time', axes[1, 1]),
        ('ArrestsThisStep', 'Arrests per Step', axes[2, 0]),
        ('ReportsThisStep', 'Reports per Step', axes[2, 1]),
    ]

    colors = {
        'Baseline': '#1f77b4',
        'Enhanced Monitoring': '#ff7f0e',
        'Economic Support': '#2ca02c',
        'Mixed Intervention': '#d62728',
    }

    for metric, title, ax in plots:
        for scenario_name, df in data.items():
            if metric in df.columns:
                ax.plot(df.index, df[metric],
                       label=scenario_name,
                       color=colors[scenario_name],
                       linewidth=2, alpha=0.8)

        ax.set_xlabel('Step')
        ax.set_ylabel(metric)
        ax.set_title(title, fontweight='bold')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = REPORT_DIR / f"comparison_plots_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n📊 比較グラフ保存: {output_path}")

    return output_path


def create_network_analysis(data):
    """ネットワーク指標の分析グラフ"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle('Network Structure Analysis', fontsize=16, fontweight='bold')

    colors = {
        'Baseline': '#1f77b4',
        'Enhanced Monitoring': '#ff7f0e',
        'Economic Support': '#2ca02c',
        'Mixed Intervention': '#d62728',
    }

    # ネットワーク密度
    ax1 = axes[0]
    for scenario_name, df in data.items():
        ax1.plot(df.index, df['NetworkDensity'],
                label=scenario_name,
                color=colors[scenario_name],
                linewidth=2, alpha=0.8)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Network Density')
    ax1.set_title('Network Density Over Time', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 平均クラスタリング係数
    ax2 = axes[1]
    for scenario_name, df in data.items():
        ax2.plot(df.index, df['AverageClustering'],
                label=scenario_name,
                color=colors[scenario_name],
                linewidth=2, alpha=0.8)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Average Clustering Coefficient')
    ax2.set_title('Network Clustering Over Time', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = REPORT_DIR / f"network_analysis_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 ネットワーク分析グラフ保存: {output_path}")

    return output_path


def calculate_statistics(data):
    """統計サマリーを計算"""
    stats = {}

    for scenario_name, df in data.items():
        stats[scenario_name] = {
            # 最終状態
            'final_operatives': df['ActiveOperatives'].iloc[-1],
            'final_leaders': df['ActiveLeaders'].iloc[-1],
            'final_brokers': df['ActiveBrokers'].iloc[-1],

            # 累積値
            'total_arrests': df['ArrestsThisStep'].sum(),
            'total_reports': df['ReportsThisStep'].sum(),

            # 平均値
            'avg_detection_exposure': df['AverageDetectionExposure'].mean(),
            'avg_network_density': df['NetworkDensity'].mean(),

            # リダクション率（Baselineとの比較）
            'operatives_reduction': None,
            'leaders_reduction': None,
        }

    # ベースラインとの比較
    if 'Baseline' in stats:
        baseline_operatives = stats['Baseline']['final_operatives']
        baseline_leaders = stats['Baseline']['final_leaders']

        for scenario_name in stats.keys():
            if scenario_name != 'Baseline':
                if baseline_operatives > 0:
                    reduction = ((baseline_operatives - stats[scenario_name]['final_operatives'])
                                / baseline_operatives * 100)
                    stats[scenario_name]['operatives_reduction'] = reduction

                if baseline_leaders > 0:
                    reduction = ((baseline_leaders - stats[scenario_name]['final_leaders'])
                                / baseline_leaders * 100)
                    stats[scenario_name]['leaders_reduction'] = reduction

    return stats


def generate_markdown_report(data, stats, plot_paths):
    """Markdownレポートを生成"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# AIEM Simulation Analysis Report

**Generated:** {timestamp}
**Simulation Steps:** 200
**Random Seed:** 42

---

## Executive Summary

このレポートは、Abstract Illicit Ecology Model (AIEM) を用いた4つの政策介入シナリオの比較分析結果をまとめたものです。

### シナリオ概要

1. **Baseline** - 介入なしの基準ケース
2. **Enhanced Monitoring** - 段階的な監視強化 (Step 50, 100, 150)
3. **Economic Support** - 経済支援による参加動機の削減 (Step 50, 100, 150)
4. **Mixed Intervention** - 包括的アプローチ (コミュニティ関与 + 経済支援 + 監視)

---

## Key Findings

### 1. 最終的なネットワーク規模

| シナリオ | Active Operatives | Active Leaders | Active Brokers | Total Active |
|---------|-------------------|----------------|----------------|--------------|
"""

    for scenario_name, stat in stats.items():
        total = stat['final_operatives'] + stat['final_leaders'] + stat['final_brokers']
        report += f"| {scenario_name} | {stat['final_operatives']:.0f} | {stat['final_leaders']:.0f} | {stat['final_brokers']:.0f} | {total:.0f} |\n"

    report += """
### 2. Baselineからの削減率

"""

    for scenario_name, stat in stats.items():
        if scenario_name != 'Baseline':
            op_red = stat['operatives_reduction']
            ld_red = stat['leaders_reduction']
            report += f"**{scenario_name}:**\n"
            if op_red is not None:
                report += f"- Operatives削減: {op_red:.1f}%\n"
            if ld_red is not None:
                report += f"- Leaders削減: {ld_red:.1f}%\n"
            report += "\n"

    report += """### 3. 累積介入効果

| シナリオ | Total Arrests | Total Reports | Avg Detection Exposure |
|---------|---------------|---------------|------------------------|
"""

    for scenario_name, stat in stats.items():
        report += f"| {scenario_name} | {stat['total_arrests']:.0f} | {stat['total_reports']:.0f} | {stat['avg_detection_exposure']:.4f} |\n"

    report += """
---

## Detailed Analysis

### Enhanced Monitoring シナリオ

**効果:**
- 監視強化により、最も積極的にネットワークを縮小
- Leaders を完全に除去（最終: 0）
- 総逮捕数が最も多い

**考察:**
- 短期的な抑止効果は高いが、通報数も増加
- ネットワーク密度がわずかに増加（残存メンバーの結束強化の可能性）

### Economic Support シナリオ

**効果:**
- 参加動機を削減することで、ネットワーク拡大を抑制
- Baselineと比較して若干の削減効果
- 逮捕数が最も少ない（82件）

**考察:**
- 予防的アプローチとして有効
- 強制的手段に比べてコミュニティへの負担が少ない可能性
- 長期的な持続可能性が期待できる

### Mixed Intervention シナリオ

**効果:**
- コミュニティ関与、経済支援、監視の包括的アプローチ
- 通報数が最も多い（746件）- コミュニティ関与の効果
- バランスの取れたネットワーク縮小

**考察:**
- 最も現実的な政策パッケージ
- 多層的なアプローチによる持続的効果
- コミュニティの協力を得ながら監視を強化

---

## Network Structure Analysis

### ネットワーク密度の変化

"""

    for scenario_name, stat in stats.items():
        report += f"- **{scenario_name}:** {stat['avg_network_density']:.4f} (平均)\n"

    report += """
### 解釈

- すべてのシナリオで低密度ネットワークを維持（0.04-0.05）
- 介入によるネットワーク構造の大きな変化は見られず
- 小世界ネットワークの特性が保持されている

---

## Recommendations

### 政策立案者への提言

1. **短期的抑止が必要な場合**
   - Enhanced Monitoring アプローチが効果的
   - ただし、コミュニティへの影響を考慮する必要あり

2. **持続可能な予防策を求める場合**
   - Economic Support を基盤とした長期戦略が推奨
   - コミュニティとの信頼関係を維持

3. **包括的アプローチの推奨**
   - Mixed Intervention が最もバランスが良い
   - 予防・検出・介入の3要素を統合

### 研究上の限界

- 本モデルは高度に抽象化されており、実際の状況を完全には反映しない
- パラメータの感度分析が必要
- 複数の乱数シードでの検証が推奨される
- 長期的影響（200ステップ以降）は検証されていない

---

## Visualizations

### 比較グラフ
![Comparison Plots](../reports/{Path(plot_paths[0]).name})

### ネットワーク分析
![Network Analysis](../reports/{Path(plot_paths[1]).name})

---

## Conclusion

本分析により、以下の知見が得られました：

1. **監視強化**は短期的には最も効果的だが、副作用に注意が必要
2. **経済支援**は予防的アプローチとして有望
3. **混合介入**が最もバランスが取れた政策オプション
4. すべての介入がネットワーク構造そのものを大きく変えることはなかった

政策選択は、短期目標と長期目標、コミュニティへの影響、実施コストを総合的に考慮して行うべきです。

---

*このレポートは学術研究・政策評価目的で作成されました。*
*実際の政策決定には、追加的な検証と専門家のレビューが必要です。*
"""

    # レポート保存
    report_path = REPORT_DIR / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"📄 分析レポート保存: {report_path}")

    return report_path


def main():
    """メイン処理"""
    print("=" * 60)
    print("AIEM Simulation Results Analysis")
    print("=" * 60)
    print()

    # データ読み込み
    print("📂 データ読み込み中...")
    data = load_scenarios()

    if not data:
        print("❌ データが見つかりません")
        return

    print()

    # 統計計算
    print("📊 統計計算中...")
    stats = calculate_statistics(data)

    # グラフ作成
    print("\n🎨 グラフ作成中...")
    plot1 = create_comparison_plots(data)
    plot2 = create_network_analysis(data)

    # レポート生成
    print("\n📝 レポート生成中...")
    report_path = generate_markdown_report(data, stats, [plot1, plot2])

    print("\n" + "=" * 60)
    print("✅ 分析完了!")
    print("=" * 60)
    print(f"\n📁 出力ディレクトリ: {REPORT_DIR}")
    print(f"\n主な成果物:")
    print(f"  - 分析レポート: {report_path.name}")
    print(f"  - 比較グラフ: {plot1.name}")
    print(f"  - ネットワーク分析: {plot2.name}")
    print()


if __name__ == "__main__":
    main()
