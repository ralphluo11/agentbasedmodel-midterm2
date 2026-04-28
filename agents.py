from mesa import Agent

class CultureAgent(Agent):
    """
    A "village" in the Axelrod (1997) cultural dissemination model.
    Each agent is fixed at a position on the grid and has a cultural
    vector of num_features traits, with each trait taking a value from
    0 to num_traits - 1.
    """

    def __init__(self, model, num_features, num_traits):
        super().__init__(model)
        self.num_features = num_features
        self.num_traits = num_traits
        # Each feature is sampled independently and uniformly from [0, num_traits-1].
        # Trait values are nominal labels (not ordered) — "3" and "7" are just two 
        # different categories, not "closer" or "farther" than "3" and "4".
        self.culture = [
            self.random.randrange(num_traits) for _ in range(num_features)
        ]

    def similarity(self, other):
        # Cultural similarity = fraction of features with matching traits.
        # Because traits are nominal (unordered), each feature contributes a binary
        # match (equal or not) — no partial similarity within a feature.
        matches = sum(
            1 for a, b in zip(self.culture, other.culture) if a == b
        )
        return matches / self.num_features

    def step(self):
        """
        The interaction rules of Axelrod (1997):
        Randomly pick a neighbor, calculate cultural similarity, and with that probability interact:
        if interact, randomly pick one of the features where they differ and copy that trait from the neighbor.
        """
        # Get neighbors according to the selected neighborhood_type, excluding self..
        # Edge/corner agents have fewer neighbors (torus=False).
        neighbors = self.model.get_cultural_neighbors(self.pos)
        if not neighbors:
            return

        neighbor = self.random.choice(neighbors)
        sim = self.similarity(neighbor)

        # With probability equal to similarity, interact and become more similar
        if self.random.random() < sim:
            # Find the features where they differ
            diff_features = [
                i for i in range(self.num_features)
                if self.culture[i] != neighbor.culture[i]
            ]
            # if is indentical, then no interaction happens
            if diff_features:
                f = self.random.choice(diff_features)
                self.culture[f] = neighbor.culture[f]