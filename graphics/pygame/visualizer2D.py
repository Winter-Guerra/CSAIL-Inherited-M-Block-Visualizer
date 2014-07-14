import pygame
from pygame.locals import *
import itertools


# globals
screen = None
clock = None
config = []
config_size = -1
extreme = None
test_cube = None

# TODO: standardize variable names, config shouldn't
# be both a function argument and a global

def init_pygame():
    global screen
    global clock
    pygame.init()
    pygame.display.set_caption("visualizer2D.py")
    screen = pygame.display.set_mode([512,512])
    clock = pygame.time.Clock()

def find_extreme(config):
    My = max([c[1] for c in config])
    mx = max([c[0] for c in config if c[1] == My])
    return (mx, My)

def init_configuration():
    global config
    global config_size
    global extreme
    global test_cube
    config = set([(0,0),(0,1),(1,0),(2,0),(3,0),(3,1),(3,2),(3,3),(4,3),
        (0,2),(0,3),(0,4),(0,5),(0,6),(1,3),(1,4),(2,3),(2,4),(-1,0),(-2,0),
        (-3,0),(-3,1),(-3,2),(-3,3),(-2,3),(-1,3),
        (0,7),(0,8),(1,8),(2,8),(3,8)])
    config_size = len(config)


    # FORNOW: UR extreme
    extreme = find_extreme(config)

    # FORNOW: Move me
    test_cube = (4,3)


def rotate_clockwise(cube, config):
    # FORNOW: Does not affect config

    # TODO: this isn't the right assertion.
    # We need to know that a clockwise motion is possible
    #assert is_mobile(cube, config)
    (x, y) = cube
    wrapped_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                      ((x,y+1),(x-1,y),(x-1,y+1)),
                      ((x-1,y),(x,y-1),(x-1,y-1)),
                      ((x,y-1),(x+1,y),(x+1,y-1))]
    for (c_curr, c_next, c_corner) in wrapped_coords:
        if c_curr in config and c_next not in config:
            if c_corner in config:
                return c_next
            else:
                return c_corner
    raise Exception


def is_mobile(cube, config):
    # TODO: should this be general or assume the rules from
    # the algorithm?  Probably should be a general check
    # that there exists a valid move.

    # neighbors_condition
    all_neighbors = find_neighbors(cube, config)
    x_neighbors = [cube2 for cube2 in all_neighbors
            if cube2[1] == cube[1]]
    y_neighbors = [cube2 for cube2 in all_neighbors
            if cube2[0] == cube[0]]
    neighbors_condition = (len(all_neighbors) <= 2 and
            len(all_neighbors) > 0 and
            len(x_neighbors) <= 1 and
            len(y_neighbors) <= 1)

    # TODO: search for connectivity_condition
    connectivity_condition = True

    return neighbors_condition and connectivity_condition


def find_neighbors(cube, config):
    x, y = cube
    neighbors = [(x+i, y+j) for i in [-1,0,1] for j in [-1,0,1] if
            (x+i, y+j) in config and abs(i) + abs(j) == 1]
    return neighbors


def draw_configuration():
    global screen
    global extreme

    outer_boundary_cubes = set([extreme])
    virtual_cube = (extreme[0], extreme[1]+1)
    starting_location = virtual_cube

    virtual_cube = rotate_clockwise(virtual_cube, config)
    while virtual_cube != starting_location:
        outer_boundary_cubes.update(find_neighbors(virtual_cube,config))
        virtual_cube = rotate_clockwise(virtual_cube, config)

    def draw_cube(cube):
        DEFAULT = (170,240,209)
        BOUNDARY = (183,132,167)
        EXTREME = (255,159,0)

        c = screen.get_size()[0]/24
        N = screen.get_size()[0]/c/2;
        (x, y) = (cube[0]+N, cube[1]+N)

        # color cubes
        color = DEFAULT
        if cube == extreme:
            color = EXTREME
        elif cube in outer_boundary_cubes:
            color = BOUNDARY
        pygame.draw.rect(screen, color, [x*c, screen.get_size()[1]-c-y*c, c, c])

    for cube in config:
        draw_cube(cube)


def step_configuration():
    global config
    global config_size
    global extreme
    global test_cube
    
    config.remove(test_cube)
    # TODO: should rotations affect the configuration?
    # Probably not, because we use rotations for testing, etc.
    test_cube = rotate_clockwise(test_cube, config)
    config.add(test_cube)

    # update extreme cube
    extreme = find_extreme(config)
    
    # check that we haven't done anything crazy
    assert len(config) == config_size


def main():
    init_pygame()
    # initialize the configuration
    init_configuration()

    while True:
        clock.tick(5)

        # key handling
        for event in pygame.event.get():
            if (event.type == QUIT or
                    (event.type == KEYDOWN and event.key == K_q)):
                pygame.quit()
                exit()
        # black out screen
        screen.fill((0,0,0))

        # deal with config
        draw_configuration()
        step_configuration()

        # flip display
        pygame.display.flip()


if __name__ == '__main__': main()

