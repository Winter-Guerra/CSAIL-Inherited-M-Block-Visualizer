# random testing of visualizer2D.py
# Originally: James Bern 7/25

from pprint import pprint

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
rotating_cubes = []


def verify_configuration():
    global config

    # connectivity condition
    connected = True
    for c1 in config: break
    comp_c1 = find_component(c1)
    for c2 in config:
        if c2 not in comp_c1:
            connected = False
            break

    # (1), (2), (3)
    rule_following = True
    for c0 in config:
        x, y = c0
        U = (0,1); D = (0,-1); R = (1,0); L = (-1,0);
        LR = (L,R); UD = (U,D);
        search_dict = {U:LR, D:LR, R:UD, L:UD}
        for (major, minors) in search_dict.iteritems():
                for minor in minors:
                    (M, m) = (major, minor)
                    # # derived cubes
                    # c5 c4 c3
                    # c0 c1 c2
                    c1 = (x+M[0],y+M[1])
                    c2 = (x+2*M[0],y+2*M[1])
                    c3 = (x+2*M[0]+m[0],y+2*M[1]+m[1])
                    c4 = (x+M[0]+m[0],y+M[1]+m[1])
                    c5 = (x+m[0],y+m[1])
                    # (1)
                    if (c1 not in config and c2 in config):
                        rule_following = False
                        break
                    # (2)
                    if (c1 not in config and c4 in config and
                            c5 not in config):
                        rule_following = False
                        break
                    # (3)
                    if (c1 not in config and c2 not in config and
                            c3 in config and c4 not in config and
                            c5 not in config):
                        rule_following = False
                        break


    if not connected:
        pprint(config)
        print("\nConfig is not connected.\n")
        exit(1)
    if not rule_following:
        pprint(config)
        print("\nConfig does not follow RULES.\n")
        exit(1)

    print("\nConfig verified!\n")


def find_extreme():
    global config
    My = max([c[1] for c in config])
    mx = max([c[0] for c in config if c[1] == My])
    return (mx, My)


def init_configuration():
    global config
    global config_size
    global extreme

    # grid system...
    config = set((0,0))
    for i in range(10):
        for j in range(10):
            config.update(set([(0+i,0+j),(1+i,0+j),(2+i,0+j),
                (3+i,0+j),(0+i,1+j),(3+i,1+j),
                (0+i,2+j),(3+i,2+j),(0+i,3+j),
                (1+i,3+j),(2+i,3+j),(3+i,3+j)]))

    config_size = len(config)
    extreme = find_extreme() # FORNOW: UR extreme



def rotate_clockwise(cube, virtual=False):
    # NOTE: Does not affect config
    # NOTE: virtual=True turns off the assert statements
    global config


    (x, y) = cube
    c1_c3_wrapped_coords = [((+1,0),(0,+1)),
                            ((0,+1),(-1,0)),
                            ((-1,0),(0,-1)),
                            ((0,-1),(+1,0))]
    for (c1, c3) in c1_c3_wrapped_coords:
        # # derived cubes
        #    c6 c7
        # c4 c3 c2
        # c5 c0 c1
        c2 = (c1[0]+c3[0], c1[1]+c3[1])
        c6 = (2*c3[0], 2*c3[1])
        c7 = (c1[0]+2*c3[0], c1[1]+2*c3[1])
        c5 = (-c1[0], -c1[1])
        c4 = (c3[0]-c1[0], c3[1]-c1[1])

        # inelegant translate
        c1 = (c1[0]+x, c1[1]+y)
        c2 = (c2[0]+x, c2[1]+y)
        c3 = (c3[0]+x, c3[1]+y)
        c4 = (c4[0]+x, c4[1]+y)
        c5 = (c5[0]+x, c5[1]+y)
        c6 = (c6[0]+x, c6[1]+y)
        c7 = (c7[0]+x, c7[1]+y)

        if virtual:
            assert cube not in config

        # Assuming c1 in config
        if c1 not in config:
            continue
        # assert c5 not in config
        if c3 in config:
            continue

        if c4 in config:
            if not virtual:
                assert c6 not in config and c7 not in config
            return c5
        elif c2 in config:
            if not virtual:
                assert c4 not in config and c5 not in config
            return c3
        else:
            # print map(lambda(x): x in config, (c1,c2,c3,c4,c5,c6,c7))
            # print ("c1: {}, c3: {}".format(c1, c3))
            # print
            if not virtual:
                assert (c4 not in config and c5 not in config and
                        c6 not in config and c7 not in config)
            return c2

    raise AssertionError


