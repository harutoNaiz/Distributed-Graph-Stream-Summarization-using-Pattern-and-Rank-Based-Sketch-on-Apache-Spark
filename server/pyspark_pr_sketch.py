import numpy as np
import hashlib

class PRSketchSpark:
    def __init__(self, width, depth, pattern_length, conflict_limit=3):
        self.width = width
        self.depth = depth
        self.pattern_length = pattern_length
        self.conflict_limit = conflict_limit
        
        # Initialize sketch matrix
        self.gM = np.zeros((width, width, depth), dtype=[
            ('rank', 'i4'), 
            ('weight', 'f4'), 
            ('list', 'O')
        ])
        
        for i in range(width):
            for j in range(width):
                for k in range(depth):
                    self.gM[i, j, k]['list'] = []

    def _generate_hash_functions(self):
        return [lambda x, seed=i: int(hashlib.md5((str(x) + str(seed)).encode()).hexdigest(), 16) % self.width 
                for i in range(self.depth)]

    def _pattern_hash(self, node):
        hash_funcs = self._generate_hash_functions()
        return [h(node) for h in hash_funcs]

    def _rank_hash(self, node):
        np.random.seed(hash(node) % 1000)
        return np.random.permutation(self.pattern_length).tolist()

    def update(self, edges):
        """Update sketch with a list of edges"""
        for row in edges:
            source = str(row['source'])
            dest = str(row['dest'])
            weight = float(row['weight']) if 'weight' in row else 1.0

            src_pattern = self._pattern_hash(source)
            dest_pattern = self._pattern_hash(dest)
            src_rank = self._rank_hash(source)
            dest_rank = self._rank_hash(dest)

            for i in range(self.depth):
                x, y = src_pattern[i], dest_pattern[i]
                rank_val = min(src_rank[i], dest_rank[i])
                cell = self.gM[x, y, i]

                if rank_val > cell['rank']:
                    cell['rank'] = rank_val
                    cell['weight'] = weight
                    cell['list'] = [(source, dest)]
                elif rank_val == cell['rank']:
                    cell['weight'] += weight
                    if (source, dest) not in cell['list']:
                        cell['list'].append((source, dest))
                        if len(cell['list']) > self.conflict_limit:
                            cell['list'].pop(0)

    def edge_query(self, source, dest):
        source = str(source)
        dest = str(dest)
        
        src_pattern = self._pattern_hash(source)
        dest_pattern = self._pattern_hash(dest)
        src_rank = self._rank_hash(source)
        dest_rank = self._rank_hash(dest)

        min_weight = float('inf')
        found = False

        for i in range(self.depth):
            x, y = src_pattern[i], dest_pattern[i]
            cell = self.gM[x, y, i]

            if min(src_rank[i], dest_rank[i]) == cell['rank']:
                found = True
                min_weight = min(min_weight, cell['weight'])

        return float(min_weight) if found else 0.0

    def reachability_query(self, source, dest):
        source = str(source)
        dest = str(dest)
        
        for i in range(self.depth):
            for x in range(self.width):
                for y in range(self.width):
                    cell = self.gM[x, y, i]
                    for pair in cell['list']:
                        if len(pair) >= 2 and pair[0] == source and pair[1] == dest:
                            return True
        return False