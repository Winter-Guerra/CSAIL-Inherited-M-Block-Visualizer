# Test of a simple visualizer for the M-Blocks
# Uses PyOpenGL, (and GLUT)
# TODO: FORNOW: TODO: Uses pygame for 
# NOTE: Hacked together from one of my graphics assignments.
# Originally James Bern 6/26/2014

from OpenGL.GL import *
# from OpenGL.GLU import *
from OpenGL.GLUT import *

# import sys # argv
# import itertools # cycle
# import random # random
# import numpy as np # matrix
# import numpy.linalg as la # pinv svd
from pprint import pprint, pformat
# import pygame

# Some globals
robot = None
# drawing_mode = 0
spin = False
# Camera globals
R_cumm = None
T_cumm = None
# 
left = False
middle = False
shiftmiddle = False
right = False
shift = False
# 
last_motion = (0, 0)
last_coords = None
# 
t = 0
#
# texture_dict

class Robot():
    ''' '''
    def __init__(self):
        self.cube_positions = [(0,0,0), (1,0,0), (0,0,1), (0,1,0), (3,2,0)]
        eps = 0.001
        self.color_pallete = [[i,j,k,1.0]
                for i in [0.0,1.0]
                for j in [0.0,1.0]
                for k in [0.0,1.0]
                if i*j>eps or j*k>eps or k*i>eps]
        pprint(self.color_pallete)
    def __repr__(self):
        return ''

    def step(self):
        pass

    def draw(self):
        ''' '''
        glMatrixMode(GL_MODELVIEW)
        for i in range(len(self.cube_positions)):
            make_cube(xyz=self.cube_positions[i],
                    color=self.color_pallete[i % len(self.color_pallete)])

def initCumm():
    global R_cumm
    global T_cumm
    glLoadIdentity()
    # Rotate us into a nice view.
    glRotate(-45, 0, 1, 0)
    R_cumm = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()
    # Drag us into frame.
    glTranslatef(0, 0, -10)
    T_cumm = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()


def keyfunc(key, x, y):
    # global drawing_mode
    global spin
    glutPostRedisplay()
    if key == chr(27) or key == 'q' or key == 'Q':
        exit(0)
    # elif key == 'm' or key == 'M':
        # drawing_mode += 1
        # drawing_mode %= 3
    elif key == 'r' or key == 'R':
        spin = not spin


def mousefunc(button, state, x, y):
    global left
    global middle
    global shiftmiddle
    global right
    global last_coords
    global last_motion
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            left = True
        elif state == GLUT_UP:
            left = False
    elif button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            if glutGetModifiers() == GLUT_ACTIVE_SHIFT:
                shiftmiddle = True
            else:
                middle = True
        elif state == GLUT_UP:
            shiftmiddle = False
            middle = False
    elif button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            right = True
        elif state == GLUT_UP:
            right = False
    if state == GLUT_DOWN:
        last_motion = (0, 0)
    elif state == GLUT_UP:
        last_coords = None


def motionfunc(x, y):
    global last_coords
    global last_motion
    global left
    global middle
    global shiftmiddle
    global right

    glutPostRedisplay()

    # Case 0: ignore motion.
    if not left and not middle and not shiftmiddle and not right:
        return
    # Case 1: initialize last_coords.
    if last_coords == None:
        last_coords = (x, y)
    # Case 2: two-chained last_coords.
    else:
        x_i, y_i = last_coords
        x_f, y_f = (x, y)
        last_motion = [x_f - x_i, y_f - y_i]
        last_coords = x_f, y_f

    # middle/shiftmiddle toggling
    if middle or shiftmiddle:
        if glutGetModifiers() == GLUT_ACTIVE_SHIFT:
            shiftmiddle = True
            middle = False
        else:
            middle = True
            shiftmiddle = False


def idlefunc():
    global last_motion
    global robot
    glutPostRedisplay()
    return


def set_view():
    '''
    Cleaned up from old set.  Handles all that cumulative MODELVIEW transform
    jazz from user mouse input.
    '''
    global left
    global middle
    global shiftmiddle
    global right
    global R_cumm
    global T_cumm
    global spin

    # Scaling factor
    c = 0.125

    # # ZOOM & PLANAR TRANSLATE
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixf(T_cumm)
    mag_last_motion = (last_motion[0]**2 + last_motion[1]**2)**.5
    # Zoom
    if shiftmiddle or right:
        glTranslatef(0, 0, -.1*c*last_motion[1])
    # Planar Translate
    if middle:
        glTranslatef(c*last_motion[0], -c*last_motion[1], 0.0)
    T_cumm = glGetFloatv(GL_MODELVIEW_MATRIX)

    # # TRANSLATION R-1 T R C_iO
    # NOTE we must first apply rotation because translation is in current z.
    glLoadIdentity()
    glMultMatrixf(R_cumm.transpose())
    glMultMatrixf(T_cumm)
    glMultMatrixf(R_cumm)

    # # ROTATION
    C_iO = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()

    # R+ := R R_cumm 
    if left and mag_last_motion > 0.0:
        translated = glGetFloatv(GL_MODELVIEW_MATRIX)
        # MultMatrix right multiplies by input.
        # So we here left multiply by glRotatef as intended.
        xy_axis = [last_motion[1]/mag_last_motion,
                last_motion[0]/mag_last_motion]
        glLoadIdentity()
        glRotatef(c*mag_last_motion/5, xy_axis[0], xy_axis[1], 0)
        glMultMatrixf(R_cumm)
        # Hash R_cumm
        R_cumm = glGetFloatv(GL_MODELVIEW_MATRIX)
        # Recover translated.
        glLoadMatrixf(translated)
    if spin:
        translated = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()
        glMultMatrixf(R_cumm)
        glRotatef(c, 0, 1, 0)
        R_cumm = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadMatrixf(translated)
    # Multiply by cummulative rotation.
    glMultMatrixf(R_cumm)
    # C_iO
    glMultMatrixf(C_iO)


