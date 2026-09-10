import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *
import numpy as np
import pandas as pd
import time, math as m

win_w, win_h = 1024, 768
wireframe_on, animation_on = False, False
mouse_status = {'x': 0, 'y': 0, 
                GLFW_MOUSE_BUTTON_LEFT: GLFW_RELEASE, 
                GLFW_MOUSE_BUTTON_MIDDLE: GLFW_RELEASE,
                GLFW_MOUSE_BUTTON_RIGHT: GLFW_RELEASE}
angle = 0

def resize(window, w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, win_w/win_h, 0.01, 30)

def refresh(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(*eye_pos, *eye_at, 0, 1, 0)
    glRotate(angle, 0, 1, 0)

    glVertexPointer(3, GL_FLOAT, 0, positions)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)   
    glfwSwapBuffers(window)

def keyboard(window, key, scancode, action, mods):
    global wireframe_on, animation_on, gui_on

    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_SPACE:
            animation_on = not animation_on
        elif key == GLFW_KEY_G:
            gui_on = not gui_on            
        elif key == GLFW_KEY_W:
            wireframe_on = not wireframe_on
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe_on else GL_FILL)
        elif key in (GLFW_KEY_UP, GLFW_KEY_DOWN, GLFW_KEY_LEFT, GLFW_KEY_RIGHT):
            dx, dy, key_scale = 0, 0, 0.1
            if key == GLFW_KEY_LEFT:
                dx = -1
            elif key == GLFW_KEY_RIGHT:
                dx = 1
            elif key == GLFW_KEY_UP:
                dy = 1
            elif key == GLFW_KEY_DOWN:
                dy = -1
            eye_dir = normalize(eye_at - eye_pos)
            up_dir = np.array((0, 1, 0))
            left_dir = np.cross(eye_dir, up_dir)
            up_dir = np.cross(left_dir, eye_dir)
            if mods & GLFW_MOD_CONTROL:
                eye_pos[:] += dy * key_scale * eye_dir
                eye_at[:] += dy * key_scale * eye_dir
            else:
                eye_pos[:] += dx * key_scale * left_dir
                eye_at[:] += dx * key_scale * left_dir
                eye_pos[:] += dy * key_scale * up_dir
                eye_at[:] += dy * key_scale * up_dir            
        elif key in (GLFW_KEY_ESCAPE, GLFW_KEY_Q):
            glfwSetWindowShouldClose(window, GLFW_TRUE)
    glfwPostEmptyEvent()

def mouse_func(window, button, action, mods):
    mouse_status['x'], mouse_status['y'] = glfwGetCursorPos(window)
    mouse_status[button] = action
        
def cursor_func(window, x, y):
    dx, dy = x-mouse_status['x'], mouse_status['y']-y 

    if mouse_status[GLFW_MOUSE_BUTTON_LEFT] == GLFW_PRESS:
        pass
    elif mouse_status[GLFW_MOUSE_BUTTON_MIDDLE] == GLFW_PRESS:
        pass
    elif mouse_status[GLFW_MOUSE_BUTTON_RIGHT] == GLFW_PRESS:
        pass
    mouse_status['x'], mouse_status['y'] = x, y

def animation(window):
    global angle

    angle += 1

def normalize(v):
    l = np.linalg.norm(v)
    if l == 0:
        return v
    else:
        return v/l

def gl_init_models():
    global start_time
    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global eye_pos, eye_at, light_pos    

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

    df = pd.read_csv("../models/bunny_uv.tri", sep='\s+', 
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    n_vertices = len(df.values)
    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    print("no. of vertices: %d, no. of triangles: %d" % 
          (n_vertices, n_vertices//3))    

    # Compute illumination here!
    eye_pos = np.array((0, 3, 3), dtype='float32')
    eye_at = centroid
    light_pos = eye_pos
    # ...
    colors[:] = (1, 1, 0)

def main():
    global window

    if not glfwInit():
        glfwTerminate()
        return

    window = glfwCreateWindow(win_w, win_h, "Illumination with Key Control Exercise", None, None)
    glfwMakeContextCurrent(window)  
    glfwSetWindowRefreshCallback(window, refresh)
    glfwSetWindowSizeCallback(window, resize)
    glfwSetKeyCallback(window, keyboard)
    glfwSetMouseButtonCallback(window, mouse_func)
    glfwSetCursorPosCallback(window, cursor_func)

    gl_init_models()
    resize(window, win_w, win_h)
    while not glfwWindowShouldClose(window):
        if animation_on:
            animation(window)
        refresh(window)
        glfwPollEvents()
    glfwDestroyWindow(window)
    glfwTerminate()

if __name__ == "__main__":
    main()