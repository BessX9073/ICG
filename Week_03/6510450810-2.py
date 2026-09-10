import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *
import numpy as np
import pandas as pd

def display(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(*(centroid+(0, 10, max(bbox))), *centroid, 0, 1, 0)
    glRotatef(degree, 0, 1, 0)

    if model_on:
        glBegin(GL_TRIANGLES)
        for i in range(n_vertices):
            glColor3fv(0.5 * (normals[i] + 1))
            glVertex3fv(positions[i])
        glEnd()

    if triangle_on:
        glColor3f(0, 0, 0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_TRIANGLES)
        for i in range(n_vertices):
            glVertex3fv(positions[i])
        glEnd()
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe_on else GL_FILL)

    if normal_lines_on:
        glBegin(GL_LINES)
        for t in range(n_triangles):
            tail = face_centroids[t]
            head = tail + face_normals[t] * vector_scale
            glColor3f(0, 1, 0)
            glVertex3fv(tail)
            glColor3f(1, 0, 0)
            glVertex3fv(head)
        glEnd()

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

model_on = True
wireframe_on, animation_on = False, False
triangle_on = False
normal_lines_on = False
vector_scale = 1.0

def keyboard(window, key, scancode, action, mods):
    global wireframe_on, animation_on
    global triangle_on, normal_lines_on, vector_scale, model_on

    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_SPACE:
            animation_on = not animation_on
        elif key == GLFW_KEY_W:
            wireframe_on = not wireframe_on
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe_on else GL_FILL)
        elif key == GLFW_KEY_T:
            triangle_on = not triangle_on
        elif key == GLFW_KEY_N:
            normal_lines_on = not normal_lines_on
        elif key == GLFW_KEY_O:
            vector_scale = max(0.1, vector_scale - 0.1)
        elif key == GLFW_KEY_P:
            vector_scale = vector_scale + 0.1
        elif key == GLFW_KEY_M:
            model_on = not model_on
        elif key == GLFW_KEY_Q:
            glfwSetWindowShouldClose(window, GLFW_TRUE)
    glfwPostEmptyEvent()

def compute_face_normals_and_centroids(positions, n_triangles):
    p0 = positions[0::3]
    p1 = positions[1::3]
    p2 = positions[2::3]

    face_n = np.cross(p1 - p0, p2 - p0)
    norm_len = np.linalg.norm(face_n, axis=1, keepdims=True)
    norm_len[norm_len < 1e-8] = 1.0
    face_n = face_n / norm_len

    face_c = (p0 + p1 + p2) / 3.0
    return face_n.astype(np.float32), face_c.astype(np.float32)

def my_init():
    global n_vertices, positions, colors, normals, uvs
    global centroid, bbox
    global n_triangles, face_normals, face_centroids

    glClearColor(0.2, 0.8, 0.8, 1)

    df = pd.read_csv(r"C:\Users\room703\6510450810\models\ashtray.tri",
                     sep='\s+', comment='#',
                     header=None, dtype=np.float32)

    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    n_vertices = len(positions)
    n_triangles = n_vertices // 3
    print("no. of vertices: %d, no. of triangles: %d" %
          (n_vertices, n_triangles))

    face_normals, face_centroids = compute_face_normals_and_centroids(positions, n_triangles)

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

    win_w, win_h = 1024, 768
    window = glfwCreateWindow(1, 1, "6510450810-2", None, None)
    glfwMakeContextCurrent(window)
    show_versions()

    glfwSetKeyCallback(window, keyboard)
    glfwSetWindowRefreshCallback(window, display)
    glfwSetWindowSizeCallback(window, reshape)
    glfwSetWindowPos(window, 20, 50)
    glfwSetWindowSize(window, win_w, win_h)

    my_init()
    while not glfwWindowShouldClose(window):
        if animation_on:
            animation(window)
        display(window)
        glfwWaitEvents()
    glfwDestroyWindow(window)
    glfwTerminate()

if __name__ == "__main__":
    main()