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
    x = 0
    i = 1
    if speed_random:
        while x < road_len:
            if np.random.rand() <= P_init:
                # choose random speed uniformly in {0,6} range
                cars[i] = random_speed()
                road[x] = i
                x += 2
                i += 1
            else:
                x += 1
    else:
        while x < road_len:
            if np.random.rand() <= P_init:
                # if not random, start all cars at Vmax
                cars[i] = Vmax
                road[x] = i
                x += 2
                i += 1
            else:
                x += 1
    return cars, road


# get the indexes of all cars on the road array
def car_positions(road):
    return np.nonzero(road)[0]


# the speed is a function of the gap size
# simplest model: accelerate to speed = gap_size
def speed_update_one_car(car_pi, car_positions, cars, road, Vmax=6):
    i = road[car_positions[car_pi]]
    distance = car_positions[car_pi+1] - car_positions[car_pi] - 2
    if distance >= Vmax:
        cars[i] = Vmax
    else:
        cars[i] = distance
    return cars


def speed_update(car_positions, cars, road, Vmax=6):
    l = len(car_positions)
    for cp in range(l-1):
        cars = speed_update_one_car(cp, car_positions, cars, road, Vmax)
    cars[l]=Vmax
    return cars


# update position of a single car given:
# 1) it's index into the car positions array
# 2) the car positions array, array of indexes that say's where each car is on
#     the road the array is ordered such that consecutive elements correspond
#     with consecutive cars. F.e. element 0 can correspond with car 1,
#     element 1 with car 2 and so on.
# 3) the cars dictionairy
# 4) road array
def position_update_one_car(car_pi, car_posses, cars, road):
    car_pos = car_posses[car_pi]
    i = road[car_pos]
    speed = cars[i]
    # if speed is zero, car doesn't move
    if speed == 0:
        return cars, road
    neighbors = car_positions(road[car_pos : car_pos + speed + 2])  
    # consider edge case when the updating the last car in the array,
    # it can dissapear off the edge when position+speed > len(array)
    if car_pi == len(car_posses)-1:
        # delete car if it disappears of the road
        if car_pos + speed > road.size - 1:
            road[car_pos] = 0
            del cars[i]
            # only return the updated car dict if a car is deleted
            return cars, road
        # otherwise, the car can get up to the exact last block
        else:
            road[car_pos + speed] = road[car_pos]
            road[car_pos] = 0
            return cars, road
    # if not last car, update the position as normal
    # if there is only one neighbor (i.e. itself), the road
    # is clear to move at it's current speed
    if neighbors.size == 1:
        road[car_pos + speed] = road[car_pos]
        road[car_pos] = 0
        return cars, road
    # otherwise, move as close to the closest leader car
    # as possible and adjust speed to this leader
    else:
        # dnn is relative distance to the first leader
        dnn = neighbors[1]
        # if the relative distance is exactly 2, it means the
        # car is already driving as close as it wants to,
        # and it can't move closer
        if dnn == 2:
            return cars, road
        # otherwise, the speed would result in a movement that
        # is larger than the gap between itself and it's nearest
        # leader
        else:
            # minimum gap is defined as it's distance to the nearest leader
            # minus two, since there should always be one block between cars =
            # distance of 2
            min_gap = dnn-2
            # if the speed is larger than this gap, is should simpy move
            # as close as possible, i.e. this exact gap size, so it's
            # new position is within one block of it's nearest leader
            if speed > min_gap:
                road[car_pos + min_gap] = road[car_pos]
                road[car_pos] = 0
            # otherwise, there is a large enough gap given the current speed
            # to move and it simply updates the position using this speed
            else:
                road[car_pos + speed] = road[car_pos]
                road[car_pos] = 0
        return cars, road


# update position of all cars
def position_update(car_posses, cars, road):
    for i in range(len(car_posses)):
        cars, road = position_update_one_car(i, car_posses, cars, road)
    return cars, road


# Generate a new car randomly if the
# first position of the road is free.
# always returns the car and road array
def generate_new_cars(cars, road, p_gen=1, speed_random=False, Vmax=6):
    if not road[0:2].any() and np.random.rand() <= p_gen:
        # give the new key a new label
        new_car = max(cars.keys())+1
        road[0] = new_car
        # print('new car ', new_car)
        # if speed randomization is false, set speed to Vmax
        if not speed_random:
            cars[new_car] = Vmax
        else:
            # choose random speed uniformly
            cars[new_car] = random_speed()
    return cars, road



def main_loop(P_init, iterations=10, road_len=int(1e4), 
              Vmax=6, Vrandom=True, p_gen=0.3,
              reaction_time=1):
    
    # make the initial road and cars
    cars, road = random_init_cars(road_len, P_init,
                                  Vrandom,
                                  Vmax)
    # make initial car positions
    positions = car_positions(road)
    
    # run the main experiment loop
    if reaction_time!=0:
        for i in range(iterations):
            # update the position using current speed
            cars, road = position_update(positions, cars, road)

            # generate randomly new cars at the beginning of the road
            #cars, road = generate_new_cars(cars, road, p_gen=0.5, speed_random=False, Vmax=6)

            # get the new car positions from the new array
            positions = car_positions(road)

            # Update the speed based on the new position when i is equal to 
            # an exact multiple of the reaction time, this has the effect of 
            # delaying each speed update with 1 reaction time.

            if i%reaction_time==0:
                cars = speed_update(positions, cars, road, Vmax)
            
    # if reaction time is zero, do the basic loop without reaction time
    # (slight code redundancy, but avoids unnecessary checks inside the loop)
    if reaction_time==0:
        for i in range(iterations):
            cars,road=position_update(positions, cars, road)
            positions=car_positions(road)
            cars=speed_update(positions, cars, road, Vmax)

    return cars, road    
