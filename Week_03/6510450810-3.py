import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *
import numpy as np
import pandas as pd

def draw_model():
    glBegin(GL_TRIANGLES)
    for i in range(n_vertices):
        glColor3fv(0.5 * (normals[i] + 1))
        glVertex3fv(positions[i])
    glEnd()

def display(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eye_target = (centroid[0] - scale_ref*0.3, centroid[1], centroid[2])
    eye = (eye_target[0], eye_target[1] + cam_height, eye_target[2] + cam_dist)
    gluLookAt(*eye, *eye_target, 0, 1, 0)
    glRotatef(degree, 0, 1, 0)

    glPushMatrix()
    glTranslatef(0, -min_y, 0)
    draw_model()
    glPopMatrix()

    glPushMatrix()
    s2 = 0.6
    glTranslatef(scale_ref*0.7, -min_y * s2, 0)
    glScalef(s2, s2, s2)
    draw_model()
    glPopMatrix()

    glPushMatrix()
    s3 = 1.3
    glTranslatef(-scale_ref*1.1, -min_y * s3, 0)
    glScalef(s3, s3, s3)
    draw_model()
    glPopMatrix()

    glfwSwapBuffers(window)

def reshape(window, w, h):
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
        elif key == GLFW_KEY_Q:
            glfwSetWindowShouldClose(window, GLFW_TRUE)
    glfwPostEmptyEvent()

def my_init():
    global n_vertices, positions, colors, normals, uvs
    global centroid, bbox, min_y
    global cam_dist, cam_height

    glClearColor(0.2, 0.8, 0.8, 1)

    df = pd.read_csv(r"C:\Users\room703\6510450810\models\teapot.tri",
                     sep='\s+', comment='#',
                     header=None, dtype=np.float32)

    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)
    min_y = df.values[:, 1].min()

    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    n_vertices = len(positions)
    print("no. of vertices: %d, no. of triangles: %d" %
          (n_vertices, n_vertices//3))

    cam_dist = 14.0
    cam_height = 3.5
    global scale_ref
    scale_ref = max(bbox)
    print("bbox:", bbox, " scale_ref:", scale_ref)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glLineWidth(1)

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

def main():
    global window, win_w, win_h

    if not glfwInit():
        glfwTerminate()
        return

    win_w, win_h = 800, 600
    glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE)
    window = glfwCreateWindow(win_w, win_h, "6510450810-3", None, None)
    glfwMakeContextCurrent(window)
    show_versions()

    glfwSetKeyCallback(window, keyboard)
    glfwSetWindowRefreshCallback(window, display)
    glfwSetWindowSizeCallback(window, reshape)
    glfwSetWindowPos(window, 20, 50)

    my_init()
    reshape(window, win_w, win_h)
    while not glfwWindowShouldClose(window):
        if animation_on:
            animation(window)
        display(window)
        glfwWaitEvents()
    glfwDestroyWindow(window)
    glfwTerminate()

if __name__ == "__main__":
    main()