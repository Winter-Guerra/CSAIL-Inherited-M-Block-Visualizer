# parallel variant of 2D algorithm
# Adapted from: visualizer2D.py
# Originally: James Bern 8/19

import pygame
from pygame.locals import *
from pprint import pprint
import os # en
import pickle # loading configs
import sys

# globals
screen = None
clock = None
config = set()
config_size = -1
extreme = None
O_lst = []
M_lst = []
N_lst = []
P4_lst = [] # lst of instances of P4
T_set = set()

running_cubes = set() # set of cubes currently being run across the outer bdry.
first_find = None
next_cube = None      # the next cube to add to running_cubes
next_P4 = None        # the next instance of P4 to add to running_cubes
BUFF = 2
buff_timer = BUFF     # how long to wait upon conclusion of next_cube
                      # # or next_P4 addition before adding next cube

# globals used when running a split
# split_mode is activated to let us know we're in the middle of a split
# split_checkpoint is the location that must be passed
# split_counter tracks the number of cubes from P4 to pass it.
# # split_waiting means that a cube is on its way to the checkpoint
split_mode = False
split_checkpoint = None
split_counter = None
# split_waiting = False

# flags
light_variant = False
# w/ imagemagick: convert -delay 2 frame*.png -reverse name.gif
dump_png = False

occ_dict = {}


# Helper functions for basic vector operations on tuples
def add_t(a, b):
    '''
    a + b componentwise
    '''
    assert type(a) is tuple
    assert type(b) is tuple
    return tuple(a_i + b_i for (a_i, b_i) in zip(a,b))

def sub_t(a, b):
    '''
    a - b componentwise
    '''
    assert type(a) is tuple
    assert type(b) is tuple
    return tuple(a_i - b_i for (a_i, b_i) in zip(a,b))

def sca_t(a, c):
    '''
    c*a
    '''
    assert type(a) is tuple
    return tuple(c*a_i for a_i in a)


#
def init_pygame():
    global screen
    global clock
    #os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(2500,100)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(25,25)
    pygame.init()
    pygame.display.set_caption("visualizer2D.py")
    screen = pygame.display.set_mode([235*2,85*2])
    # screen = pygame.display.set_mode([140*8,50*4])
    clock = pygame.time.Clock()


def find_extreme():
    global config
    Mx = max([c[0] for c in config])
    My = max([c[1] for c in config if c[0] == Mx])
    return (Mx, My)


def verify_configuration():
    global config
    raise NotImplementedError

    # connectivity condition
    for c1 in config: break
    comp_c1 = find_component(c1)
    for c2 in config:
        assert c2 in comp_c1

    # (1), (2), (3)
    # (A), (B), (B)
    for c0 in config:
        # x, y = c0
        U = (0,1); D = (0,-1); R = (1,0); L = (-1,0);
        LR = (L,R); UD = (U,D);
        search_dict = {U:LR, D:LR, R:UD, L:UD}
        for (major, minors) in search_dict.iteritems():
                for minor in minors:
                    (M, m) = (major, minor)
                    # # derived cubes
                    #
                    # ^
                    # |
                    # m
                    #
                    # cf ce cd cc
                    # c5 c4 c3 cb
                    # c0 c1 c2 ca  M->
                    c1 = (x+M[0],y+M[1]) #add_t(c0, M)
                    c2 = (x+2*M[0],y+2*M[1])
                    c3 = (x+2*M[0]+m[0],y+2*M[1]+m[1])
                    c4 = (x+M[0]+m[0],y+M[1]+m[1])
                    c5 = (x+m[0],y+m[1])
                    # (1)
                    assert not (c1 not in config and c2 in config)
                    # (2)
                    assert (not (c1 not in config and c4 in config and
                        c5 not in config))
                    # (3)
                    assert (not (c1 not in config and c2 not in config
                        and c3 in config and c4 not in config and
                        c5 not in config))

    # print("\nConfig verified!\n")


