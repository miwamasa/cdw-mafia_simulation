"""
Abstract Illicit Ecology Model (AIEM) - Agent Classes
学術研究・政策評価用の抽象化されたエージェントモデル
"""

from mesa import Agent
import numpy as np


class AbstractAgent(Agent):
    """
    すべてのエージェントの基底クラス
    共通の抽象属性を持つ
    """

    def __init__(self, unique_id, model, role):
        super().__init__(model)
        self.unique_id = unique_id
        self.role = role

        # 共通抽象属性（仕様書セクション5より）
        self.resources = self.random.uniform(0.1, 1.0)
        self.legitimacy = self.random.uniform(0.0, 1.0)
        self.risk_tolerance = self.random.uniform(0.0, 1.0)
        self.social_capital = self.random.uniform(0.0, 1.0)
        self.detection_exposure = self.random.uniform(0.0, 1.0)

        # specialty_vector: 抽象的な活動タイプの傾向（3次元ベクトル）
        self.specialty_vector = np.random.dirichlet(np.ones(3))

        self.active = True
        self.arrest_count = 0

    def update_social_capital(self):
        """ネットワーク位置に基づいて社会資本を更新"""
        neighbors = list(self.model.network.neighbors(self.unique_id))
        if len(neighbors) > 0:
            # 近隣ノードの平均legitimacyに基づいて調整
            neighbor_legitimacies = []
            for n in neighbors:
                agent = self.model.get_agent_by_id(n)
                if agent and hasattr(agent, 'legitimacy'):
                    neighbor_legitimacies.append(agent.legitimacy)
            if neighbor_legitimacies:
                avg_neighbor_legitimacy = np.mean(neighbor_legitimacies)
                self.social_capital = 0.7 * self.social_capital + 0.3 * avg_neighbor_legitimacy

    def adjust_risk_from_environment(self):
        """環境要因（逮捕率など）に基づいてリスク許容度を調整"""
        if self.model.recent_arrest_rate > 0.1:
            # 逮捕率が高い場合、リスク許容度を下げる（学習）
            self.risk_tolerance *= 0.95

    def step(self):
        """各ステップでの行動（サブクラスでオーバーライド）"""
        if not self.active:
            return
        self.update_social_capital()
        self.adjust_risk_from_environment()


class Leader(AbstractAgent):
    """
    組織的統制要素
    戦略決定に関与（抽象的な意思決定のみ）
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, role="Leader")
        # Leaderは比較的高い資源と社会資本を持つ
        self.resources = self.random.uniform(0.5, 1.0)
        self.social_capital = self.random.uniform(0.4, 1.0)
        self.detection_exposure = self.random.uniform(0.1, 0.5)  # 比較的低い露出

    def step(self):
        super().step()
        if not self.active:
            return

        # 抽象的な資源配分決定
        self.distribute_resources()

    def distribute_resources(self):
        """配下のOperativeに資源を配分（抽象化）"""
        neighbors = list(self.model.network.neighbors(self.unique_id))
        if len(neighbors) > 0 and self.resources > 0.3:
            # 資源を近隣に分配
            distribution_amount = self.resources * 0.1
            for neighbor_id in neighbors:
                agent = self.model.get_agent_by_id(neighbor_id)
                if agent and isinstance(agent, (Operative, Broker)):
                    transfer = distribution_amount / len(neighbors)
                    agent.resources += transfer
                    self.resources -= transfer


class Operative(AbstractAgent):
    """
    実行者
    個人行動の主体、社会経済状態・リスク志向などの属性を持つ
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, role="Operative")
        self.economic_stress = self.random.uniform(0.0, 1.0)

    def step(self):
        super().step()
        if not self.active:
            return

        # 経済的ストレスがリスク許容度に影響
        if self.economic_stress > 0.7:
            self.risk_tolerance = min(1.0, self.risk_tolerance + 0.05)

        # 抽象的な活動（具体的な違法行為は含まない）
        self.perform_abstract_activity()

    def perform_abstract_activity(self):
        """抽象化された活動を実行"""
        if self.risk_tolerance > 0.5 and self.resources < 0.3:
            # 資源が少なく、リスク許容度が高い場合、活動を行う
            activity_success_prob = self.social_capital * (1 - self.detection_exposure)
            if self.random.random() < activity_success_prob:
                self.resources += 0.1
            else:
                # 検出リスク
                self.detection_exposure = min(1.0, self.detection_exposure + 0.1)


