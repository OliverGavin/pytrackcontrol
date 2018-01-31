from collections import defaultdict, deque


class Dag:

    def __init__(self, root=None):
        """Constructor for creating a Directed Acyclic Graph.

        Parameters
        ----------
        root: str, optional
            Set a single pre-determined root. Otherwise it/they can be found.
        """
        self._root = root
        self._vertices = set([root]) if root else set()
        self._graph = defaultdict(list)

    def add_edge(self, u, v):
        """Add an edge to the dag from vertex u to v.
        """
        if u not in self._vertices:
            self._vertices.add(u)
        if v not in self._vertices:
            self._vertices.add(v)

        self._graph[u].append(v)

    def topological_sort(self):
        # get indegree of each vertex
        indegree = {u: 0 for u in self._vertices}
        for u_dependants in self._graph.values():
            for v in u_dependants:
                indegree[v] += 1

        if self._root:
            # we already know there is a single vertex with indegree of 0
            queue = deque([self._root])
        else:
            # add all vertices with indegree of 0
            queue = deque([v for v, deg in indegree.items() if deg == 0])

        count = 0   # vertices visited

        ordering = []   # topological ordering

        while queue:

            u = queue.popleft()
            ordering.append(u)

            for v in self._graph[u]:
                indegree[v] -= 1

                if indegree[v] == 0:
                    queue.append(v)

            count += 1

        if count != len(self._vertices):
            raise ValueError("Graph contains cycles")

        return ordering
