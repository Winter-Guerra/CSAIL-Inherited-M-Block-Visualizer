# 2D pygame visualization of 2D reconfiguration algorithm
# for squares.
# James Bern 7/15

import pygame
from pygame.locals import *
import os # environ

# globals
screen = None
clock = None
config = set()
config_size = -1
extreme = None
O_set = set()
M_set = set()
N_set = set()
T_set = set()
rotating_cube = None

# TODO: (now) standardize variable names, config shouldn't
# be both a function argument and a global
# TODO: make global names match names from paper

def init_pygame():
    global screen
    global clock
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(2500,100)
    pygame.init()
    pygame.display.set_caption("visualizer2D.py")
    screen = pygame.display.set_mode([512,512])
    clock = pygame.time.Clock()


def find_extreme():
    global config
    My = max([c[1] for c in config])
    mx = max([c[0] for c in config if c[1] == My])
    return (mx, My)


def verify_configuration():
    # Check rules 1, 2, 3 and output that the pass
    pass


def init_configuration():
    global config
    global config_size
    global extreme
    config = set([(0,0),(0,1),(1,0),(2,0),(3,0),(3,1),(3,2),(3,3),(4,3),
        (0,2),(0,3),(0,4),(0,5),(0,6),(1,3),(1,4),(2,3),(2,4),(-1,0),(-2,0),
        (-3,0),(-3,1),(-3,2),(-3,3),(-2,3),(-1,3),
        (0,7),(0,8),(1,8),(2,8),(3,8)])#,(2,-1),(2,-2),(2,-3),(2,-4),(2,-5),
        #(3,-4),(4,-4),(5,-4)])
    config_size = len(config)


    # FORNOW: UR extreme
    extreme = find_extreme()


def rotate_clockwise(cube):
    # NOTE: Does not affect config
    global config

    # TODO: Build transfers into the model
    # TODO: Build checks into the model

    (x, y) = cube
    clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                             ((x,y+1),(x-1,y),(x-1,y+1)),
                             ((x-1,y),(x,y-1),(x-1,y-1)),
                             ((x,y-1),(x+1,y),(x+1,y-1))]
    for (c_curr, c_next, c_corner) in clockwise_2box_coords:
        if c_curr in config and c_next not in config:
            if c_corner in config:
                # TODO: assert
                return c_next
            else:
                # TODO: assert
                return c_corner
    raise Exception



    # TODO: search for connectivity_condition
    connectivity_condition = True

    return neighbors_condition and connectivity_condition


def find_neighbors(cube):
    global config
    x, y = cube
    neighbors = set([(x+i, y+j) for i in [-1,0,1] for j in [-1,0,1] if
            (x+i, y+j) in config and abs(i) + abs(j) == 1])
    return neighbors


