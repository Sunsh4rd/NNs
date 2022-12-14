import argparse
from dataclasses import dataclass
import json
import math
import re
import sys


@dataclass(repr=True)
class Vertex:
    name: str
    value: int = 0

    def __eq__(self, __o: 'Vertex') -> bool:
        return self.name == __o.name

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Edge:
    source: Vertex
    dest: Vertex
    order: int


class Graph:

    def __init__(self, vertices: list[Vertex], edges: list[Edge], sinks: list[Vertex]) -> None:
        self.vertices = vertices
        self.edges = edges
        self.sinks = sinks

    @staticmethod
    def from_file(path: str) -> 'Graph':
        item = r'\(\s*\w+\s*,\s*\w+\s*,\s*[1-9]{1}\d*\s*\)'
        seq = f'\s*{item}\s*(,\s*{item}\s*)*'
        with open(f'input_files/{path}', 'r', encoding='utf-8') as f:
            g = f.read()
            if re.fullmatch(seq, g):
                graph_edges = [re.findall(r'\w+', i)
                               for i in re.findall(item, g)]
            else:
                print('Ошибка во входном файле!')
                exit()

            vertices_list, edges_list, vertices_from, vertices_to = [], [], [], []
            for source, dest, order in graph_edges:
                s, d = Vertex(source), Vertex(dest)
                if s not in vertices_list:
                    vertices_list.append(s)
                if d not in vertices_list:
                    vertices_list.append(d)
                if s not in vertices_from:
                    vertices_from.append(s)
                if d not in vertices_to:
                    vertices_to.append(d)
                edges_list.append(Edge(s, d, order))

            if len(vertices_list) == len(vertices_from):
                print('В графе нет вершин-стоков')

            sinks = [
                v for v in vertices_list if v not in vertices_from and v in vertices_to]
            edges_list.sort(key=lambda x: x.order)

            return Graph(vertices_list, edges_list, sinks)

    def to_json(self, path: str) -> None:
        with open(f'output_files/{path}', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'vertices': [str(v) for v in self.vertices],
                    'edges': [
                        {'source': str(edge.source),
                         'dest': str(edge.dest),
                         'order': edge.order
                         } for edge in self.edges
                    ]
                }, f, indent=4)

    def is_acyclic(self) -> bool:
        used = {v: 0 for v in self.vertices}

        def dfs(v: Vertex) -> bool:
            used[v] = 1
            adjacent_vertices = (i.dest for i in self.edges if i.source == v)
            for to in adjacent_vertices:
                if used[to] == 0:
                    if dfs(to):
                        return True
                elif used[to] == 1:
                    return True
            used[v] = 2
            return False

        for v in self.vertices:
            if dfs(v):
                return False

        return True

    def get_function_by_graph(self) -> str:
        if not self.is_acyclic():
            print('Граф содержит цикл, невозможно построить функцию!')
            return None

        vertices_from, vertices_to = [], []
        for e in self.edges:
            if e.source not in vertices_from:
                vertices_from.append(e.source)
            if e.dest not in vertices_to:
                vertices_to.append(e.dest)

        if len(self.vertices) == len(vertices_from):
            print('Граф не содержит стоков, невозможно построить функцию!')
            return None

        sinks = [
            v for v in self.vertices if v not in vertices_from and v in vertices_to]
        used, fun = [], []

        def get_function_as_string(sink: Vertex) -> None:
            fun.append(str(sink))
            used.append(sink)
            flag = False
            ansectors = 0
            for e in self.edges:
                if e.dest == sink and e.source not in used:
                    ansectors += 1
                    flag = True
                    if ansectors == 1:
                        fun.append('(')
                    if ansectors >= 2:
                        fun.append(',')
                    get_function_as_string(e.source)
            if flag and ansectors <= 1:
                fun.append(')')
            elif flag and ansectors >= 2:
                fun.append(')')

        all_funs = []
        for s in sinks:
            get_function_as_string(s)
            all_funs.append(''.join(fun))
            fun = []
            used = []

        return ''.join(all_funs)

    def get_function_value_by_graph(self, vert_op_dict: dict) -> list[int]:
        used = []
        edges_list = self.edges

        def value_function_helper(v: Vertex):
            used.append(v)
            v.value = vert_op_dict[str(v)]
            if v.value.isdigit():
                v.value = int(v.value)
            vert_ancestors = []
            for e in edges_list:
                if e.dest == v and e.source not in used:
                    vert_ancestors.append(e.source)
                    value_function_helper(e.source)
            if v.value == '+':
                v.value = 0
                for va in vert_ancestors:
                    v.value += int(va.value)
            if v.value == 'exp':
                v.value = round(math.exp(int(vert_ancestors[0].value)))
            if v.value == '*':
                v.value = 1
                for va in vert_ancestors:
                    v.value *= int(va.result)

        fun_values = []
        for s in self.sinks:
            used = []
            value_function_helper(s)
            fun_values.append(s.value)

        return fun_values


