"""
Ricardo Calvo Pérez

Starting Date: 12/2024
"""
from agents import Car, Traffic_Light, Road, Obstacle, Destination
from model import City
from mesa.visualization import CanvasGrid, ModularServer, BarChartModule
import random


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1

                 }

    if (isinstance(agent, Car)):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["r"] = 0.69
        portrayal["Layer"] = 2
        portrayal["Color"] = agent.color
    if (isinstance(agent, Road)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.condition else "green"
        portrayal["Layer"] = 1
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
    if (isinstance(agent, Destination)):
        portrayal["Color"] = "pink"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["text"] = agent.carsArrived
        portrayal["text_color"] = "black"

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

cars_arrived_chart = BarChartModule(
    {"Label": "Arrived", "Color": "#00FF00"}
)

grid = CanvasGrid(agent_portrayal, width, height, width*20, height*20)

server = ModularServer(
    City, [grid], "Traffic Base", model_params)

server.port = 8889  # The default
server.launch()
