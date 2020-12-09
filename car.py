import time
import threading
import random
import logging

logging.basicConfig(filename='logger.txt', level=logging.INFO)

class Environment():
    def __init__(self, distance=200, dt=0.01):
        self.cars = []
        self.max_distance = distance
        self.road = [0 for i in range(self.max_distance)]
        self.dt = dt
        # self.cur_id = 0

    def updateEnvironment(self):
        self.road = [0 for i in range(self.max_distance)]
        # del_car = []
        for i in range(len(self.cars)):
            if i >= 1:
                pre_car = self.cars[i-1]
            else:
                pre_car = None
            
            if (len(self.cars) >= 2) & (i == 0):
                pre_car = self.cars[-1]
            location = self.cars[i].update(pre_car, self.dt)
            location = int(location)

            while self.road[location] == 1:
                location -= 1
                if location < 0:
                    location = (self.max_distance - 1)
            self.road[location] = 1

    def refresh(self):
        print('\r',end="", flush=True)
        for i in self.road:
            if i == 0:
                print("_", end="", flush=True)
            elif i == 1:
                print("🚀", end="", flush=True)
        speed = 0
        for i in range(len(self.cars)):
            speed += self.cars[i].current_speed
        print(int(speed/len(self.cars)), end="", flush=True)
            
    def addCar(self, car):
        self.cars.append(car)
        # self.cur_id += 1
    



class Car():
    def __init__(self, id, location=0, max_speed=20, acceleration=5, stop_speed=5, safe_distance=2, p=0, max_distance=100, logger=None):
        self.id = id
        self.safe_distance = safe_distance
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.stop_speed = stop_speed
        self.current_location = location
        self.current_speed = 0
        self.p = p
        self.max_distance = max_distance
        self.logger = logger
    
    def log(self, distance):
        if self.logger != None:
            self.logger.info("id: {}, speed: {}, location: {}, 距离前车距离: {}".format(self.id, self.current_speed, self.current_location, distance))
    
    def changeLocation(self, location):
        if location >= self.max_distance:
            self.current_location = location - self.max_distance
        else:
            self.current_location = location

    """
    changeSpeed will change location
    return final_speed
    """
    def changeSpeed(self, control, dt, pre_car):
        if control == "up":
            speed = min(self.max_speed, self.current_speed+self.acceleration*dt)
        elif control == "down":
            speed = max(0, self.current_speed-self.stop_speed*dt)

        """
        模拟随机刹车
        """
        # if random.random() / 1 <= self.p:
        #     speed = max(0, self.current_location-self.stop_speed*dt)

        distance = self.calDistance(self.current_speed, speed, dt)
        if self.current_location > pre_car.current_location:
            pre_car_location = pre_car.current_location + self.max_distance
        else:
            pre_car_location = pre_car.current_location

        if (self.current_location + distance) >= pre_car_location:
            distance = pre_car_location - 1
            speed = 0
        else:
            distance = self.current_location + distance
        self.changeLocation(distance)
        self.current_speed = speed

    def calDistance(self, begin_speed, end_speed, dt):
        return (begin_speed + end_speed)/2*dt

    def update(self, pre_car, dt):
        if pre_car.current_location < self.current_location:
            distance = self.max_distance - self.current_location + pre_car.current_location
        else:
            distance = pre_car.current_location - self.current_location
        if distance < self.safe_distance:
            self.changeSpeed('down', dt, pre_car)
        else:
            self.changeSpeed('up', dt, pre_car)
        self.log(distance)
        return self.current_location

class ACar(Car):
    def __init__(self, id, location, logger):
        super().__init__(id, location=location, logger=logger)
    def update(self, pre_car, dt):
        return self.current_location

def main():
    road_distance = 100
    env = Environment(distance=road_distance)
    for i in range(20):
        env.addCar(Car(i, 60-i,max_distance=road_distance))

    while True:
        env.updateEnvironment()
        env.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    main()