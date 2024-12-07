"""
Ricardo Calvo Pérez

Starting Date: 12/2024
"""

from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa import DataCollector
from agents import Car, Obstacle, Traffic_Light, Road, Destination
import random
import json


class City(Model):
    def __init__(self, width, height, city):
        super().__init__(seed=42)
        self.width = width
        self.height = height
        self.num_steps = 0
        self.num_cars = 1
        self.num_traffic_lights = 1
        self.num_roads = 1
        self.num_obstacles = 1
        self.destinations = []
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.carSpawns = [
            (0, 0),              # Bottom Left
            (width - 1, 0),      # Bottom Right
            (0, height-1),       # Left Top
            (width-1, height-1)  # Top Right
        ]
        self.running = True

        self.datacollector = DataCollector(
            agent_reporters={
                "Arrived": lambda a: a.carsArrived if isinstance(a, Destination) else 0
            }
        )

        dataDictionary = json.load(open('Cities/mapDictionary.json'))

        with open(city) as cityFile:
            lines = cityFile.readlines()

            for r, row in enumerate(lines):
                for c, col in enumerate(row):

                    pos = (c, self.height - r - 1)  # (x,y)

                    # Road
                    if col in ["v", "^", ">", "<"]:
                        road = Road(
                            f"r{self.num_roads}",  # ID
                            dataDictionary[col],   # Direction
                            self                   # Model
                        )
                        # Place road in current position
                        self.grid.place_agent(road, pos)
                        self.num_roads += 1

                    # Traffic Lights
                    elif col in ["S", "s"]:
                        # Find direction
                        if col == "S":
                            above = (pos[0], pos[1] + 1)
                            agents_above = self.grid.get_cell_list_contents([
                                                                            above])
                            direction = self.get_direction(
                                agents_above, ["Up", "Down"], "Up")
                        elif col == "s":
                            left = (pos[0] - 1, pos[1])
                            agents_left = self.grid.get_cell_list_contents([
                                                                           left])
                            direction = self.get_direction(
                                agents_left, ["Left", "Right"], "Left")

                        # Place road in current position
                        road = Road(
                            f"r{self.num_roads}",  # ID
                            direction,             # Determined direction
                            self                   # Model
                        )
                        self.grid.place_agent(road, pos)
                        self.num_roads += 1

                        # Place traffic ligth in current position
                        trafficLight = Traffic_Light(
                            f"tl{self.num_traffic_lights}",  # ID
                            False if col == "S" else True,   # Set conditions of lights
                            int(dataDictionary[col]),        # Set group
                            self                             # Model
                        )

                        self.grid.place_agent(trafficLight, pos)
                        self.num_traffic_lights += 1
                        self.schedule.add(trafficLight)

                    # Building
                    elif col == "#":
                        building = Obstacle(
                            f"b{self.num_obstacles}",       # ID
                            self                            # Model
                        )
                        self.grid.place_agent(building, pos)
                        self.num_obstacles += 1

                    # Destination
                    elif col == "D":
                        destination = Destination(
                            f"d{len(self.destinations)}",    # ID
                            self                             # Model
                        )
                        self.grid.place_agent(destination, pos)
                        self.destinations.append(pos)
                        self.schedule.add(destination)

        for corner in self.carSpawns:
            destination = random.choice(self.destinations)
            car = Car(
                f"c{self.num_cars}",                        # ID
                corner,                                     # Position
                destination,                                # Destination cords
                self                                        # Model
            )
            self.grid.place_agent(car, corner)
            self.schedule.add(car)
            self.num_cars += 1

        self.datacollector.collect(self)

    def get_direction(self, agents, valid_directions, default):
        for agent in agents:
            if isinstance(agent, Road):
                return agent.direction if agent.direction in valid_directions else default
        return default

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.num_steps += 1

        if self.num_steps % 5 == 0:
            free_corners = [corner for corner in self.carSpawns if not any(
                isinstance(agent, Car) for agent in self.grid.get_cell_list_contents(corner))]

            if len(free_corners) == 0:
                self.running = False
                return

            for corner in free_corners:
                destination = random.choice(self.destinations)
                car = Car(
                    f"c{self.num_cars}",                        # ID
                    corner,                                     # Position
                    destination,                                # Destination cords
                    self                                        # Model
                )
                self.grid.place_agent(car, corner)
                self.schedule.add(car)
                self.num_cars += 1
