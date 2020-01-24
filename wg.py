#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import random 
from collections import defaultdict
import matplotlib.pyplot as plt
from CA import *


# In[2]:


# def main_loop(P_init, 
#               iterations=10, road_len=int(1e3), Vmax=6, Vrandom=True,
#              p_gen=0.5):
    
#     # make the initial road and cars
#     cars, road = random_init_cars(road_len, P_init,
#                                   Vrandom,
#                                   Vmax)
#     # make initial car positions
#     positions = car_positions(road)
    
#     im = []
#     im.append(np.copy(road))
#     # run the main experiment loop
#     for i in range(iterations):
#         # update the position using current speed
#         cars, road = position_update(positions, cars, road)
#         im.append(np.copy(road))
#         # get the new car positions from the new array
#         positions = car_positions(road)
#         # update the speed based on the new position
#         cars = speed_update(positions, cars, road, Vmax)
# #         print(road)
        
#     return cars, road, im     
def main_loop(P_init, 
              iterations=10, road_len=int(1e2), Vmax=6, Vrandom=True,
             p_gen=0.1):
    
    # make the initial road and cars
    cars, road = random_init_cars(road_len, P_init,
                                  Vrandom,
                                  Vmax)
    # make initial car positions
    positions = car_positions(road)
    im = []
    im.append(np.copy(road))
    # run the main experiment loop
    for i in range(iterations):
        # update the position using current speed
        cars, road = position_update(positions, cars, road)
        
        # generate randomly new cars at the beginning of the road
#         cars, road = generate_new_cars(cars, road, p_gen=0.5, speed_random=False, Vmax=6)
        im.append(np.copy(road))
        # get the new car positions from the new array
        positions = car_positions(road)
        
        # update the speed based on the new position
        cars = speed_update(positions, cars, road, Vmax)
#         print(road)

        
    return cars, road, im
        
# cars, road = main_loop(0.3, 1000)         
        
cars, road, r = main_loop(0.5, 1000)


# In[3]:


# cars, road = random_init_cars(200, 0.6)
# r = []
# print(cars)
# r.append(np.copy(road))
# for i in range(100):
#     pos = car_positions(road)
#     cars, road = position_update(pos, cars, road)
#     print(cars)
#     pos = car_positions(road)
#     cars = speed_update(pos, cars, road)
#     print(cars)
#     r.append(np.copy(road))

# r1 = np.asarray(r)
r1 = np.array([np.array(xi) for xi in r])
r2 = np.where(r1>0, 1, r1)
plt.figure(figsize=(200,200))
plt.imshow(r2, cmap='binary', interpolation=None)
plt.plot()

