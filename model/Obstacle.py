

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

    def get_start_x(self):
        return self.start_x

    def get_start_y(self):
        return self.start_y

    def get_end_x(self):
        return self.end_x

    def get_end_y(self):
        return self.end_y

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_obstacle_location(self, timestep):
        if self.start_time <= timestep <= self.end_time:
            x = self.start_x + (timestep - self.start_time) / (self.end_time - self.start_time) * (
                    self.end_x - self.start_x)
            y = self.start_y + (timestep - self.start_time) / (self.end_time - self.start_time) * (
                    self.end_y - self.start_y)
            return x, y
        else:
            return None

    def __repr__(self) -> str:
        return f'radius={self.radius}, start_x = {self.start_x}, start_y = {self.start_y},' \
               f' end_x = {self.end_x}, end_y = {self.end_y}, start_time = {self.start_time},' \
               f' end_time = {self.end_time}, coefficient = {self.coefficient}'


