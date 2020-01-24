import numpy as np
import random
import matplotlib.pyplot as plt
import config
from collections import defaultdict

# return a random speed between 0 and 6 blocks per time step
# used for initializing cars with random speeds
def random_speed(Vmax=6):
    return random.choice(range(Vmax))

# subroutine for the speed_randomizer function
# this is not necessary, but to reduce numer of code lines
# udpates the speed for one car
def speed_randomizer_sub(cars, c, p, amount, alt_speed=False):
    # if alternative speed is off, use the config.Vmax1 to update car speed
    if alt_speed==False:
        if np.random.rand()<=0.5:
            cars[c] += amount
        else: 
            cars[c] -= amount
        # check if the speed doesn't go above or below the boundaries of Vmax and 0, 
        # if it does, set it to Vmax or 0 
        if cars[c] > config.Vmax1:
            cars[c] = config.Vmax1
        if cars[c] < 0:
            cars[c] = 0
        return cars
    else:
        # if alternative speed is selected, use the config.Vmax2 speed instead
        if np.random.rand()<=0.5:
            cars[c] += amount
        else: 
            cars[c] -= amount
        # check if the speed doesn't go above or below the boundaries of Vmax and 0, 
         # if it does, set it to Vmax or 0 
        if cars[c] > config.Vmax2:
            cars[c] = config.Vmax2
        if cars[c] < 0:
            cars[c] = 0
        return cars
        

# function that adds noise to car velocity,
# it can randomly change slightly modeling the idea of
# driver cruise inconsistency
#   cars = dict of car_label : speed, 
#   p = probability the speed will change each main_loop iteration
#   amount = amount that the speed changes
def speed_randomizer(cars, p=0.1, amount=1):
    # check for the varying Vmax setting
    if config.Vm_vary!=0:
        for c in cars:
            # check for the slower Vmax
            if c % config.Vm_vary == 0:
                speed_randomizer_sub(cars, c, p, amount, alt_speed=True)
            # otherwise, continue routine as normal             
            else:
                cars = speed_randomizer_sub(cars, c, p, amount, alt_speed=False) 
    # if Vm_vary is not used, simply update using the standard Vmax1
    else:
        for c in cars:
            cars = speed_randomizer_sub(cars, c, p, amount, alt_speed=False)
    return cars                  
                




# populate the road with P_init density random cars
def random_init_cars(road_len, P_init, speed_random=False):
    config.flow_counter = 0
    cars = defaultdict(int)
    # zero indicates there is no car or a non-rear part of a car
    # is present
    road = np.array([0]*road_len)
    x = 0
    i = 1
    # as always, check the use of Vm_vary for the two different Vmax scenario
    if config.Vm_vary != 0:
        if speed_random:
            while x < road_len:
                if np.random.rand() <= P_init:
                    # choose random speed uniformly in {0,6} range
                    if i % config.Vm_vary == 0:
                        # slower Vmax
                        cars[i] = random_speed(config.Vmax2)
                    else: 
                        # higher Vmax
                        cars[i] = random_speed(config.Vmax1)
                    road[x] = i
                    x += 2
                    i += 1
                else:
                    x += 1
        else:
            while x < road_len:
                if np.random.rand() <= P_init:
                    # if not random, start all cars at Vmax
                    if i%config.Vm_vary==0:
                        cars[i] = config.Vmax2
                    else:
                        cars[i] = config.Vmax1
                    road[x] = i
                    x += 2
                    i += 1
                else:
                    x += 1
    # if not, apply the function with only Vmax1
    else:
        if speed_random:
            while x < road_len:
                if np.random.rand() <= P_init:
                    # choose random speed uniformly in {0,6} range
                    cars[i] = speed_random(config.Vmax1)
                    road[x] = i
                    x += 2
                    i += 1
                else:
                    x += 1
        else:
            while x < road_len:
                if np.random.rand() <= P_init:
                    # if not random, start all cars at Vmax
                    cars[i] = config.Vmax1
                    road[x] = i
                    x += 2
                    i += 1
                else:
                    x += 1

    # initial amount of cars
    config.car_counter = len(cars)
    return cars, road


# get the indexes of all cars on the road array
def car_positions(road):
    return np.nonzero(road)[0]


# the speed is a function of the gap size
# simplest model: accelerate to speed = gap_size
def speed_update_one_car(car_pos_index, car_pos, cars, road):
    i = road[car_pos[car_pos_index]]
    if config.Vm_vary != 0 and i % config.Vm_vary == 0:
        Vmax = config.Vmax2
    else:
        Vmax = config.Vmax1
    distance = car_pos[car_pos_index+1] - car_pos[car_pos_index] - 2
    if distance >= Vmax:
        cars[i] = Vmax
    else:
        cars[i] = distance
    return cars


def speed_update(car_pos, cars, road):
    l = len(car_pos)
    for pos in range(l-1):
        cars = speed_update_one_car(pos, car_pos, cars, road)
    if config.Vm_vary != 0 and i % config.Vm_vary == 0:
        Vmax = config.Vmax2
    else:
        Vmax = config.Vmax1
    cars[road[car_pos[l-1]]] = Vmax
    return cars


