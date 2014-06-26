# First cut of high-level M-Block code
# Originally: James Bern 6/25/2014

from pprint import pprint
from pprint import pformat

class World:
    ''' '''
    def __init__(self):
        self.blocks = []
        self._next_ID = 0

    def add(self, block):
        assert(isinstance(block, Block))
        block.ID = self.next_ID()
        self.blocks.append(block)

    def next_ID(self):
        return_me = self._next_ID
        self._next_ID += 1
        return return_me

    # def find_global_configuration(self):
        # # TODO: Call find_neighbors(...)
        # pass

    # # TODO: Strip out into actual C call
    # # # TODO: Try out SWIG
    # @staticmethod
    # def find_neighbors(block):
        # pass

    def __repr__(self):
        return pformat({block:
            set(neighbor for neighbor in block.neighbors_dict.values()
            if neighbor != None) for block in self.blocks})
    
# class Move:
    # ''' '''
    # # TODO: Formalize how the world is oriented.
    # # There needs to be some sort of snapping to a grid,
    # # or initial establishing of axes
    # def __init__(self, configuration, pivot, clockwise):
        # pass

    # # # Usage: assert(validate_move_x(move)
    # # TODO: validate_move_geometry(...)?
    # # # TODO (eventually): validate_move_physics(...)?

# class Configuration:
    # ''' '''
    # def __init__(self):
        # self.blocks = []

class Block:
    ''' '''
    def __init__(self):
        # Unique identifier within a World
        self.ID = None
        # Surrounding blocks within a World
        # FORNOW assume this is what can be measured
        DUB = [-1, 0, 1] # discrete unit ball
        self.neighbors_dict = {(i, j, k) : None
                for i in DUB for j in DUB for k in DUB
                if i * j == 0 and j * k == 0 and k * i == 0
                and (i, j, k) != (0, 0, 0)}

    def __repr__(self):
        return 'b{}'.format(self.ID)

def main():
    w = World();
    for _ in xrange(4):
        b = Block()
        w.add(b)
    w.blocks[1].neighbors_dict[(1,0,0)] = w.blocks[0]
    pprint(w)

main()










































