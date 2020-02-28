import sys
import numpy as np
import matplotlib.pyplot as plt

file = sys.argv[1]

with open(file) as f:
    lines = f.read().splitlines()

x = [int(line.split(' ')[1]) for line in lines]
#x_sum =  sum(x)
fig = plt.figure()
ax = fig.add_subplot(111)
n, bins, rectangles = ax.hist(x, 100, density=True)
fig.canvas.draw()
plt.show()
