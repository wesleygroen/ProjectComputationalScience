flow_counter = 0
car_counter = 0
plot_data = []
Vmax1 = 6
Vmax2 = 5


# Vm_vary is used to seperate the slow and fast driver classes,
# Vm_vary will be an integer number, such that the portion of
# slow drivers is equal to 1 / Vm_vary

#     We use it as a modulo operator,
# using i % (modulo) Vm_vary == 0 to check if the i-th driver label is
# a multiple of Vm_vary, and making these drivers have the alternative,
# lower Vmax.
Vm_vary = 2

# Table to define the speed, distance becomes an index into
# this list to get the corresponding speed update response.
# This is used for the aggresive driver scenario.

# table for the fast drivers
speed_table1 = [0, 3, 5, Vmax1, Vmax1]
# table for the slower drivers
speed_table2 = [0, 3, 4, Vmax2, Vmax2]
