import solara
import colorsys
from mesa.visualization import SolaraViz, make_space_component, make_plot_component

from model import CultureModel


def agent_portrayal(agent):
    """
    give each agent a color based on their culture (a tuple of traits) and a square marker
    """
    culture_tuple = tuple(agent.culture)
    # Make a hash of the culture tuple and map it to a hue value in [0, 1]
    h = (hash(culture_tuple) % 360) / 360
    # Convert HSV to RGB, with fixed saturation and value for bright colors
    r, g, b = colorsys.hsv_to_rgb(h, 0.7, 0.9)
    color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    return {
        "color": color,
        "marker": "s",  
        "size": 200,
    }

# define model parameters with types and default values for the SolaraViz interface 
# moore is a boolean parameter that controls the neighborhood type (von Neumann or Moore)
model_params = {
    "width": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid width",
        "min": 5,
        "max": 20,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid height",
        "min": 5,
        "max": 20,
        "step": 1,
    },
    "num_features": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of features (F)",
        "min": 2,
        "max": 15,
        "step": 1,
    },
    "num_traits": {
        "type": "SliderInt",
        "value": 10,
        "label": "Traits per feature (q)",
        "min": 2,
        "max": 15,
        "step": 1,
    },
    "neighborhood_type": {
        "type": "Select",
        "value": "von_neumann_4",
        "values": ["von_neumann_4", "moore_8", "extended_12"],
        "label": "Neighborhood range",
    },
    "seed": {
        "type": "InputText",
        "value": "42",
        "label": "Random seed",
    },
}


@solara.component
@solara.component
def ParameterDisplay(model):
    # Display model parameters to help user understand current state of the simulation
    neighborhood_labels = {
        "von_neumann_4": "von Neumann (4)",
        "moore_8": "Moore (8)",
        "extended_12": "Extended range (12)",
    }
    neighborhood_name = neighborhood_labels[model.neighborhood_type]
    stable_status = "Yes" if not model.running else "No"

    solara.Markdown(
        f"""
        ### Model Parameters
        
        - **Grid size:** {model.width} × {model.height} ({model.width * model.height} sites)
        - **Features (F):** {model.num_features}
        - **Traits per feature (q):** {model.num_traits}
        - **Neighborhood:** {neighborhood_name}
        - **Torus:** {model.grid.torus}
        - **Stable:** {stable_status}

        Each square represents one site/agent. Colors represent the agent's complete cultural vector, so identical colors indicate identical cultures.

        Note: Axelrod's original Figure 1 visualizes cultural similarity across boundaries between neighboring sites. This GUI instead visualizes cultural regions directly, while the mean-similarity plot captures convergence over time.
        """
    )



model = CultureModel()

SpaceComponent = make_space_component(agent_portrayal)
RegionsPlot = make_plot_component("Regions")
SimilarityPlot = make_plot_component("Mean Similarity")

page = SolaraViz(
    model,
    components=[SpaceComponent, RegionsPlot, SimilarityPlot, ParameterDisplay],
    model_params=model_params,
    name="Axelrod (1997) — Dissemination of Culture",
)
page