def init_configuration(init_config=None, random=False):
    global config
    global config_size
    global extreme

    # Load config from file
    if init_config != None:
        MX = min([tup[0] for tup in init_config])
        MY = max([tup[1] for tup in init_config])
        config = set((tup[0]-MX,MY-tup[1]) for tup in init_config)
        pprint(config)
        pass

    # Generate random config
    elif random:
        pass

    else:
        config = set([(0,0),(1,0)])

    # always need to run these
    config_size = len(config)
    extreme = find_extreme() # FORNOW: UR extreme



def rotate_clockwise(cube, virtual=False):
    # NOTE: Does not affect config
    # NOTE: virtual=True turns off the assert statements
    global config

    c0 = cube
    c1_c3_wrapped_coords = [((+1,0),(0,+1)),
                            ((0,+1),(-1,0)),
                            ((-1,0),(0,-1)),
                            ((0,-1),(+1,0))]
    for (i, j) in c1_c3_wrapped_coords:
        # # derived cubes
        #    ^
        #    |
        #    j
        #
        #    c6 c7
        # c4 c3 c2
        # c5 c0 c1  i ->
        d1 = i
        d3 = j
        d2 = add_t(i, j)            #(c1[0]+c3[0], c1[1]+c3[1])
        d6 = sca_t(j, 2)             #(2*c3[0], 2*c3[1])
        d7 = add_t(i, sca_t(j, 2))  #(c1[0]+2*c3[0], c1[1]+2*c3[1])
        d5 = sca_t(i, -1)            #(-c1[0], -c1[1])
        d4 = add_t(j, sca_t(i, -1)) #(c3[0]-c1[0], c3[1]-c1[1])

        # inelegant translate
        c1,c2,c3,c4,c5,c6,c7 = map(lambda di: (add_t(c0, di)),
                (d1,d2,d3,d4,d5,d6,d7))

        if virtual:
            assert cube not in config

        # # We use c1 as our pivot (fine since such a pivot must exist), so
        # (assumption) => c1 in config
        if c1 not in config:
            continue
        # (assumption) => c3 not in config
        if c3 in config:
            continue
        # => c5 not in config
        assert c5 not in config

        # Transfer Move
        if c4 in config:
            if not virtual:
                assert c6 not in config and c7 not in config
            return c5

        # Linear Move
        elif c2 in config:
            if not virtual:
                assert c4 not in config and c5 not in config
            return c3

        # Corner Move
        else:
            # print map(lambda(x): x in config, (c1,c2,c3,c4,c5,c6,c7))
            # print ("c1: {}, c3: {}".format(c1, c3))
            # print
            if not virtual:
                assert (c4 not in config and c5 not in config and
                        c6 not in config and c7 not in config)
            return c2

    exit("Error: No valid move found!")


def find_neighbors(cube):
    '''
    return a list of neighbors, in clockwise order if possible.
    e.g. for - y -
             - c x
             - - -
    the returned list should be [x, y]
    '''
    global config
    x, y = cube
    neighbors = [(x+i, y+j) for i in [-1,0,1] for j in [-1,0,1] if
            (x+i, y+j) in config and abs(i) + abs(j) == 1]

    # FORNOW: this is a hack
    if len(neighbors) == 2:
        clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                                 ((x,y+1),(x-1,y),(x-1,y+1)),
                                 ((x-1,y),(x,y-1),(x-1,y-1)),
                                 ((x,y-1),(x+1,y),(x+1,y-1))]
        for (c_curr, c_next, _) in clockwise_2box_coords:
            if (c_curr in config and c_next in config):
                return [c_curr, c_next]

    return neighbors


def find_component(cube_a):
    '''
    return the component cube_a is part of as a set
    '''
    global config
    # Run a simple breadth-first search
    marked_cubes = set([cube_a])
    prev_cubes = set([cube_a])
    next_cubes = set()
    old_len = -1
    while len(marked_cubes) != old_len:
        old_len = len(marked_cubes)
        for cube in prev_cubes:
            next_cubes.update(find_neighbors(cube))
        marked_cubes.update(next_cubes)
        prev_cubes = next_cubes.copy()
    return marked_cubes


def exists_path(cube_a, cube_b):
    '''
    return True iff there exists a path between cube_a
    and cube_b in configuration
    '''
    global config
    return cube_b in find_component(cube_a)


