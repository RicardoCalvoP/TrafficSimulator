"""
Ricardo Calvo Pérez

Starting Date: 12/2024
"""
from model import City, Car, Traffic_Light, Road, Obstacle, Destination
from mesa.visualization import CanvasGrid, ModularServer, BarChartModule

DIRECTIONS = {"Right": "→",
              "Left": "←",
              "Up": "↑",
              "Down": "↓"}


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "Shape": "rect",
        "Filled": True,
        "Layer": 0,
        "w": 1,
        "h": 1,
        "text": "",
        "text_color": "black"
    }

    # Cars
    if isinstance(agent, Car):
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["r"] = 0.69
        portrayal["Color"] = agent.color
        portrayal["Layer"] = 1

    # Traffic Lights
    if isinstance(agent, Traffic_Light):
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["r"] = 0.5
        portrayal["Color"] = "#B81B0E" if not agent.condition else "#549C30"
        portrayal["Layer"] = 1

    # Roads
    if isinstance(agent, Road):
        portrayal["text"] = DIRECTIONS[agent.direction]
        portrayal["text_color"] = "white"
        portrayal["stroke"] = None
        portrayal["Color"] = "#3F3F3F"
        portrayal["Layer"] = 0

    # Obstacles
    if isinstance(agent, Obstacle):
        portrayal["stroke"] = None
        portrayal["Color"] = "#306E68"
        portrayal["Layer"] = 0

    # Destinations
    if isinstance(agent, Destination):
        portrayal["text"] = agent.carsArrived
        portrayal["text_color"] = "black"
        portrayal["stroke"] = None
        portrayal["Color"] = "#5DC1B9"
        portrayal["Layer"] = 0

    return portrayal


cityFile = 'Cities/city1.txt'
with open(cityFile) as baseFile:
    lines = [line.strip() for line in baseFile]  # Remove newline characters
    width = len(lines[0])  # Correct width without '\n'
    height = len(lines)  # Number of lines gives the height

model_params = {
    "width": width,
    "height": height,
    "city": cityFile
}

grid = CanvasGrid(agent_portrayal, width, height, width*20, height*20)


cars_arrived_chart = BarChartModule([{"Label": "Arrived", "Color": "#00FF00"}],
                                    scope="agent", sorting="ascending", sort_by="Arrived")


server = ModularServer(
    City, [grid, cars_arrived_chart], "Traffic Base", model_params)

server.port = 8889  # The default
server.launch()
