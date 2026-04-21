

from mesa import Model
from mesa.space import SingleGrid
from agents import CultureAgent
from mesa.datacollection import DataCollector




from collections import deque


def count_regions(model):
    """
    计算文化区域数量 = 连通分量数量。
    两个相邻格子属于同一 region 当且仅当文化完全相同。
    用 BFS 遍历。
    """
    visited = set()
    regions = 0
    width, height = model.grid.width, model.grid.height

    for x in range(width):
        for y in range(height):
            if (x, y) in visited:
                continue
            # 新 region 起点
            regions += 1
            start_agent = model.grid.get_cell_list_contents([(x, y)])[0]
            target_culture = tuple(start_agent.culture)

            # BFS: 用队列（先进先出）扩展所有"相邻且文化相同"的格子
            queue = deque([(x, y)])
            while queue:
                cx, cy = queue.popleft()  # 从队头弹 → BFS
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))
                # 检查 von Neumann 邻居
                for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if (nx, ny) in visited:
                        continue
                    neighbor_agent = model.grid.get_cell_list_contents([(nx, ny)])[0]
                    if tuple(neighbor_agent.culture) == target_culture:
                        queue.append((nx, ny))
    return regions

def is_stable(model):
    """
    检查系统是否已稳定：所有相邻 agent 对要么完全相同、要么完全不同。
    没有"部分相似"的邻居对 => 没有可能的交互。
    """
    for agent in model.agents:
        neighbors = model.grid.get_neighbors(
            agent.pos, moore=False, include_center=False
        )
        for n in neighbors:
            sim = agent.similarity(n)
            if 0 < sim < 1:
                return False
    return True


class CultureModel(Model):
    """
    Axelrod 1997 文化传播模型。
    """

    def __init__(
        self,
        width=10,
        height=10,
        num_features=5,
        num_traits=10,
        seed=None,
    ):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.num_features = num_features
        self.num_traits = num_traits

        # 非环形 grid（边角 agent 邻居少，符合原文）
        self.grid = SingleGrid(width, height, torus=False)

        # 每个格点放一个 agent
        for x in range(width):
            for y in range(height):
                a = CultureAgent(self, num_features, num_traits)
                self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "Regions": count_regions,
                "Stable": lambda m: int(is_stable(m)),
            }
        )
        self.datacollector.collect(self)

        self.running = True

    def step(self):
        """
        Axelrod 一次 event = 激活一个随机 agent。
        为了让 GUI 可视化更流畅，这里一步运行多个 events。
        """
        events_per_step = self.width * self.height  # 平均每个 agent 被激活一次
        for _ in range(events_per_step):
            agent = self.random.choice(list(self.agents))
            agent.step()

        self.datacollector.collect(self)

        # 稳定后停止
        if is_stable(self):
            self.running = False