def draw_axes():
    '''
    Dang son look at that fade.
    '''
    O = (0,0,0)
    l = 5
    x = [O, (l,0,0)]
    y = [O, (0,l,0)]
    z = [O, (0,0,l)]
    axes = x+y+z
    r = (1,0,0)
    g = (0,1,0)
    b = (0,0,1)
    o = (0,0,0)
    w = (1,1,1)
    rgb = [w,o,w,o,w,o]

    glDisable(GL_LIGHTING)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, axes)
    glColorPointer(3, GL_FLOAT, 0, rgb)
    glDrawArrays(GL_LINES, 0, len(axes))
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glEnable(GL_LIGHTING)


def make_cube(color=[0.8, 0.0, 0.0, 1.0], xyz=None):
    '''
    Uses glutSolidCube to make a cube of
        color color
        at xyz position xyz.
    '''

    initMaterial(special=color)

    SIZE = 1.

    # To draw at some given xyz.
    if xyz != None:
        glPushMatrix()
        glTranslatef(*xyz)
    glutSolidCube(SIZE)
    if xyz != None:
        glPopMatrix()


def redraw():
    '''
    Step the robot and draw.
    '''
    global robot
    global drawing_mode

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    set_view()
    draw_axes()

    robot.step()
    robot.draw()

    glutSwapBuffers()


def resize(w, h):
    if w > h: w = h;
    else: h = w;

    glViewport(0, 0, w, h)
    glutPostRedisplay()


def initMaterial(special=False):
    emit = [0.0, 0.1, 0.0, 1.0]
    amb  = [0.2, 0.2, 0.2, 1.0]
    if special:
        amb = special
    diff = [1.0, 1.0, 1.0, 1.0]
    spec = [1.0, 1.0, 1.0, 1.0]
    shiny = 100.0

    glMaterialfv(GL_FRONT, GL_AMBIENT, amb)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diff)
    glMaterialfv(GL_FRONT, GL_SPECULAR, spec)
    glMaterialfv(GL_FRONT, GL_EMISSION, emit)
    glMaterialfv(GL_FRONT, GL_SHININESS, shiny)


def initLights():
    for i in [1,2,3]:
        c = 2.5
        R = {1:10 ,2:-10 ,3:0}[i]
        amb = [c, c, c, 1.0]
        diff = [c, c, c, 1.0]
        spec = [c, c, c, 1.0]
        lightpos = [R, R, R, 1.0]

        # Lights
        GL_light = eval("GL_LIGHT" + str(i))
        glLightfv(GL_light, GL_AMBIENT, amb)
        glLightfv(GL_light, GL_DIFFUSE, diff)
        glLightfv(GL_light, GL_SPECULAR, spec)
        glLightfv(GL_light, GL_POSITION, lightpos)
        glLightfv(GL_light, GL_LINEAR_ATTENUATION, .9)
        glEnable(GL_light)

    # Ambient light.
    ambientColor = [2.0, 2.0, 1.8, 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambientColor);
    glEnable(GL_LIGHTING)


def initGL():
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)


def initGLUT():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(1800, 200)
    glutCreateWindow("MBlock Visualizer v0")


# def initTexture(file_name):
    # '''
    # Initialize a texture using pygame.
    # Handles OpenGL initialization, and adds to the global texture_dict.
    # return texture_name, RGBA pixel data, width, height.
    # NOTE adapted from example: http://www.pygame.org/wiki/SimpleOpenGL2dClasses
    # '''
    # global texture_dict
    # # 1) Generate texture name (GLuint) with glGenTextures(num_textures)
    # texture_name = glGenTextures(1)
    # # Load image with pygame and grab width and height.
    # _pygame_image = pygame.image.load(file_name)
    # width = _pygame_image.get_width()
    # height = _pygame_image.get_height()
    # # Grab RGBA pixel data with pygame.
    # pixel_data = pygame.image.tostring(_pygame_image, "RGBA", 1)
    # return (texture_name, pixel_data, width, height)


# def bindTexture(texture_name, pixel_data, width, height, gl_texture_coordinates):
    # '''
    # FORNOW Bind the texture.
    # NOTE adapted from example: http://www.pygame.org/wiki/SimpleOpenGL2dClasses
    # '''
    # # 2) Select new texture with glBindTexture
    # glBindTexture(GL_TEXTURE_2D, texture_name)
    # # 3) Fill the texture with image using glTexImage2D
    # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
            # GL_UNSIGNED_BYTE, pixel_data)
    # # 4) Set texture's minification and magnification filters using glTexParameteri
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # # 6) Bind with glTexCoordPointer
    # glTexCoordPointer(2,  GL_FLOAT, 0, gl_texture_coordinates)
    # return


def main():
    global robot
    # global texture_dict

    initGLUT() # Initialize GLUT first!  Depth test depends on window.
    initGL()
    initLights()
    initMaterial()
    initCumm()

    # Set up perspective matrix with really far clipping plane
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-1, 1, -1, 1, 1, 100)
    set_view()

    robot = Robot()

    # Set up callbacks
    glutDisplayFunc(redraw)
    glutReshapeFunc(resize)
    glutKeyboardFunc(keyfunc)
    glutMouseFunc(mousefunc)
    glutMotionFunc(motionfunc)
    glutIdleFunc(idlefunc)

    glutMainLoop()

if __name__ == "__main__": main()