def P4_search(m1):
    '''
    return instance of P4 if m1 is such,
    otherwise return None
    assumes m1 splitting cube.
    '''
    global config

    P_major = None # the three cubes lie along this axis
    P_minor = None # connects filled cubes to empty outer free space
    x, y = m1

    U = (0,1); D = (0,-1); R = (1,0); L = (-1,0)
    LR = (L,R); UD = (U,D);
    search_dict = {U:LR, D:LR, R:UD, L:UD}

    for (major, minors) in search_dict.iteritems():
        for minor in minors:
            broken = False
            for i in xrange(4):
                full = (x + i*major[0], y + i*major[1])
                empty = (full[0] + minor[0], full[1] + minor[1])
                if full not in config or empty in config:
                    broken = True
            if not broken:
                (P_major, P_minor) = (major, minor)
                P4 = [m1,
                     (m1[0] +   major[0], m1[1] +   major[1]),
                     (m1[0] + 2*major[0], m1[1] + 2*major[1]),
                     (m1[0] + 3*major[0], m1[1] + 3*major[1])]
                return P4
    return None


def classify_configuration():
    global config
    global config_size
    global extreme
    global O_lst, M_lst, N_lst, T_set, P4_lst
    global next_cube
    global next_P4
    global buff_timer

    # calculate O_lst
    O_lst = []
    virtual_cube = (find_extreme()[0]+1, find_extreme()[1])
    starting_location = virtual_cube
    virtual_cube = rotate_clockwise(virtual_cube, virtual=True)

    # TODO: implement clockwise look ahead neighbors
    # FORNOW: hacked into find_neighbors
    while virtual_cube != starting_location:
        assert virtual_cube not in config
        for neighbor in find_neighbors(virtual_cube):
            if neighbor not in O_lst:
                O_lst.append(neighbor)
        virtual_cube = rotate_clockwise(virtual_cube, virtual=True)
    # FORNOW: convention, shows up in step_configuration
    # Basically, we don't want to look in the tail
    # for cubes to move
    if extreme in O_lst:
        O_lst.remove(extreme)
    for cube_t in T_set:
        if cube_t in O_lst:
            O_lst.remove(cube_t)

    # FORNOW: reverse for algorithm
    O_lst.reverse()

    # calculate M_lst
    M_lst = []
    for cube in O_lst:
        neighbors_condition = False
        connectivity_condition = False

        # neighbors_condition: enforce any one neighbor,
        # or two neighbors sharing a corner
        # NOTE: greater than zero neighbors is the job
        # of verify_configuration
        cube_neighbors = find_neighbors(cube)
        num_neighbors = len(cube_neighbors)
        num_x_neighbors = len([cube2 for cube2 in cube_neighbors
                if cube2[1] == cube[1]])
        num_y_neighbors = len([cube2 for cube2 in cube_neighbors
                if cube2[0] == cube[0]])
        if num_x_neighbors <= 1 and num_y_neighbors <= 1:
            neighbors_condition = True

        # connectivity_condition:
        # if one neighbor: True
        # if two neighbors: ensure there exists a path connecting the neighbors
        # but not containing the cube under examination
        if num_neighbors == 1:
            connectivity_condition = True
        elif num_neighbors == 2 and neighbors_condition:
            config.remove(cube)
            cube_a = cube_neighbors.pop()
            cube_b = cube_neighbors.pop()
            # restore cube_neighbors to keep things clean
            cube_neighbors = find_neighbors(cube)
            connectivity_condition = exists_path(cube_a, cube_b)
            config.add(cube)

        if neighbors_condition and connectivity_condition:
            M_lst.append(cube)

    # calculate N_lst, P4_lst
    # and FORNOW: pick next cubes to rotate if we have to
    N_lst = []
    P4_lst = []
    for cube in M_lst:
        splitting = False

        x, y = cube
        clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                                 ((x,y+1),(x-1,y),(x-1,y+1)),
                                 ((x-1,y),(x,y-1),(x-1,y-1)),
                                 ((x,y-1),(x+1,y),(x+1,y-1))]
        for (c_curr, c_next, c_corner) in clockwise_2box_coords:
            if (c_curr in config and c_next in config
                    and c_corner not in config):
                splitting = True

        # FORNOW: sloppy in so many ways
        if not splitting:
            N_lst.append(cube)

            if next_cube == None and next_P4 == None:
                buff_timer = BUFF
                next_cube = cube

        else:
            search_results = P4_search(cube)
            if search_results != None:
                P4 = search_results
                P4_lst.append(P4)

                if next_cube == None and next_P4 == None:
                    buff_timer = BUFF
                    next_P4 = P4

    # check that we haven't done anything crazy
    # NOTE: modified assertion
    assert len(config) + len(running_cubes) == config_size


