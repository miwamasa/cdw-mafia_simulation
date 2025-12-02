"""
Abstract Illicit Ecology Model (AIEM) - Model Class
学術研究・政策評価用の抽象化されたシミュレーションモデル
"""

from mesa import Model
from mesa import DataCollector
import networkx as nx
import numpy as np
import random

from .agents import Leader, Operative, Broker, Facilitator, CommunityMember, Authority


class AIEMModel(Model):
    """
    Abstract Illicit Ecology Model (AIEM)
    逸脱的ネットワークを生態系としてモデル化
    """

    def __init__(
        self,
        n_leaders=5,
        n_operatives=30,
        n_brokers=10,
        n_facilitators=8,
        n_community_members=50,
        n_authorities=3,
        network_k=4,
        network_p=0.3,
        initial_monitoring_capacity=0.5,
        economic_stress_level=0.5,
        seed=None,
    ):
        super().__init__()
        if seed is not None:
            self.random.seed(seed)
            np.random.seed(seed)

        # パラメータ
        self.n_leaders = n_leaders
        self.n_operatives = n_operatives
        self.n_brokers = n_brokers
        self.n_facilitators = n_facilitators
        self.n_community_members = n_community_members
        self.n_authorities = n_authorities

        # 環境パラメータ
        self.economic_stress_level = economic_stress_level
        self.initial_monitoring_capacity = initial_monitoring_capacity

        # ネットワーク（Watts-Strogatz小世界モデル）
        total_agents = (
            n_leaders + n_operatives + n_brokers +
            n_facilitators + n_community_members + n_authorities
        )
        self.network = nx.watts_strogatz_graph(
            n=total_agents, k=network_k, p=network_p, seed=seed
        )

        # 統計追跡
        self.arrests_this_step = 0
        self.recent_arrest_rate = 0.0
        self.reports_this_step = 0

        # エージェント作成
        self._create_agents()

        # データ収集
        self.datacollector = DataCollector(
            model_reporters={
                "ActiveLeaders": lambda m: self.count_active_by_role("Leader"),
                "ActiveOperatives": lambda m: self.count_active_by_role("Operative"),
                "ActiveBrokers": lambda m: self.count_active_by_role("Broker"),
                "ActiveFacilitators": lambda m: self.count_active_by_role("Facilitator"),
                "TotalResources": lambda m: self.total_resources(),
                "AverageDetectionExposure": lambda m: self.average_detection_exposure(),
                "ArrestsThisStep": lambda m: m.arrests_this_step,
                "ReportsThisStep": lambda m: m.reports_this_step,
                "NetworkDensity": lambda m: nx.density(m.network),
                "AverageClustering": lambda m: nx.average_clustering(m.network),
            }
        )

        self.running = True

    def _create_agents(self):
        """エージェントを作成してネットワークに配置"""
        agent_id = 0

        # Leaders
        for _ in range(self.n_leaders):
            agent = Leader(agent_id, self)
            agent_id += 1

        # Operatives
        for _ in range(self.n_operatives):
            agent = Operative(agent_id, self)
            agent.economic_stress = self.economic_stress_level
            agent_id += 1

        # Brokers
        for _ in range(self.n_brokers):
            agent = Broker(agent_id, self)
            agent_id += 1

        # Facilitators
        for _ in range(self.n_facilitators):
            agent = Facilitator(agent_id, self)
            agent_id += 1

        # Community Members
        for _ in range(self.n_community_members):
            agent = CommunityMember(agent_id, self)
            agent_id += 1

        # Authorities
        for _ in range(self.n_authorities):
            agent = Authority(agent_id, self)
            agent.monitoring_capacity = self.initial_monitoring_capacity
            agent_id += 1

    def get_agent_by_id(self, agent_id):
        """IDによってエージェントを取得"""
        for agent in self.agents:
            if agent.unique_id == agent_id:
                return agent
        return None

    def count_active_by_role(self, role):
        """特定の役割のアクティブなエージェント数を数える"""
        return sum(1 for agent in self.agents
                   if agent.role == role and agent.active)

    def total_resources(self):
        """全エージェントの資源総量"""
        return sum(agent.resources for agent in self.agents
                   if hasattr(agent, 'resources'))

    def average_detection_exposure(self):
        """平均検出露出度"""
        exposures = [agent.detection_exposure for agent in self.agents
                     if hasattr(agent, 'detection_exposure') and agent.active]
        return np.mean(exposures) if exposures else 0.0

    def intervene_agent(self, agent_id):
        """エージェントに介入（抽象化された逮捕）"""
        agent = self.get_agent_by_id(agent_id)
        if agent and agent.active:
            agent.arrest_count += 1
            self.arrests_this_step += 1

            # 複数回の逮捕でネットワークから除外
            if agent.arrest_count >= 2:
                agent.active = False
                # ネットワークから除去
                if agent.unique_id in self.network:
                    self.network.remove_node(agent.unique_id)

    def report_suspicious_activity(self, target_agent_id):
        """疑わしい活動の通報"""
        self.reports_this_step += 1
        agent = self.get_agent_by_id(target_agent_id)
        if agent:
            # 通報により検出露出度が増加
            agent.detection_exposure = min(1.0, agent.detection_exposure + 0.2)

    def apply_policy_intervention(self, intervention_type, intensity=0.5):
        """
        政策介入を適用
        intervention_type: 'monitoring', 'economic_support', 'community_engagement'
        """
        if intervention_type == 'monitoring':
            # 監視強化
            for agent in self.agents:
                if agent.role == "Authority":
                    agent.monitoring_capacity = min(1.0,
                        agent.monitoring_capacity + intensity * 0.3)

        elif intervention_type == 'economic_support':
            # 経済支援（コミュニティメンバーとOperativeのストレス軽減）
            for agent in self.agents:
                if agent.role in ["Operative", "CommunityMember"]:
                    if hasattr(agent, 'economic_stress'):
                        agent.economic_stress = max(0.0,
                            agent.economic_stress - intensity * 0.3)
                    if hasattr(agent, 'resources'):
                        agent.resources += intensity * 0.2

        elif intervention_type == 'community_engagement':
            # コミュニティ関与強化（通報傾向の向上）
            for agent in self.agents:
                if agent.role == "CommunityMember":
                    agent.reporting_propensity = min(1.0,
                        agent.reporting_propensity + intensity * 0.2)

    def step(self):
        """1タイムステップを実行"""
        # 統計リセット
        self.arrests_this_step = 0
        self.reports_this_step = 0

        # エージェントのステップ実行（ランダムな順序）
        agent_list = list(self.agents)
        random.shuffle(agent_list)
        for agent in agent_list:
            agent.step()

        # 逮捕率の更新
        active_illicit = self.count_active_by_role("Leader") + \
                        self.count_active_by_role("Operative") + \
                        self.count_active_by_role("Broker")
        if active_illicit > 0:
            self.recent_arrest_rate = self.arrests_this_step / active_illicit
        else:
            self.recent_arrest_rate = 0.0

        # データ収集
        self.datacollector.collect(self)

        # 停止条件のチェック（オプション）
        if active_illicit == 0:
            self.running = False