class Broker(AbstractAgent):
    """
    仲介者
    異なるサブネット間の接続を媒介
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, role="Broker")
        # Brokerは高い社会資本を持つ
        self.social_capital = self.random.uniform(0.5, 1.0)

    def step(self):
        super().step()
        if not self.active:
            return

        # 仲介による利益（抽象化）
        self.mediate_connections()

    def mediate_connections(self):
        """接続を仲介し、資源を得る"""
        neighbors = list(self.model.network.neighbors(self.unique_id))
        if len(neighbors) >= 2:
            # ネットワーク位置の価値から利益を得る
            mediation_value = len(neighbors) * 0.02
            self.resources += mediation_value


class Facilitator(AbstractAgent):
    """
    フロント／合法的接点
    合法経済との接点（抽象化）
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, role="Facilitator")
        # Facilitatorは高いlegitimacyを持つ
        self.legitimacy = self.random.uniform(0.5, 1.0)
        self.detection_exposure = self.random.uniform(0.0, 0.3)  # 低い露出

    def step(self):
        super().step()
        if not self.active:
            return

        # 合法的な外観を維持
        self.maintain_legitimacy()

    def maintain_legitimacy(self):
        """合法性を維持・向上させる"""
        if self.resources > 0.2:
            # 資源を使って合法性を高める
            self.resources -= 0.05
            self.legitimacy = min(1.0, self.legitimacy + 0.05)
            self.detection_exposure = max(0.0, self.detection_exposure - 0.05)


class CommunityMember(AbstractAgent):
    """
    一般市民
    環境要因、被害感受性、通報可能性などを持つ
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, role="CommunityMember")
        # 一般市民は通常高いlegitimacyを持つ
        self.legitimacy = self.random.uniform(0.7, 1.0)
        self.vulnerability = self.random.uniform(0.0, 1.0)
        self.reporting_propensity = self.random.uniform(0.0, 1.0)

    def step(self):
        super().step()
        if not self.active:
            return

        # 通報行動（抽象化）
        self.consider_reporting()

    def consider_reporting(self):
        """異常な活動を検出して通報する可能性を評価"""
        neighbors = list(self.model.network.neighbors(self.unique_id))
        for neighbor_id in neighbors:
            agent = self.model.get_agent_by_id(neighbor_id)
            if agent and agent.detection_exposure > 0.7:
                # 高い露出度の近隣がいる場合、通報を検討
                if self.random.random() < self.reporting_propensity * 0.1:
                    self.model.report_suspicious_activity(neighbor_id)


class Authority(AbstractAgent):
    """
    法執行・規制機関
    監視強度、捜査資源、政策介入能力を持つ
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, role="Authority")
        self.monitoring_capacity = 0.5
        self.intervention_resources = 1.0

    def step(self):
        super().step()

        # 監視と介入
        self.monitor_and_intervene()

    def monitor_and_intervene(self):
        """監視を行い、必要に応じて介入"""
        # 全エージェントを監視
        for agent in self.model.agents:
            if agent.role in ["Leader", "Operative", "Broker"] and agent.active:
                # 検出確率は露出度と監視能力に依存
                detection_prob = agent.detection_exposure * self.monitoring_capacity * 0.05

                if self.random.random() < detection_prob:
                    # 検出・介入（抽象化された「逮捕」）
                    self.model.intervene_agent(agent.unique_id)
                    self.intervention_resources -= 0.1

        # 資源の回復
        self.intervention_resources = min(1.0, self.intervention_resources + 0.05)
