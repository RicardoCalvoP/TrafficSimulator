"""
Ricardo Calvo Pérez

Starting Date: 12/2024
"""
from mesa import Agent
import heapq
import random


class Car(Agent):
    def __init__(self, unique_id, position, destination, model):
        super().__init__(unique_id, model)

        r = random.randint(150, 255)
        g = random.randint(150, 255)
        b = random.randint(150, 255)

        # Agents propreties
        self.id = unique_id
        self.color = f"rgb({r}, {g}, {b})"
        self.lastPosition = position
        self.position = position
        self.futurePosition = position
        self.destination = destination
        self.direction = "Left"
        self.status = "Driving"
        self.path = []
        self.patience = self.random.randint(5, 14)
        self.waitingTime = 0

    def get_accessible_neighbors(self, current_position):
        """
        Get the neighbors that are accessible based on road direction, traffic light behavior, and not buildings.
        """
        accessible_positions = []
        neighbors = self.model.grid.get_neighborhood(
            current_position, moore=True, include_center=False
        )
        current_direction = self._determine_current_direction(
            current_position)

        if not current_direction:
            return accessible_positions

        for neighbor in neighbors:
            cell_contents = self.model.grid.get_cell_list_contents(
                neighbor)
            for entity in cell_contents:
                if self._is_movement_allowed(entity, neighbor, current_position, current_direction):
                    accessible_positions.append(neighbor)

        return accessible_positions

    def _determine_current_direction(self, current_position):
        """
        Helper to determine the current direction based on the cell's content.
        """
        for entity in self.model.grid.get_cell_list_contents(current_position):
            if isinstance(entity, Road):
                return entity.direction
        return None

    def _is_movement_allowed(self, entity, neighbor, current_position, current_direction):
        """
        Check if movement is allowed based on entity type and road direction.
        """
        if isinstance(entity, Destination) and entity.pos == self.destination:
            return True
        if isinstance(entity, Road):
            return self._validate_direction(entity, neighbor, current_position, current_direction)
        return False

    def _validate_direction(self, entity, neighbor, current_position, current_direction):
        """
        Validate if the direction of movement is correct.
        """
        direction_rules = {
            "Up": lambda: entity.pos[1] >= current_position[1] and entity.direction != "Down",
            "Down": lambda: entity.pos[1] < current_position[1] and entity.direction != "Up",
            "Right": lambda: entity.pos[0] >= current_position[0] and entity.direction != "Left",
            "Left": lambda: entity.pos[0] < current_position[0] and entity.direction != "Right",
        }
        return direction_rules.get(current_direction, lambda: False)()

    def calculate_path(self, start, goal):
        priority_queue = []
        heapq.heappush(priority_queue, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        def calculate_heuristic(point_a, point_b):
            return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])

        while priority_queue:
            current = heapq.heappop(priority_queue)[1]
            if current == goal:
                break
            for next_step in self.get_accessible_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_step not in cost_so_far or new_cost < cost_so_far[next_step]:
                    cost_so_far[next_step] = new_cost
                    priority = new_cost + calculate_heuristic(goal, next_step)
                    heapq.heappush(priority_queue, (priority, next_step))
                    came_from[next_step] = current
        else:
            return []

        return self._reconstruct_path(came_from, start, goal)

    def _reconstruct_path(self, came_from, start, goal):
        current = goal
        reconstructed_path = []
        while current != start:
            if current not in came_from:
                return []
            reconstructed_path.append(current)
            current = came_from[current]
        reconstructed_path.reverse()
        return reconstructed_path

    def proceed(self):
        self.waitingTime = 0
        next_position = self.path.pop(0)
        self.lastPosition = self.position
        self.position = next_position
        self.model.grid.move_agent(self, next_position)

    def step(self):
        if not self.path:
            self.path = self.calculate_path(self.position, self.destination)

        if self.pos == self.destination:
            destination_cords = self.model.grid.get_cell_list_contents(
                [self.destination])
            for agents in destination_cords:
                if isinstance(agents, Destination):
                    agents.carsArrived += 1
            self.model.grid.remove_agent(self)
        if self.path:
            next_position = self.path[0]
            entities_in_next_position = self.model.grid.get_cell_list_contents([
                                                                               next_position])
            for entity in entities_in_next_position:
                if isinstance(entity, Traffic_Light):
                    if not entity.condition:  # Red light
                        self.status = "RedLight"
                        return  # Stop and wait

            entities_in_position = self.model.grid.get_cell_list_contents([
                                                                          next_position])
            if any(isinstance(entity, Car) for entity in entities_in_position):
                if entity.status == "Driving":
                    self.waitingTime += 1
                    if self.waitingTime >= self.patience:
                        self.proceed()
                        self.status = "Driving"
                else:
                    self.status = "RedLight"
                    return
            else:
                # Free cell
                self.status = "Driving"
                self.proceed()


class Traffic_Light(Agent):

    """
    Traffic lights agents will change conditions within time
    from green to red and from red to green
    """

    def __init__(self, unique_id,  condition, timeToChange, model):
        super().__init__(unique_id, model)
        self.condition = condition
        self.timeToChange = timeToChange

    def step(self,):
        """
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.condition = not self.condition


class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """

    def __init__(self, unique_id, direction, model):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass


class Obstacle(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Destination(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carsArrived = 0

    def step(self):
        pass
