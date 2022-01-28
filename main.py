import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import networkx as nx
from topicGraph import TopicGraph
import numpy as np
from urllib.parse import unquote
import pickle as pkl


class Graph:

  def __init__(self, n, m):

    k = (1 + n)*(n**(m-1))

    self.c = np.zeros((k, k))
    self.names = {}
    self.names_arr = []
    self.sizes = np.zeros((k,))

class Mapper:

  def __init__(self):

    self.searching = []
    self.rootURL = "https://en.wikipedia.org/wiki/"
    self.headers = {
      'User-Agent': 'My User Agent 1.0',
      'From': 'youremail@domain.com'
    }
    self.n = 0


  def load(self, file):

    self.graph = Graph(10, 2)

    with open("results/" + file, 'rb') as f:
      self.graph = pkl.load(f)


  def map(self, iterations, links_per_page, startUrl, file):

    self.graph = Graph(links_per_page, iterations)

    self.n = 1

    self.graph.names[startUrl] = 0
    self.graph.names_arr.append(startUrl)
    self.searching.append(startUrl)

    for _ in range(iterations):

      self.search(links_per_page)

    print("Scraping Views")

    self.scrapeViews()

    with open("results/" + file, 'wb') as out:
      pkl.dump(self.graph, out)
  

  def search(self, m):

    nextLayer = []
    print("Searching: ", self.searching)

    for url in self.searching:

      print(":: ", url)

      page = requests.get(self.rootURL + url)
      soup = BeautifulSoup(page.content, "html.parser")
      links = soup.find_all("a")

      for link in links[:2*m]:
        
        Url = link.get("href")

        if (Url is not None) and (link.get("class") is None) and (":" not in Url):

          if Url[:5] == "/wiki":

            Url = Url[6:]

            n = self.graph.names[url]

            if Url in self.graph.names:

              ind = self.graph.names[Url]
              self.graph.c[max(ind, n)][min(ind, n)] = 1

            else:

              self.graph.names[Url] = self.n
              self.graph.names_arr.append(Url)
              self.graph.c[self.n, n] = 1
              self.n += 1
              nextLayer.append(Url)
              
    self.searching = nextLayer


  def scrapeViews(self):

    for node in self.graph.names:

      self.graph.sizes[self.graph.names[node]] = self.views(node)/10000


  def views(self, url):

    views = 0

    statURL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/"+url+"/monthly/2021010100/2021053100"
    statpage = requests.get(statURL, headers=self.headers)
    json = statpage.json()

    if "items" in json:

      views = int(statpage.json()["items"][0]["views"])

    return views


  def thresh(self, n):

    self.graph.c += np.transpose(self.graph.c)

    ind = np.where(self.graph.c.sum(axis=0) < n)
    self.graph.c[:,ind], self.graph.c[ind] = 0, 0


  def drawx(self, thresh=3):

    G = nx.Graph()
    G.views = {}

    self.thresh(thresh)

    for ind in np.where(self.graph.c.sum(axis=1) != 0)[0]:

        name = unquote(self.graph.names_arr[ind])
        G.add_node(name)
        G.views[name] = self.graph.sizes[ind] * 100

    l = np.where(self.graph.c == 1)

    for edge in np.transpose(l):

      G.add_edge(unquote(self.graph.names_arr[edge[0]]), unquote(self.graph.names_arr[edge[1]]))

    pos=nx.spring_layout(G)
    ax = plt.subplot()
    nx.draw(
        G,
        pos,
        node_size=[G.views[v] for v in G],
        with_labels=True,
    )
    plt.show()

  
  def draw(self, thresh=2):

    self.thresh(thresh)

    t = TopicGraph(self.graph)

    t.simulate(1000)
    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))
    t.plot(ax, lines=True)

    ax.axis("off")
    ax.relim()
    ax.autoscale_view()
    plt.show()  


m = Mapper()
# m.map(3, 10, "Mathematics", "3_10_mathematics.pkl")
m.load('3_10_mathematics.pkl')
m.drawx(thresh=12)
