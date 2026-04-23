

from mesa import Model
from mesa.space import SingleGrid
from agents import CultureAgent
from mesa.datacollection import DataCollector




from collections import deque


def count_regions(model):
    visited = set()
    regions = 0
    width, height = model.grid.width, model.grid.height
    
    # 根据 moore 选择邻居方向
    if model.moore:
        directions = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]
    else:
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    for x in range(width):
        for y in range(height):
            if (x, y) in visited:
                continue
            regions += 1
            start_agent = model.grid.get_cell_list_contents([(x, y)])[0]
            target_culture = tuple(start_agent.culture)
            
            queue = deque([(x, y)])
            while queue:
                cx, cy = queue.popleft()
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))
                for dx, dy in directions:
                    nx, ny = cx + dx, cy + dy
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
            agent.pos, moore=model.moore, include_center=False
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
        moore=False,
        seed=None,
    ):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.num_features = num_features
        self.num_traits = num_traits
        self.moore = moore

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
        events_per_step = self.width * self.height
        for _ in range(events_per_step):
            agent = self.random.choice(list(self.agents))
            agent.step()

        self.datacollector.collect(self)

        if is_stable(self):
            self.running = False