class Matrix:

    def __init__(self, matrix: list[list[int]], vector: list[int]) -> None:
        self.matrix = matrix
        self.vector = vector

    @staticmethod
    def from_file(path_vector: str, path_matrix: str) -> 'Matrix':
        with open(path_vector, 'r', encoding='utf-8') as f:
            vector_data = f.read().split()
        vector = [int(x) for x in vector_data]
        with open(path_matrix, 'r', encoding='utf-8') as f:
            matrix_data = f.readlines()
        matrix = []
        idx = 0
        length = len(vector)
        for line in matrix_data:
            idx += 1
            line = line.replace('[', ' ').replace(']', ' ')[1:-2].split('   ')
            tmp = []
            for x in line:
                x = x.split(' ')
                try:
                    x = [int(i) for i in x]
                    tmp.append(x)
                except ValueError:
                    print(f'Ошибка во входном файле в строке {idx}')
                    return None
                if len(x) != length:
                    print(
                        f'Не совпадает число компонент нейронов в слоях {idx - 1} - {idx}')
                    return None
            length = len(line)
            matrix.append([tmp])

        return Matrix(matrix, vector)

    def get_network(self):
        new_matrix = []

        for layer in self.matrix:
            tmp = []
            for x in layer:
                for neuron in x:
                    value = 0
                    for i in range(len(self.vector)):
                        value += neuron[i] * self.vector[i]
                    value /= (1 + abs(value))
                    tmp.append(value)
                new_matrix.append(tmp)
                self.vector = tmp
        return new_matrix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', choices=['1', '2', '3', '4'], required=True)
    parser.add_argument('--ig', default='graph.txt')
    parser.add_argument('--og', default='graph.json')
    parser.add_argument('--of', default='function.txt')
    parser.add_argument('--op', default='operations.txt')
    parser.add_argument('--im', default='matrix.txt')
    parser.add_argument('--iv', default='vector.txt')
    parser.add_argument('--om', default='matrix.json')
    parser.add_argument('--ow', default='output.txt')
    args = parser.parse_args()

    match args.t:
        case '1':
            rg = Graph.from_file(args.ig)
            rg.to_json(args.og)
        case '2':
            rg = Graph.from_file(args.ig)
            function = rg.get_function_by_graph()
            with open(f'output_files/{args.of}', 'w', encoding='utf-8') as f:
                f.write(function)
        case '3':
            rg = Graph.from_file(args.ig)
            with open(f'input_files/{args.op}', 'r', encoding='utf-8') as f:
                data = f.read()
                vert_op_list = re.findall(
                    r'\w : [*+]|\w : exp|\w : \d*', data)
                if len(vert_op_list) != len(data.split('\n')):
                    print('Ошибка во входном файле!')
                    exit()
                vert_op_dict = {}
                for v_op in vert_op_list:
                    v, op = v_op.split(' : ')
                    vert_op_dict[v] = op
            ops = vert_op_dict
            function_value = rg.get_function_value_by_graph(ops)
            with open(f'output_files/{args.of}', 'w', encoding='utf-8') as f:
                f.write(' '.join(str(v) for v in function_value))
        case '4':
            mm = Matrix.from_file(
                f'input_files/{args.iv}', f'input_files/{args.im}')
            if mm:
                with open(f'output_files/{args.om}', 'w', encoding='utf-8') as f:
                    json.dump(
                        {
                            'network': {
                                'layers': mm.matrix
                            }
                        }, f, indent=4
                    )
                results = mm.get_network()
                with open(f'output_files/{args.ow}','w',encoding='utf-8') as f:
                    f.write(' '.join(str(x) for x in results[-1]))


if __name__ == '__main__':
    main()
