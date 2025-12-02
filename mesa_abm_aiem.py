#!/usr/bin/env python3
"""
Abstract Illicit Ecology Model (AIEM) - メインスクリプト
学術研究・政策評価用の抽象化されたシミュレーション実行環境

使用方法:
    python mesa_abm_aiem.py --steps 200 --seed 42 --scenario scenarios/example.yaml
"""

import argparse
import yaml
from datetime import datetime
from pathlib import Path
import pandas as pd

from src.model import AIEMModel


def load_scenario(scenario_path):
    """YAMLシナリオファイルを読み込む"""
    if not scenario_path or not Path(scenario_path).exists():
        return None

    with open(scenario_path, 'r', encoding='utf-8') as f:
        scenario = yaml.safe_load(f)

    return scenario


def run_simulation(config):
    """シミュレーションを実行"""
    print(f"=== Abstract Illicit Ecology Model (AIEM) ===")
    print(f"研究目的: 政策介入効果の比較評価")
    print(f"Steps: {config['steps']}")
    print(f"Seed: {config['seed']}")
    print()

    # モデル初期化
    model_params = config.get('model_params', {})
    model = AIEMModel(
        n_leaders=model_params.get('n_leaders', 5),
        n_operatives=model_params.get('n_operatives', 30),
        n_brokers=model_params.get('n_brokers', 10),
        n_facilitators=model_params.get('n_facilitators', 8),
        n_community_members=model_params.get('n_community_members', 50),
        n_authorities=model_params.get('n_authorities', 3),
        network_k=model_params.get('network_k', 4),
        network_p=model_params.get('network_p', 0.3),
        initial_monitoring_capacity=model_params.get('initial_monitoring_capacity', 0.5),
        economic_stress_level=model_params.get('economic_stress_level', 0.5),
        seed=config['seed'],
    )

    # 介入スケジュール
    interventions = config.get('interventions', [])

    print("シミュレーション実行中...")
    for step in range(config['steps']):
        # スケジュールされた介入を適用
        for intervention in interventions:
            if intervention['step'] == step:
                print(f"  Step {step}: 介入 '{intervention['type']}' (強度: {intervention['intensity']})")
                model.apply_policy_intervention(
                    intervention['type'],
                    intervention['intensity']
                )

        model.step()

        # 進捗表示
        if (step + 1) % 50 == 0:
            print(f"  Step {step + 1}/{config['steps']} 完了")

    print("シミュレーション完了\n")

    return model


def save_results(model, output_path):
    """結果をCSVファイルに保存"""
    df = model.datacollector.get_model_vars_dataframe()

    # 出力ディレクトリ作成
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path)
    print(f"結果を保存: {output_path}")

    # サマリー表示
    print("\n=== シミュレーション結果サマリー ===")
    print(f"最終Active Operatives: {df['ActiveOperatives'].iloc[-1]:.0f}")
    print(f"最終Active Leaders: {df['ActiveLeaders'].iloc[-1]:.0f}")
    print(f"最終Active Brokers: {df['ActiveBrokers'].iloc[-1]:.0f}")
    print(f"総逮捕数: {df['ArrestsThisStep'].sum():.0f}")
    print(f"総通報数: {df['ReportsThisStep'].sum():.0f}")
    print(f"最終ネットワーク密度: {df['NetworkDensity'].iloc[-1]:.4f}")
    print(f"最終平均クラスタリング係数: {df['AverageClustering'].iloc[-1]:.4f}")


def main():
    parser = argparse.ArgumentParser(
        description='Abstract Illicit Ecology Model (AIEM) シミュレータ'
    )
    parser.add_argument(
        '--steps',
        type=int,
        default=100,
        help='シミュレーションステップ数 (デフォルト: 100)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='ランダムシード (デフォルト: None)'
    )
    parser.add_argument(
        '--scenario',
        type=str,
        default=None,
        help='YAMLシナリオファイルのパス'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='出力CSVファイルのパス'
    )

    args = parser.parse_args()

    # シナリオ読み込み
    scenario = load_scenario(args.scenario)

    # 設定の構築
    config = {
        'steps': args.steps,
        'seed': args.seed,
    }

    if scenario:
        print(f"シナリオ読み込み: {args.scenario}")
        print(f"  名前: {scenario.get('name', 'N/A')}")
        print(f"  説明: {scenario.get('description', 'N/A')}\n")

        # シナリオからパラメータをマージ
        if 'model_params' in scenario:
            config['model_params'] = scenario['model_params']
        if 'interventions' in scenario:
            config['interventions'] = scenario['interventions']
        # シナリオのstepsを優先
        if 'steps' in scenario:
            config['steps'] = scenario['steps']

    # シミュレーション実行
    model = run_simulation(config)

    # 結果保存
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/run_{timestamp}.csv"

    save_results(model, output_path)


if __name__ == "__main__":
    main()
