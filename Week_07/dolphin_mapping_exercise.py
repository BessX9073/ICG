import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *
from PIL import Image

def resize(window, w, h):
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

def refresh(window):
    glColor3f(1.0, 1.0, 0.0)

    glClearColor(1, 1, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glBegin(GL_QUADS)
    glVertex3f( 1.0, 1.0, 0.0)
    glVertex3f(-1.0, 1.0, 0.0)
    glVertex3f(-1.0,-1.0, 0.0)
    glVertex3f( 1.0,-1.0, 0.0)
    glEnd()

    glfwSwapBuffers(window)

def gl_init():
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    filename = "../texture_map/dolphin.jpg"
    # Insert code for texture mapping here!

def main():
    global window

    if not glfwInit():
        glfwTerminate()
        return

    window = glfwCreateWindow(800, 800, "Texture Mapping Exercise", None, None)
    glfwMakeContextCurrent(window)  
    glfwSetWindowRefreshCallback(window, refresh)
    glfwSetWindowSizeCallback(window, resize)

    gl_init()
    while not glfwWindowShouldClose(window):
        refresh(window)
        glfwWaitEvents()
    glfwDestroyWindow(window)
    glfwTerminate()

if __name__ == "__main__":
    main()