def step_configuration():
    global config
    global extreme
    global O_lst, M_lst, N_lst, T_set
    # global rotating_cubes
    global running_cubes
    global next_cube
    global next_P4
    global buff_timer
    global split_mode
    global split_checkpoint
    global split_counter

    if next_cube == None and next_P4 == None:
        # TODO: DRY, strip out, c'mon son.
        if running_cubes:
            next_running_cubes = set()
            for cube_r in running_cubes:
                # Still running...
                if not (cube_r[1] == extreme[1] and cube_r[0] > extreme[0]):
                    cube_r = rotate_clockwise(cube_r)
                    next_running_cubes.add(cube_r)
                # Made it to the tail.
                else:
                    config.add(cube_r)
                    T_set.add(cube_r)
                    # do _not_ add to next_running_cubes
            running_cubes = next_running_cubes
            return
        else:
            exit("We made it.")

    # Stage next_cube or next_P4 to run (if buff timer expended)
    # Wait on/decrement timer
    if buff_timer > 0:
        buff_timer -= 1
    else:
        # # Stage cubes
        # Standard tail relocation
        if next_cube != None:
            assert next_cube in config
            running_cubes.add(next_cube)
            config.remove(next_cube)
            next_cube = None
        else:
            # Issue here is that splits can be "facing"
            # either direction, so flushing is kind of non-trivial.
            # Approach is to run m1 for BUFF and then record its location
            # as the split_checkpoint.
            # (can run virtually)
            # a counter will be maintained of how many cubes have passed
            # this checkpoint, and once it reaches 4 we can just set
            # next_P4 to None and exit split_mode.
            if not split_mode:
                # # prepare splitting fields (heh.)
                split_mode = True
                split_checkpoint = None
                split_counter = 0
                # split_waiting = False

                # calculate split_checkpoint
                m1 = next_P4[0]
                shell = m1
                # TODO: cases, formalize
                # FORNOW: very loose bound
                for _ in xrange(BUFF+3):
                    shell = rotate_clockwise(shell)
                split_checkpoint = shell

                # start the first cube
                config.remove(m1)
                running_cubes.add(m1)
                # split_waiting = True

        # split loop
        if split_mode:
            # NOTE: won't be in config
            # TODO: problem here is that we need the cube from
            # P4 to be at the checkpoint, not just any cube
            # hacky sol'n is to book keep each one of the cubes from P4's motion 
            # by updating next_P4
            if split_checkpoint in running_cubes and split_checkpoint in next_P4:

                split_counter += 1

                if split_counter == 4:
                    split_mode = False
                    next_P4 = None
                else:
                    m_i = next_P4[split_counter]
                    config.remove(m_i)
                    running_cubes.add(m_i)

    # run the cubes
    next_running_cubes = set()
    for cube_r in running_cubes:
        # Still running...
        if not (cube_r[1] == extreme[1] and cube_r[0] > extreme[0]):
            cube_r = rotate_clockwise(cube_r)
            next_running_cubes.add(cube_r)
        # Made it to the tail.
        else:
            config.add(cube_r)
            T_set.add(cube_r)
            # do _not_ add to next_running_cubes
    running_cubes = next_running_cubes

    # FORNOW bookkeep next_P4
    if split_mode:
        for i in range(split_counter + 1):
            if not (next_P4[i][1] == extreme[1] and next_P4[i][0] > extreme[0]):
                next_P4[i] = rotate_clockwise(next_P4[i])