def find_neighbors(cube):
    global config
    x, y = cube
    neighbors = set([(x+i, y+j) for i in [-1,0,1] for j in [-1,0,1] if
            (x+i, y+j) in config and abs(i) + abs(j) == 1])
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


def path_search(cube_a, cube_b):
    '''
    return True iff there exists a path between cube_a
    and cube_b in configuration
    '''
    global config
    return cube_b in find_component(cube_a)


def update_configuration():
    global config
    global config_size
    global extreme
    global O_set, M_set, N_set, T_set

    # update O_set
    O_set = set()
    virtual_cube = (find_extreme()[0]+1, find_extreme()[1])
    starting_location = virtual_cube
    virtual_cube = rotate_clockwise(virtual_cube, virtual=True)
    while virtual_cube != starting_location:
        assert virtual_cube not in config
        O_set.update(find_neighbors(virtual_cube))
        virtual_cube = rotate_clockwise(virtual_cube, virtual=True)
    # FORNOW: convention, shows up in step_configuration
    # Basically, we don't want to look in the tail
    # for cubes to move
    O_set.discard(extreme)
    for cube_t in T_set:
        O_set.discard(cube_t)

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
    global rotating_cubes

    if not rotating_cubes:
        # Grab next cube_n
        # Pythonic for "if len(N_set) != 0"
        if N_set:
            rotating_cubes = [N_set.pop()]
            # unnecessary, but clarifies intent
            N_set.add(rotating_cubes[0])
        # Search for P for a 3 Cube Escape
        else:
            # axes
            P_found = False
            P_major = None # the three cubes lie along this axis
            P_minor = None # connects filled cubes to empty outer free space
            for cube_m in M_set:
                x, y = cube_m
                U = (0,1); D = (0,-1); R = (1,0); L = (-1,0)
                LR = (L,R); UD = (U,D);
                search_dict = {U:LR, D:LR, R:UD, L:UD}
                for (major, minors) in search_dict.iteritems():
                    for minor in minors:
                        broken = False
                        for i in xrange(3):
                            full = (x + i*major[0], y + i*major[1])
                            empty = (full[0] + minor[0], full[1] + minor[1])
                            if full not in config or empty in config:
                                broken = True
                        if not broken:
                            P_found = True
                            (P_major, P_minor) = (major, minor)
                            rotating_cubes = [cube_m,
                                    (cube_m[0] + major[0], cube_m[1] + major[1]),
                                    (cube_m[0] + 2*major[0], cube_m[1] + 2*major[1])]
                            return
            # No more moves exist
            if not P_found:
                for cube in config:
                    # horizontal line condition
                    if cube[1] != extreme[1]:
                        print "\nNo moves exist.\n"
                        pprint(config)
                        exit(1)
                print "\nI think we are done.\n"
                exit(0)

    else:
        # Standard tail relocation
        if len(rotating_cubes) == 1:
            cube_tr = rotating_cubes[0]
            # If not part of tail...
            if not (cube_tr[1] == extreme[1] and cube_tr[0] > extreme[0]):
                config.remove(cube_tr)
                cube_tr = rotate_clockwise(cube_tr)
                config.add(cube_tr)
                # FORNOW: so the two overall operations (tr/3ce) are paralell
                rotating_cubes = [cube_tr]
            else:
                T_set.add(cube_tr)
                rotating_cubes = []
        # 3 Cube Escape
        else:
            assert len(rotating_cubes) == 3
            moved_cube = False
            for i in range(3):
                cube_3ce = rotating_cubes[i]
                if cube_3ce[1] == extreme[1] and cube_3ce[0] > extreme[0]:
                    # sloppy, but whatever
                    T_set.add(cube_3ce)
                    continue
                else:
                    moved_cube = True
                    config.remove(cube_3ce)
                    cube_3ce = rotate_clockwise(cube_3ce)
                    config.add(cube_3ce)
                    # be sure to update rotating_cubes
                    rotating_cubes[i] = cube_3ce
                    break
            # If all three cubes part of tail...
            if not moved_cube:
                rotating_cubes = []


def run_test_case():
    global rotating_cubes
    global config

    init_configuration()
    verify_configuration()
    update_configuration()

    try:
        while True:
            step_configuration()
            if not rotating_cubes:
                update_configuration()
    except AssertionError:
        print "Oh dear!"
        pprint(config)

def main():
    run_test_case()

if __name__ == '__main__': main()

