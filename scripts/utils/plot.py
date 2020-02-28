import sys
import numpy as np
import matplotlib.pyplot as plt

file = sys.argv[1]

with open(file) as f:
    lines = f.read().splitlines()

x = [int(line.split(' ')[1]) for line in lines]
#x_sum =  sum(x)
#x = [i / x_sum for i in x]
x_len = len(x)
x.extend([0] * (1500 - len(x)))
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x)
ax.axvline(x=x_len)
fig.canvas.draw()
plt.show()