def occ_dict_add(cell, d_tup=None, full=None):
    ''' Call this function: does adding and checking '''

    global occ_dict

    # # # perform checks

    if cell in occ_dict:
        assert occ_dict[cell] != "FULL"

    # # full cell analysis
    if full:
        assert d_tup == None
        assert cell not in occ_dict
        occ_dict[cell] = "FULL"
        return

    # # circle sector analysis
    assert d_tup != None

    # collision detection
    if cell in occ_dict:
        for e_tup in occ_dict[cell]:
            # same edge
            assert e_tup[0] != d_tup[0]
            # perpendicular edges (one vert one horz)
            if abs(d_tup[0][0]) + abs(e_tup[0][0]) == 1:
                # NOTE: must both be pointing away from shared vertex
                # TODO: picture explaining this,
                # it's subtle.
                assert sum(e_tup[1]) == sum(d_tup[0])
                assert sum(e_tup[0]) == sum(d_tup[1])
            # NOTE: parallel disjoint edges never a problem

    # actually perform addition
    if cell not in occ_dict:
        occ_dict[cell] = [d_tup]
    else:
        occ_dict[cell].append(d_tup)


def detect_collisions():
    '''
    Run collision detection of all cubes in running_cubes.
    '''
    global config
    global occ_dict

    # dictionary detailing which cells will be occupied (and how)
    # during the next lockstep rotation
    occ_dict = {}

    # d_tuple (direction_tuple) =
    # (broken edge as vector, vector pointing from less to more occupied sides)
    #      1 2    1 2
    # e.g. a x -> x a  (a rotating over blocks marked 0.)
    #      0 0    0 0
    # 1 = (U=(0,1), R=(1,0)) (swoop goes up to the right)
    # 2 = (U=(0,1), L=(-1,0)) (swoop goes up to the left)


    # calls to occ_dict_add
    for cube in running_cubes:

        # add in intermediate occ's
        # # FORNOW: hacked out of rotate_clockwise code
        #
        c0 = cube
        occ_dict_add(c0, full=True)

        c1_c3_wrapped_coords = [((+1,0),(0,+1)),
                                ((0,+1),(-1,0)),
                                ((-1,0),(0,-1)),
                                ((0,-1),(+1,0))]
        for (i, j) in c1_c3_wrapped_coords:
            # # derived cubes
            #    ^
            #    |
            #    j
            #
            #    c6 c7
            # c4 c3 c2
            # c5 c0 c1  i ->
            # ca cb 
            d1 = i
            d3 = j
            d2 = add_t(i, j)            #(c1[0]+c3[0], c1[1]+c3[1])
            d6 = sca_t(j, 2)             #(2*c3[0], 2*c3[1])
            d7 = add_t(i, sca_t(j, 2))  #(c1[0]+2*c3[0], c1[1]+2*c3[1])
            d5 = sca_t(i, -1)            #(-c1[0], -c1[1])
            d4 = add_t(j, sca_t(i, -1)) #(c3[0]-c1[0], c3[1]-c1[1])
            da = add_t(sca_t(i, -1), sca_t(j, -1))
            db = sca_t(j, -1)

            # inelegant translate
            c1,c2,c3,c4,c5,c6,c7 = map(lambda di: (add_t(c0, di)),
                    (d1,d2,d3,d4,d5,d6,d7))
            ca,cb = map(lambda di: (add_t(c0, di)), (da,db))

            if c1 not in config: continue
            if c3 in config: continue
            assert c5 not in config

            # Transfer Move c0 -> c5
            if c4 in config:
                assert c6 not in config and c7 not in config
                # # j face
                # -i bias
                occ_dict_add(cb, d_tup=(j, sca_t(i, -1)))
                # +i bias
                occ_dict_add(ca, d_tup=(j, i))

                occ_dict_add(c5, full=True)
                break

            # Linear Move c0 -> c3
            elif c2 in config:
                assert c4 not in config and c5 not in config
                # # -i face
                # +j bias
                occ_dict_add(c5, d_tup=(sca_t(i, -1), j))
                # -j bias
                occ_dict_add(c4, d_tup=(sca_t(i, -1), sca_t(j, -1)))

                occ_dict_add(c3, full=True)
                break

            # Corner Move c0 -> c2
            else:
                assert (c4 not in config and c5 not in config and
                        c6 not in config and c7 not in config)
                # copied from Linear Move
                occ_dict_add(c5, d_tup=(sca_t(i, -1), j))
                occ_dict_add(c4, d_tup=(sca_t(i, -1), sca_t(j, -1)))
                # # -j face
                # +i bias
                occ_dict_add(c6, d_tup=(sca_t(j, -1), i))
                # -i bias
                occ_dict_add(c7, d_tup=(sca_t(j, -1), sca_t(i, -1)))

                occ_dict_add(c2, full=True)
                break


