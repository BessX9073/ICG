import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *
import numpy as np
import pandas as pd

v0 = np.array((-1.5, -0.9, 0.0))
v1 = np.array((1.2, -0.9, 0.0))
v2 = np.array((0.0, 1.8, 0.0))
c = (v0 + v1 + v2) / 3

def refresh(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(c[0], c[1], c[2]+5, c[0], c[1], c[2], 0, 1, 0)
    glRotatef(degree, 0.5, 0.8, 0)

    glPolygonOffset(1.0, 0.1)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0.5, 0.5)
    glVertex3fv(v0)
    glColor3f(0.5, 1, 0.5)
    glVertex3fv(v1)
    glColor3f(0.5, 0.5, 1)
    glVertex3fv(v2)
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

    glfwSwapBuffers(window)

def resize(window, w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w/h, 1, 50)

degree = 0
def animation(window):
    global degree
    degree = degree + 1
    glfwPostEmptyEvent()

wireframe_on, animation_on = False, False
def keyboard(window, key, scancode, action, mods):
    global wireframe_on, animation_on

    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_SPACE:
            animation_on = not animation_on
        elif key == GLFW_KEY_W:
            wireframe_on = not wireframe_on
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe_on else GL_FILL)
        elif key in (GLFW_KEY_ESCAPE, GLFW_KEY_Q):
            glfwSetWindowShouldClose(window, GLFW_TRUE)
    glfwPostEmptyEvent()

def my_init():
    glClearColor(0.2, 0.8, 0.8, 1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glLineWidth(1)
    glEnable(GL_MULTISAMPLE)

def main():
    global window, win_w, win_h

    if not glfwInit():
        glfwTerminate()
        return

    win_w, win_h = 1024, 768
    
    # More info at https://learnopengl.com/Advanced-OpenGL/Anti-Aliasing
    glfwWindowHint(GLFW_SAMPLES, 8)
    window = glfwCreateWindow(win_w, win_h, "A Triangular Normal Exercise", None, None)
    glfwMakeContextCurrent(window)
    
    glfwSetWindowRefreshCallback(window, refresh)
    glfwSetWindowSizeCallback(window, resize)
    glfwSetKeyCallback(window, keyboard)
    glfwSetWindowPos(window, 20, 50)
    resize(window, *glfwGetWindowSize(window)) 

    my_init()
    while not glfwWindowShouldClose(window):
        if animation_on:
            animation(window)
        refresh(window)
        glfwWaitEvents()
    glfwDestroyWindow(window)
    glfwTerminate()   

if __name__ == "__main__":
    main()