# update position of a single car given:
# 1) it's index into the car positions array
# 2) the car positions array, array of indexes that say's where each car is on
#     the road the array is ordered such that consecutive elements correspond
#     with consecutive cars. F.e. element 0 can correspond with car 1,
#     element 1 with car 2 and so on.
# 3) the cars dictionairy
# 4) road array
def position_update_one_car(car_pos_index, car_pos, cars, road):
    pos = car_pos[car_pos_index]
    i = road[pos]
    speed = cars[i]
    # if speed is zero, car doesn't move
    if speed == 0:
        return cars, road
    neighbors = car_positions(road[pos: pos + speed + 2])
    # consider edge case when the updating the last car in the array,
    # it can dissapear off the edge when position + speed > len(array)
    if car_pos_index == len(car_pos)-1:
        # delete car if it disappears of the road
        if pos + speed > road.size - 1:
            road[pos] = 0
            # if a car gets deleted, we increment the global counter with 1 to
            # track the flow
            config.flow_counter += 1
            del cars[i]
            # only return the updated car dict if a car is deleted
            return cars, road
        # otherwise, the car can get up to the exact last block
        else:
            road[pos + speed] = road[pos]
            road[pos] = 0
            return cars, road
    # if not last car, update the position as normal
    # if there is only one neighbor (i.e. itself), the road
    # is clear to move at it's current speed
    if neighbors.size == 1:
        road[pos + speed] = road[pos]
        road[pos] = 0
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
                road[pos + min_gap] = road[pos]
                road[pos] = 0
            # otherwise, there is a large enough gap given the current speed
            # to move and it simply updates the position using this speed
            else:
                road[pos + speed] = road[pos]
                road[pos] = 0
        return cars, road


# update position of all cars
def position_update(car_pos, cars, road):
    for i in range(len(car_pos)):
        cars, road = position_update_one_car(i, car_pos, cars, road)
    return cars, road


# Generate a new car randomly if the
# first position of the road is free.
# always returns the car and road array
def generate_new_cars(cars, road, p_gen=1, speed_random=False):
    if not road[0:2].any() and np.random.rand() <= p_gen:
        config.car_counter += 1
        # give the new key a new label
        new_car = config.car_counter
        road[0] = new_car
        
        # if speed randomization is false, set speed to Vmax
        if not speed_random:
            # check if Vm_vary is activated
            if config.Vm_vary!=0:
                # slower Vmax case
                if new_car%config.Vm_vary==0:
                    cars[new_car] = config.Vmax2
                # fast Vmax case
                else:
                    cars[new_car] = config.Vmax1
            # otherwise use default of Vmax1
            else:
                cars[new_car] = config.Vmax1       


            
        else:
            # choose random speed uniformly
            # again, check for Vm_vary
            if config.Vm_vary!=0:
                if new_car%config.Vm_vary==0:
                    # slow Vmax
                    cars[new_car] = random_speed(config.Vmax2)
                else:
                    # fast Vmax
                    cars[new_car] = random_speed(config.Vmax1)
            # standard Vmax1
            else:
                cars[new_car] = random_speed(config.Vmax1)
    return cars, road


def main_loop(P_init=0.05, iterations=10, road_len=1000,
              Vmax1=10, Vmax2=7, Vrandom=False,
               p_gen=0.05, reaction_time=0, p_Vrandom=0.1, 
               Vrandom_amount=1, Vm_vary=0):
    config.Vmax1=Vmax1
    config.Vmax2=Vmax2
    # check wether or not Vm_vary functionality is on, 
    # if not, all cars have one Vmax.
    # make the initial road and cars
    cars, road = random_init_cars(road_len, P_init,
                                  Vrandom)
    
    # make initial car positions
    positions = car_positions(road)
    config.plot_data = []
    config.plot_data.append(np.copy(road))
    # run the main experiment loop
    if reaction_time != 0:
        for i in range(iterations):
            # update the position using current speed
            cars, road = position_update(positions, cars, road)
            # randomize their speed, modeling driver cruise inconsistency
            cars = speed_randomizer(cars, p_Vrandom, Vrandom_amount)
            # generate randomly new cars at the beginning of the road
            cars, road = generate_new_cars(cars, road, p_gen,
                                           Vrandom)
            config.plot_data.append(np.copy(road))
            # get the new car positions from the new array
            positions = car_positions(road)
            if positions.size == 0:
                continue
            # Update the speed based on the new position when i is equal to
            # an exact multiple of the reaction time, this has the effect of
            # delaying each speed update with 1 reaction time.
            if i % reaction_time == 0:
                cars = speed_update(positions, cars, road)
                
    # if reaction time is zero, do the basic loop without reaction time
    # (slight code redundancy, but avoids unnecessary checks inside the loop)
    if reaction_time == 0:
        for i in range(iterations):
            cars, road = position_update(positions, cars, road)
            cars = speed_randomizer(cars, p_Vrandom, Vrandom_amount)
            cars, road = generate_new_cars(cars, road, p_gen,
                                           Vrandom)
            config.plot_data.append(np.copy(road))
            positions = car_positions(road)
            if positions.size == 0:
                continue
            cars = speed_update(positions, cars, road)
    return cars, road
        




# quick plot of the road in every timestep
def plot_traffic():
    r1 = np.array([np.array(xi) for xi in config.plot_data])
    r2 = np.where(r1>0, 1, r1)
    plt.figure(figsize=(100,100))
    plt.imshow(r2, cmap='binary', interpolation=None)
    plt.show()
