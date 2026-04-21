from mesa import Agent

class CultureAgent(Agent):
    """
    Axelrod (1997) 文化传播模型中的一个"村庄"。
    每个 agent 固定在 grid 上一个位置，有一个由 num_features 个
    traits 组成的文化向量，每个 trait 取值 0 到 num_traits-1。
    """

    def __init__(self, model, num_features, num_traits):
        super().__init__(model)
        self.num_features = num_features
        self.num_traits = num_traits
        # 随机初始化文化：例如 [8, 7, 2, 5, 4]
        self.culture = [
            self.random.randrange(num_traits) for _ in range(num_features)
        ]

    def similarity(self, other):
        """共享 feature 的比例，范围 [0, 1]"""
        matches = sum(
            1 for a, b in zip(self.culture, other.culture) if a == b
        )
        return matches / self.num_features

    def step(self):
        """
        Axelrod 的交互规则：
        1. 随机挑一个邻居
        2. 以 cultural similarity 为概率决定是否交互
        3. 若交互，随机挑一个两者不同的 feature，把邻居的 trait 复制过来
        """
        # von Neumann 邻域（上下左右 4 个），边角 agent 邻居少于 4 个
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=False, include_center=False
        )
        if not neighbors:
            return

        neighbor = self.random.choice(neighbors)
        sim = self.similarity(neighbor)

        # 以相似度为概率交互
        if self.random.random() < sim:
            # 找出两者不同的 feature 索引
            diff_features = [
                i for i in range(self.num_features)
                if self.culture[i] != neighbor.culture[i]
            ]
            # 如果完全相同就什么都不做（sim=1 时 diff 为空）
            if diff_features:
                f = self.random.choice(diff_features)
                self.culture[f] = neighbor.culture[f]