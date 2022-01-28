import numpy as np
import matplotlib.pyplot as plt


class TopicGraph:


  def __init__(self, graph):

    self.graph = graph

    self.f = np.zeros((len(self.graph.c), 2))
    self.v = np.zeros((len(self.graph.c), 2))
    self.r = np.zeros((len(self.graph.c), 2))

    self.spacing = 0.2
    self.k = 1

    length = np.ceil(np.sqrt(len(self.graph.c)))
    grid = np.arange(length) * 50
    gx, gy = np.meshgrid(grid, grid)
    self.r[:,0] = gx.flatten()[:len(self.graph.c)]
    self.r[:,1] = gy.flatten()[:len(self.graph.c)]


  def simulate(self, steps):

    for _ in range(steps):

      self.step()
      


  def step(self, dt=0.1 ):

    self.f = 0.1 * (-1*self.r + self.f[0])

    for n in np.argwhere(self.graph.c.sum(axis=1) != 0):

      self.f[n] += self.k * np.dot(self.graph.c[n], self.r - self.r[n])
      self.v[n] += dt * self.f[n]
      new_x = self.r[n] + dt * self.v[n]

      sep = np.linalg.norm(self.r - new_x, axis=1)
      col = np.argwhere(sep < self.graph.sizes + self.graph.sizes[n] + self.spacing)

      if len(col) == 0:
        
        self.r[n] = new_x

      else:

        if len(col) == 1 and col[0] == n:

          self.r[n] = new_x

        else:

          self.v[n] = 0


  def plot(self, ax, lines=False):

    circles = np.argwhere(self.graph.c.sum(axis=1) != 0)

    for i in circles:
      i = i[0]
      circ = plt.Circle(self.r[i], self.graph.sizes[i], color="r")
      ax.add_patch(circ)
      if lines:
        pass
      # ax.text(*self.r[i], self.graph.names_arr[i], horizontalalignment='center', verticalalignment='center')



