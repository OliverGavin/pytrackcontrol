from unittest import TestCase

from pytrackcontrol.graph import Dag


class TestDag(TestCase):

    def test_empty(self):
        dag = Dag()
        result = dag.topological_sort()
        self.assertEqual(result, [])

    def test_single_root(self):
        dag = Dag('root')
        result = dag.topological_sort()
        self.assertEqual(result, ['root'])

    def test_single_edge(self):
        dag = Dag()
        dag.add_edge('parent', 'child')
        result = dag.topological_sort()
        self.assertEqual(result, ['parent', 'child'])

    def test_two_roots(self):
        dag = Dag()
        dag.add_edge('parent1', 'child')
        dag.add_edge('parent2', 'child')
        result = dag.topological_sort()
        self.assertEqual(set(result[:2]), set(['parent1', 'parent2']))
        self.assertEqual(result[2], 'child')

    def test_binary(self):
        dag = Dag()
        dag.add_edge('parent', 'child1')
        dag.add_edge('parent', 'child2')
        result = dag.topological_sort()
        self.assertEqual(result[0], 'parent')
        self.assertEqual(set(result[1:]), set(['child1', 'child2']))

    def test_diamond(self):
        dag = Dag()
        dag.add_edge('parent', 'child1')
        dag.add_edge('parent', 'child2')
        dag.add_edge('child1', 'grandchild')
        dag.add_edge('child2', 'grandchild')
        result = dag.topological_sort()
        self.assertEqual(result[0], 'parent')
        self.assertEqual(set(result[1:3]), set(['child1', 'child2']))
        self.assertEqual(result[3], 'grandchild')

    def test_complex(self):
        dag = Dag()
        dag.add_edge('parent1', 'child1')
        dag.add_edge('parent1', 'child2')
        dag.add_edge('parent2', 'child2')
        dag.add_edge('parent2', 'child3')
        dag.add_edge('child1', 'grandchild1')
        dag.add_edge('child2', 'grandchild1')
        dag.add_edge('child2', 'grandchild2')
        dag.add_edge('child3', 'grandchild2')

        result = dag.topological_sort()
        self.assertEqual(set(result[:2]), set(['parent1', 'parent2']))
        self.assertEqual(set(result[2:5]), set(['child1', 'child2', 'child3']))
        self.assertEqual(set(result[5:]), set(['grandchild1', 'grandchild2']))
