import numpy as np
import random
from collections import defaultdict


# return a random speed between 0 and 6 blocks per time step
def random_speed():
    return random.choice([0, 1, 2, 3, 4, 5, 6])


# populate the road with P_init density random cars
def random_init_cars(road_len, P_init, speed_random=False, Vmax=6):
    cars = defaultdict(int)
    # zero indicates there is no car or a non-rear part of a car
    # is present
    road = np.array([0]*road_len)
    x = 0; i = 1
    if speed_random:
        while x < road_len:
            if np.random.rand() <= P_init:
                # choose random speed uniformly in {0,6} range
                cars[i] = random_speed()
                road[x] = i
                x += 2; i += 1
            else:
                x += 1
    else:
        while x < road_len:
            if np.random.rand() <= P_init:
                # if not random, start all cars at Vmax
                cars[i] = Vmax
                road[x] = i
                x += 2; i += 1
            else:
                x += 1
    return cars, road


# get the indexes of all cars on the road array
def car_positions(road):
    return np.nonzero(road)[0]
