from collections import defaultdict
import pandas as pd


class Graph:
    def __init__(self):
        self.graph = defaultdict(dict)

    def add_edge(self, u, v, capacity):
        self.graph[u][v] = capacity
        self.graph[v][u] = capacity

    def ford_fulkerson(self, source, sink):
        parent = {}

        def bfs(source, sink):
            visited = set()
            queue = [source]
            visited.add(source)

            while queue:
                u = queue.pop(0)
                for v, capacity in self.graph[u].items():
                    if v not in visited and capacity > 0:
                        queue.append(v)
                        parent[v] = u
                        visited.add(v)
                        if v == sink:
                            return True
            return False

        max_flow = 0

        while bfs(source, sink):
            path_flow = float("inf")
            s = sink
            while s != source:
                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]

            max_flow += path_flow

            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                v = parent[v]

        return max_flow

    def calculate_od_traffic_value(self, source, sink):

        pass


def read_csv(input_file):
    data = pd.read_csv(input_file, delimiter=";")
    return data


def read_txt(input_file):
    with open(input_file, "r") as file:
        lines = file.readlines()
        paths = []
        for line in lines:
            paths.append([path.strip('"') for path in line.strip().split(",")])
    return paths


def main():
    data = read_csv("networks/wielun/daily_traffic_base.csv")
    data["from"] = data["from"].str.strip().str.strip('"')
    data["to"] = data["to"].str.strip().str.strip('"')

    g = Graph()

    for index, row in data.iterrows():
        g.add_edge(row["from"], row["to"], row["trailer"])

    max_flow = g.ford_fulkerson("D", "G")
    print(max_flow)
    values = read_txt("networks/wielun/wielun_paths.txt")


if __name__ == "__main__":
    main()
