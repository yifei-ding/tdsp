

class Obstacle(object):
    def __init__(self, radius, start_x, start_y, end_x, end_y, start_time, end_time, coefficient):
        self.radius = radius
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.start_time = start_time
        self.end_time = end_time
        self.coefficient = coefficient  # time dependent weight = weight * coefficient

    def get_coefficient(self):
        return self.coefficient

    def get_radius(self):
        return self.radius

    def get_obstacle_location(self, timestep):
        if self.start_time <= timestep < self.end_time:
            x = self.start_x + (timestep - self.start_time) / (self.end_time - self.start_time) * (
                    self.end_x - self.start_x)
            y = self.start_y + (timestep - self.start_time) / (self.end_time - self.start_time) * (
                    self.end_y - self.start_y)
            return x, y
        elif timestep >= self.end_time:
            return self.end_x, self.end_y
        else:
            return None

    def __repr__(self) -> str:
        return f'radius={self.radius}, start_x = {self.start_x}, start_y = {self.start_y},' \
               f' end_x = {self.end_x}, end_y = {self.end_y}, start_time = {self.start_time},' \
               f' end_time = {self.end_time}, coefficient = {self.coefficient}'


