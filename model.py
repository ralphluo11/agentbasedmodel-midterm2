from mesa import Model
from mesa.space import SingleGrid
from agents import CultureAgent
from mesa.datacollection import DataCollector

from collections import deque



def count_regions(model):
    visited = set()
    regions = 0
    width, height = model.grid.width, model.grid.height
    
    # change directions based on neighborhood type (von Neumann or Moore)
    if model.neighborhood_type == "von_neumann_4":
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    elif model.neighborhood_type == "moore_8":
        directions = [
            (dx, dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if (dx, dy) != (0, 0)
        ]

    elif model.neighborhood_type == "extended_12":
        directions = [
            (dx, dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if (dx, dy) != (0, 0)
        ]
        directions += [(2, 0), (-2, 0), (0, 2), (0, -2)]

    else:
        raise ValueError(f"Unknown neighborhood_type: {model.neighborhood_type}")
    # use BFS to find connected components of agents with the same culture
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
    Check if the system is stable: all neighboring agent pairs are either
    identical or completely different.
    """
    for agent in model.agents:
        neighbors = model.get_cultural_neighbors(agent.pos)
        for n in neighbors:
            sim = agent.similarity(n)
            if 0 < sim < 1:
                return False
    return True

def mean_neighbor_similarity(model):
    """Average cultural similarity across neighboring pairs."""
    seen_pairs = set()
    sims = []

    for agent in model.agents:
        neighbors = model.get_cultural_neighbors(agent.pos)
        for n in neighbors:
            pair = tuple(sorted([agent.unique_id, n.unique_id]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            sims.append(agent.similarity(n))

    return sum(sims) / len(sims) if sims else 0

class CultureModel(Model):
    """
    Agents are fixed on a grid; each has a cultural vector of traits.
    Interaction probability between neighbors equals their cultural
    similarity, and interaction copies one differing trait from
    neighbor to active agent. System is stable when all adjacent
    pairs are either identical or completely different.
    """

    def __init__(
        self,
        width=10,
        height=10,
        num_features=5,
        num_traits=10,
        neighborhood_type="von_neumann_4",
        seed=None,
    ):
        # Convert string seed from UI input to int (or None if empty)
        if isinstance(seed, str):
            seed = int(seed) if seed.strip() else None
        
        super().__init__(seed=seed)  

        self.width = width
        self.height = height
        self.num_features = num_features
        self.num_traits = num_traits
        self.neighborhood_type = neighborhood_type

        # make a non-toroidal grid (agents on edges have fewer neighbors, which can affect dynamics and stability)
        self.grid = SingleGrid(width, height, torus=False)

        # place one agent per cell
        for x in range(width):
            for y in range(height):
                a = CultureAgent(self, num_features, num_traits)
                self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "Regions": count_regions,
                "Stable": lambda m: int(is_stable(m)),
                "Mean Similarity": mean_neighbor_similarity,
            }
        )
        self.running = True
        self.datacollector.collect(self)

        
    
    def get_cultural_neighbors(self, pos):

        """

        Return neighbors according to Axelrod-style interaction ranges.

        """

        x, y = pos

        if self.neighborhood_type == "von_neumann_4":

            offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        elif self.neighborhood_type == "moore_8":

            offsets = [

                (dx, dy)

                for dx in [-1, 0, 1]

                for dy in [-1, 0, 1]

                if (dx, dy) != (0, 0)

            ]

        elif self.neighborhood_type == "extended_12":

            offsets = [

                (dx, dy)

                for dx in [-1, 0, 1]

                for dy in [-1, 0, 1]

                if (dx, dy) != (0, 0)

            ]

            offsets += [(2, 0), (-2, 0), (0, 2), (0, -2)]

        else:

            raise ValueError(f"Unknown neighborhood_type: {self.neighborhood_type}")

        neighbors = []

        for dx, dy in offsets:

            nx, ny = x + dx, y + dy

            if 0 <= nx < self.width and 0 <= ny < self.height:

                cell_contents = self.grid.get_cell_list_contents([(nx, ny)])

                if cell_contents:

                    neighbors.extend(cell_contents)

        return neighbors
        
    def step(self):
        if not self.running:
            return  # already stable, skip
# Axelrod's original time unit is one random interaction event.
# For GUI readability, one Mesa step is treated as one approximate sweep:
# width * height random events, still sampled asynchronously with replacement.
        events_per_step = self.width * self.height
        for _ in range(events_per_step):
            agent = self.random.choice(list(self.agents))
            agent.step()

        self.datacollector.collect(self)

        if is_stable(self):
            self.running = False