def draw_cube(cube, color):
    c = 4
    N = 1
    (x, y) = (cube[0]+N, cube[1]+N)
    pygame.draw.rect(screen, color, [x*c, screen.get_size()[1]-c-y*c, c, c])


def draw_configuration(frozen=False):
    global config
    global screen
    global extreme
    global O_lst, M_lst, N_lst, T_set
    global P4_lst
    global rotating_cubes
    global light_variant

    f = 1
    if light_variant:
        f = 2

    DEFAULT = (153,102,204)
    BOUNDARY = (0,191,255)
    EXTREME = (255/f,159/f,0/f)
    MOBILE = (133,187,101)
    MOBILE_NON_SPLITTING = (0,255,0)
    ROTATING = (255/f,85/f,163/f)
    P4_HIGHLIGHT = (255,255,0)
    P4 = (155,155,0)
    FROZEN = (100/f,100/f,100/f)
    WHITE = (255,255,255)
    BLACK = (0,0,0)

    if light_variant:
        screen.fill(WHITE)
    else:
        screen.fill(BLACK)

    # NOTE: precendence order
    for cube in config.union(running_cubes):
        color = DEFAULT

        if cube in [tup[0] for tup in P4_lst]:
            color = P4_HIGHLIGHT
        elif cube in [elem for tup in P4_lst for elem in tup]:
            color = P4
        elif cube in N_lst:
            color = MOBILE_NON_SPLITTING
        elif cube in M_lst:
            color = MOBILE
        elif cube in O_lst:
            color = BOUNDARY

        if cube in running_cubes:
            color = ROTATING
        elif cube in T_set or cube == extreme:
            color = EXTREME
        elif frozen:
            color = FROZEN

        draw_cube(cube, color)

    pygame.display.flip()


def main():
    global running_cubes
    global dump_png
    global split_mode

    input_config = None
    # process cmd line arg's
    if len(sys.argv) == 1:
        pass
    else:
        assert len(sys.argv) == 2
        arg = sys.argv[1]
        try:
            g = open(arg, 'r')
            input_config = pickle.load(g)
        except IOError:
            print "config file not found."

    init_pygame()
    # initialize the configuration
    init_configuration(init_config=input_config, random=False)
    # verify_configuration()
    classify_configuration()
    draw_configuration()
    pygame.time.wait(1000)

    # visualization options
    draw_moves = True
    draw_rotations = True

    # ghetto padding for powerpoint
    frame_i = -1
    # for _ in xrange(200):
        # frame_i += 1
        # pad = '0'*(4-len(str(frame_i)))
        # pygame.image.save(pygame.display.get_surface(), 'frame' + pad + str(frame_i) + '.png')

    while True:
        # FORNOW: frame_i only used by dump_png
        frame_i += 1
        # key handling
        for event in pygame.event.get():
            if (event.type == QUIT or
                    (event.type == KEYDOWN and event.key == K_q)):
                pygame.quit()
                exit()

        step_configuration()
        pygame.time.wait(50)
        # FORNOW
        if not split_mode and buff_timer == 0:
            classify_configuration()

        if draw_moves:
            draw_configuration(frozen=False)
            pygame.display.flip()
            # pygame.time.wait(1000)
        else:
            if draw_rotations:
                draw_configuration(frozen=True)

        detect_collisions()

        if dump_png:
            pad = '0'*(4-len(str(frame_i)))
            pygame.image.save(pygame.display.get_surface(), 'frame' + pad + str(frame_i) + '.png')
        print frame_i,



if __name__ == '__main__': main()

