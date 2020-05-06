import matplotlib.pyplot as plt
import numpy as np

data = [[1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 3, 0, 3]]


fig = plt.figure()
ax = fig.add_subplot(111)
ax.axes.get_yaxis().set_visible(False)
ax.set_aspect(1)

def avg(a, b):
    return (a + b) / 2.0

for y, row in enumerate(data):
    for x, col in enumerate(row):
        x1 = [x, x+0.1]
        y1 = [0, 0]
        y2 = [1, 1]
        if col == 1:
            plt.fill_between(x1, y1, y2=y2, color='red')
            plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), "A", 
                                        horizontalalignment='center',
                                        verticalalignment='center')
        if col == 2:
            plt.fill_between(x1, y1, y2=y2, color='orange')
            plt.text(avg(x1[0], x1[0]+0.1), avg(y1[0], y2[0]), "B", 
                                        horizontalalignment='center',
                                        verticalalignment='center')
        if col == 3:
            plt.fill_between(x1, y1, y2=y2, color='yellow')
            plt.text(avg(x1[0], x1[0]+0.1), avg(y1[0], y2[0]), "C", 
                                        horizontalalignment='center',
                                        verticalalignment='center')

line, = ax.plot(np.random.rand(10))

            
plt.ylim(1, 0)
plt.show()
