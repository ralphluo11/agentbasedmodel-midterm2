import solara
import colorsys
from mesa.visualization import SolaraViz, make_space_component, make_plot_component

from model import CultureModel


def agent_portrayal(agent):
    """
    把 agent 的文化向量映射成颜色。
    简单做法：把文化元组 hash 成一个颜色，这样相同文化=相同颜色。
    """
    culture_tuple = tuple(agent.culture)
    # 把文化映射成 0-1 之间的 hue
    h = (hash(culture_tuple) % 360) / 360
    # HSL 转 RGB（简单起见用 matplotlib 风格 hex）
    r, g, b = colorsys.hsv_to_rgb(h, 0.7, 0.9)
    color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    return {
        "color": color,
        "marker": "s",  # 方块
        "size": 200,
    }


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
    """显示当前模型参数和运行状态"""
    # 触发重新渲染
    model.steps  # 访问这个属性让 Solara 知道要更新
    neighborhood_name = "Moore (8)" if model.moore else "von Neumann (4)"
    
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