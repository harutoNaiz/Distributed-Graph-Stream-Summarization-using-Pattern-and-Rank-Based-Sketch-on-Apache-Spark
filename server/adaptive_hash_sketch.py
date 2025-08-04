import numpy as np
import hashlib

class AdaptiveHashSketch:
    def __init__(self, width, depth, pattern_length, conflict_limit=3):
        self.width = width
        self.depth = depth
        self.pattern_length = pattern_length
        self.conflict_limit = conflict_limit
        self.current_hash_count = depth
        self.gM = {}
        self._initialize_matrix()

    def _initialize_matrix(self):
        for k in range(self.current_hash_count):
            if k not in self.gM:
                self.gM[k] = np.zeros((self.width, self.width), dtype=[
                    ('weight', 'f4'), 
                    ('list', 'O')
                ])
                for i in range(self.width):
                    for j in range(self.width):
                        self.gM[k][i, j]['list'] = []

    def _generate_hash_functions(self, count=None):
        if count is None:
            count = self.current_hash_count
        return [lambda x, seed=i: int(hashlib.md5((str(x) + str(seed)).encode()).hexdigest(), 16) % self.width 
                for i in range(count)]

    def _pattern_hash(self, node, hash_count=None):
        if hash_count is None:
            hash_count = self.current_hash_count
        hash_funcs = self._generate_hash_functions(hash_count)
        return [h(node) for h in hash_funcs]

    def _expand_hash_functions(self):
        old_count = self.current_hash_count
        self.current_hash_count += self.depth
        print(f"[ADAPTIVE] Expanding hash functions from {old_count} to {self.current_hash_count}")
        self._initialize_matrix()
        self._redistribute_data()

    def _redistribute_data(self):
        all_edges = []
        for k in range(min(self.current_hash_count - self.depth, len(self.gM))):
            for i in range(self.width):
                for j in range(self.width):
                    cell = self.gM[k][i, j]
                    for edge_pair in cell['list']:
                        if len(edge_pair) >= 2:
                            all_edges.append({
                                'source': edge_pair[0],
                                'dest': edge_pair[1],
                                'weight': cell['weight'] / len(cell['list'])
                            })
        self._clear_old_data()
        if all_edges:
            self.update(all_edges)

    def _clear_old_data(self):
        for k in range(self.current_hash_count - self.depth):
            if k in self.gM:
                for i in range(self.width):
                    for j in range(self.width):
                        self.gM[k][i, j]['weight'] = 0.0
                        self.gM[k][i, j]['list'] = []

    def _check_collision_rate(self):
        total_cells = 0
        full_cells = 0
        for k in range(self.current_hash_count):
            if k in self.gM:
                for i in range(self.width):
                    for j in range(self.width):
                        total_cells += 1
                        if len(self.gM[k][i, j]['list']) >= self.conflict_limit:
                            full_cells += 1
        collision_rate = full_cells / total_cells if total_cells > 0 else 0
        return collision_rate > 0.8

    def update(self, edges):
        for row in edges:
            source = str(row['source'])
            dest = str(row['dest'])
            weight = float(row['weight']) if 'weight' in row else 1.0
            src_pattern = self._pattern_hash(source)
            dest_pattern = self._pattern_hash(dest)
            edge_placed = False

            for i in range(self.current_hash_count):
                if i >= len(src_pattern) or i >= len(dest_pattern):
                    src_pattern = self._pattern_hash(source, self.current_hash_count)
                    dest_pattern = self._pattern_hash(dest, self.current_hash_count)

                x, y = src_pattern[i], dest_pattern[i]
                if i not in self.gM:
                    self._initialize_matrix()

                cell = self.gM[i][x, y]
                edge_exists = any(pair[0] == source and pair[1] == dest 
                                  for pair in cell['list'] if len(pair) >= 2)

                if edge_exists:
                    cell['weight'] += weight
                    edge_placed = True
                    break
                elif len(cell['list']) < self.conflict_limit:
                    cell['weight'] += weight
                    cell['list'].append((source, dest))
                    edge_placed = True
                    break

            if not edge_placed:
                if self._check_collision_rate():
                    self._expand_hash_functions()
                    self.update([row])

    def edge_query(self, source, dest):
        source = str(source)
        dest = str(dest)
        src_pattern = self._pattern_hash(source)
        dest_pattern = self._pattern_hash(dest)
        total_weight = 0.0
        found = False

        for i in range(self.current_hash_count):
            if i >= len(src_pattern) or i >= len(dest_pattern):
                src_pattern = self._pattern_hash(source, self.current_hash_count)
                dest_pattern = self._pattern_hash(dest, self.current_hash_count)

            if i not in self.gM:
                continue

            x, y = src_pattern[i], dest_pattern[i]
            cell = self.gM[i][x, y]

            for pair in cell['list']:
                if len(pair) >= 2 and pair[0] == source and pair[1] == dest:
                    edge_weight = cell['weight'] / len(cell['list']) if len(cell['list']) > 0 else 0
                    total_weight += edge_weight
                    found = True
                    break

        return float(total_weight) if found else 0.0

    def reachability_query(self, source, dest):
        source = str(source)
        dest = str(dest)
        for i in range(self.current_hash_count):
            if i not in self.gM:
                continue
            for x in range(self.width):
                for y in range(self.width):
                    cell = self.gM[i][x, y]
                    for pair in cell['list']:
                        if len(pair) >= 2 and pair[0] == source and pair[1] == dest:
                            return True
        return False

    def get_stats(self):
        total_edges = 0
        total_weight = 0.0
        occupied_cells = 0
        total_cells = 0
        for i in range(self.current_hash_count):
            if i not in self.gM:
                continue
            for x in range(self.width):
                for y in range(self.width):
                    total_cells += 1
                    cell = self.gM[i][x, y]
                    if len(cell['list']) > 0:
                        occupied_cells += 1
                        total_edges += len(cell['list'])
                        total_weight += cell['weight']
        return {
            'hash_functions': self.current_hash_count,
            'total_edges': total_edges,
            'total_weight': total_weight,
            'occupied_cells': occupied_cells,
            'total_cells': total_cells,
            'occupancy_rate': occupied_cells / total_cells if total_cells > 0 else 0
        }