def path_search(cube_a, cube_b):
    '''
    return True iff there exists a path between cube_a
    and cube_b in configuration
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

    return cube_b in marked_cubes


def update_configuration():
    global config
    global config_size
    global extreme
    global O_set, M_set, N_set, T_set

    # # FORNOW: update extreme cube
    # extreme = find_extreme()

    # update O_set
    O_set = set()
    # NOTE: at intermediate steps the cube extreme may
    # not actually be the extremal cube, so use find_extreme().
    virtual_cube = (find_extreme()[0], find_extreme()[1]+1)
    starting_location = virtual_cube
    virtual_cube = rotate_clockwise(virtual_cube)
    while virtual_cube != starting_location:
        O_set.update(find_neighbors(virtual_cube))
        virtual_cube = rotate_clockwise(virtual_cube)
    # FORNOW: convention, shows up in step_configuration
    # Basically, we don't want to look in the tail
    # for cubes to move
    O_set.remove(extreme)
    for cube_t in T_set:
        O_set.remove(cube_t)

    # update M_set
    M_set = set()
    for cube in O_set:
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
            connectivity_condition = path_search(cube_a, cube_b)
            config.add(cube)

        if neighbors_condition and connectivity_condition:
            M_set.add(cube)

    # update N_set
    N_set = set()
    for cube in M_set:
        non_splitting = True
        x, y = cube

        clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                                 ((x,y+1),(x-1,y),(x-1,y+1)),
                                 ((x-1,y),(x,y-1),(x-1,y-1)),
                                 ((x,y-1),(x+1,y),(x+1,y-1))]
        for (c_curr, c_next, c_corner) in clockwise_2box_coords:
            if (c_curr in config and c_next in config
                    and c_corner not in config):
                non_splitting = False

        if non_splitting:
            N_set.add(cube)

    # check that we haven't done anything crazy
    assert len(config) == config_size


def step_configuration():
    global config
    global extreme
    global O_set, M_set, N_set, T_set
    global rotating_cube

    if rotating_cube == None:
        # Grab next cube_n
        # Pythonic for "if len(N_set) != 0"
        if N_set:
            rotating_cube = N_set.pop()
            # unnecessary, but clarifies intent
            N_set.add(rotating_cube)
        # Search for P for a 3 Cube Escape
        else:
            # axes
            P_major = None # the three cubes lie along this axis
            P_minor = None # connects filled cubes to empty outer free space
            for cube_m in M_set:
                x, y = cube_m
                U = (0,1); D = (0,-1); R = (1,0); L = (-1,0)
                LR = (L,R); UD = (U,D);
                search_dict = {U:LR, D:LR, R:UD, L:UD}
                for (major, minors) in search_dict.iteritems():
                    for minor in minors:
                        P_found = True
                        for i in xrange(3):
                            full = (x + i*major[0], y + i*major[1])
                            empty = (full[0] + minor[0], full[1] + minor[1])
                            if full not in config or empty in config:
                                P_found = False
                        if P_found:
                            (P_major, P_minor) = (major, minor)
                            rotating_cube = [cube_m,
                                    (cube_m[0] + major[0], cube_m[1] + major[1]),
                                    (cube_m[0] + 2*major[0], cube_m[1] + 2*major[1])]


    else:
        # Standard tail relocation
        if type(rotating_cube[0]) is int:
            # If not part of tail...
            if not (rotating_cube[1] == extreme[1] and rotating_cube[0] > extreme[0]):
                config.remove(rotating_cube)
                rotating_cube = rotate_clockwise(rotating_cube)
                config.add(rotating_cube)
            else:
                T_set.add(rotating_cube)
                rotating_cube = None
        # 3 Cube Escape
        else:
            assert type(rotating_cube[0]) is tuple
            moved_cube = False
            for i in range(3):
                cube_3ce = rotating_cube[i]
                if cube_3ce[1] == extreme[1] and cube_3ce[0] > extreme[0]:
                    # sloppy, but whatever
                    T_set.add(cube_3ce)
                    continue
                else:
                    moved_cube = True
                    config.remove(cube_3ce)
                    cube_3ce = rotate_clockwise(cube_3ce)
                    config.add(cube_3ce)
                    # be sure to update rotating_cube
                    rotating_cube[i] = cube_3ce
                    break
            # If all three cubes part of tail...
            if not moved_cube:
                rotating_cube = None



def draw_configuration():
    global config
    global screen
    global extreme
    global O_set, M_set, N_set, T_set

    screen.fill((0,0,0))

    def draw_cube(cube, color):
        c = screen.get_size()[0]/24
        N = screen.get_size()[0]/c/2;
        (x, y) = (cube[0]+N, cube[1]+N)
        pygame.draw.rect(screen, color, [x*c, screen.get_size()[1]-c-y*c, c, c])

    DEFAULT = (153,102,204)
    BOUNDARY = (222,93,131)
    EXTREME = (255,159,0)
    MOBILE = (133,187,101)
    MOBILE_NON_SPLITTING = (0,255,0)

    # NOTE: precendence order
    for cube in config:
        color = DEFAULT
        if cube == extreme or cube in T_set:
            color = EXTREME
        elif cube in N_set:
            color = MOBILE_NON_SPLITTING
        elif cube in M_set:
            color = MOBILE
        elif cube in O_set:
            color = BOUNDARY
        draw_cube(cube, color)

    pygame.display.flip()


def main():
    init_pygame()
    # initialize the configuration
    init_configuration()
    update_configuration()

    while True:
        clock.tick(5)
        # key handling
        for event in pygame.event.get():
            if (event.type == QUIT or
                    (event.type == KEYDOWN and event.key == K_q)):
                pygame.quit()
                exit()

        # NOTE: step_configuration also calls draw_configuration, but whatever
        step_configuration()
        update_configuration()
        draw_configuration()



if __name__ == '__main__': main()

