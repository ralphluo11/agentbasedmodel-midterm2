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
    "moore": {
    "type": "Select",
    "value": False,
    "values": [False, True],
    "label": "Neighborhood (False=von Neumann/4, True=Moore/8)",
    },
    "seed": {
        "type": "InputText",
        "value": "42",
        "label": "Random seed",
    },
}


@solara.component
def ParameterDisplay(model):
    # Access model.steps to trigger re-rendering when the model advances
    model.steps  
    neighborhood_name = "Moore (8)" if model.moore else "von Neumann (4)"
    # Display model parameters to help user understand current state of the simulation
    solara.Markdown(
        f"""
        ### Model Parameters
        
        - **Grid size:** {model.width} × {model.height} ({model.width * model.height} sites)
        - **Features (F):** {model.num_features}
        - **Traits per feature (q):** {model.num_traits}
        - **Neighborhood:** {neighborhood_name}
        - **Torus:** {model.grid.torus}
        
        ### Status
        
        - **Step:** {model.steps}
        - **Events per step:** {model.width * model.height}
        - **Total events:** {model.steps * model.width * model.height:,}
        - **Regions:** {model.datacollector.model_vars['Regions'][-1] if model.datacollector.model_vars['Regions'] else 'N/A'}
        - **Stable:** {'✓ Yes' if not model.running else '✗ No (still evolving)'}
        """
    )



model = CultureModel()

SpaceComponent = make_space_component(agent_portrayal)
RegionsPlot = make_plot_component("Regions")

page = SolaraViz(
    model,
    components=[SpaceComponent, RegionsPlot, ParameterDisplay],
    model_params=model_params,
    name="Axelrod (1997) — Dissemination of Culture",
)
page