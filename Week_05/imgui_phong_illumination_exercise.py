import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *
import numpy as np
import pandas as pd
import time, math as m
import imgui
from imgui.integrations.glfw import GlfwRenderer

impl, angle = None, 0
win_w, win_h = 1280, 800
Ka = [0.3, 0.3, 0.3]
I, light_pos, eye_pos, eye_at = [1, 1, 1], [0, 0, 10], [0, 0, 0], [0, 0, 0]
rot_x, rot_y, specular_on = 0, 30, True
clear_color = [0.5, 0.85, 0.85]
mouse_status = {'x': 0, 'y': 0, 
                GLFW_MOUSE_BUTTON_LEFT: GLFW_RELEASE, 
                GLFW_MOUSE_BUTTON_MIDDLE: GLFW_RELEASE,
                GLFW_MOUSE_BUTTON_RIGHT: GLFW_RELEASE}

def normalize(u):
    return u / (np.linalg.norm(u) + 1e-5)

def draw_gui():
    global I, Ka, Kd, Ks, shininess, clear_color
    global rot_x, rot_y, specular_on, two_sided_on

    impl.process_inputs()
    imgui.new_frame()                 # Start the Dear ImGui frame 
    imgui.set_next_window_position(win_w-420, 50, imgui.APPEARING)
    imgui.set_next_window_size(400, 380, imgui.APPEARING)
    imgui.set_next_window_collapsed(False, imgui.FIRST_USE_EVER)
    imgui.begin("Control")            # Create a window
    imgui.push_item_width(300)
    _, I = imgui.color_edit3("Light Intensity", *I)
    _, Ka = imgui.color_edit3("Ka", *Ka)
    _, specular_on = imgui.checkbox("Specular Enabled", specular_on)
    imgui.text("Light Position")
    imgui.push_item_width(100)
    _, light_pos[0] = imgui.slider_float("X###light_pos_x", light_pos[0], -10, 10)
    imgui.same_line()
    _, light_pos[1] = imgui.slider_float("Y###light_pos_y", light_pos[1], -10, 10)
    imgui.same_line()
    _, light_pos[2] = imgui.slider_float("Z###light_pos_z", light_pos[2], -10, 10)
    imgui.text("Eye Position")
    _, eye_pos[0] = imgui.slider_float("X###eye_pos_x", eye_pos[0], -10, 10)
    imgui.same_line()
    _, eye_pos[1] = imgui.slider_float("Y###eye_pos_y", eye_pos[1], -10, 10)
    imgui.same_line()
    _, eye_pos[2] = imgui.slider_float("Z###eye_pos_z", eye_pos[2], -10, 10)
    imgui.text("Eye At")
    _, eye_at[0] = imgui.slider_float("X###eye_at_x", eye_at[0], -10, 10)
    imgui.same_line()
    _, eye_at[1] = imgui.slider_float("Y###eye_at_y", eye_at[1], -10, 10)
    imgui.same_line()
    _, eye_at[2] = imgui.slider_float("Z###eye_at_z", eye_at[2], -10, 10)
    imgui.pop_item_width()
    imgui.text("Model Rotation")
    imgui.push_item_width(150)    
    _, rot_x = imgui.slider_float("X###rotate_x", rot_x, -180, 180)
    imgui.same_line()        
    _, rot_y = imgui.slider_float("Y###rotate_y", rot_y, -180, 180)
    imgui.pop_item_width()        
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)

    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    imgui.end()

def resize(window, w, h):
    glViewport(0, 0, w, h)	
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.1, 50)

def refresh(window):
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(*eye_pos, *eye_at, 0, 1, 0)

    glRotate(angle, 0.8, 0.8, 0.2)
    glRotate(rot_x, 1, 0, 0)
    glRotate(rot_y, 0, 1, 0)

    compute_phong()

    # Prepare passing vertex positions, colors, normals, and uvs to GPU
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)      
    
    draw_gui()
    imgui.render()
    impl.render(imgui.get_draw_data())    

    glfwSwapBuffers(window)

wireframe_on, animation_on = False, False
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

def mouse_func(window, button, action, mods):
    mouse_status['x'], mouse_status['y'] = glfwGetCursorPos(window)
    mouse_status[button] = action

def cursor_func(window, x, y):
    global light_rotation

    if impl.io.want_capture_mouse:
        return
    dx, dy = x-mouse_status['x'], mouse_status['y']-y 
    mouse_status['x'], mouse_status['y'] = x, y
    if mouse_status[GLFW_MOUSE_BUTTON_LEFT] == GLFW_PRESS:
        light_rotation[0] += 0.5*dx
        light_rotation[1] -= 0.5*dy

def scroll_func(window, dx, dy):
    scroll_scale = 0.2
    eye_dir = normalize(eye_at - eye_pos)    
    eye_pos[:] += dy * scroll_scale * eye_dir
    eye_at[:] += dy * scroll_scale * eye_dir

def animation(window):
    global angle

    angle += 1

def compute_phong(vectorized=False):
    if vectorized:
        P = positions
        L = light_pos - P
        L  = L * 1/np.linalg.norm(L, axis=1).reshape(-1, 1)
        N = normals
        NdotL = np.sum(N * L, axis=1).reshape(-1, 1)
        V  = eye_pos - P
        V  = V * 1/np.linalg.norm(V, axis=1).reshape(-1, 1)
        R  = 2 * NdotL * N - L
        R  = R * 1/np.linalg.norm(R, axis=1).reshape(-1, 1)
        VdotR = np.sum(V * R, axis=1)
        ambient = np.array(Ka) * np.array(I)
        diffuse = Kd * np.maximum(NdotL, 0).reshape(-1, 1) * I
        specular = Ks * np.power(np.maximum(VdotR, 0), shininess).reshape(-1, 1) * I
        specular = (NdotL > 0) * specular_on * specular
        colors[:] = ambient + diffuse + specular
    else: # compute vertex colors using Phong Equation
        pass

def gl_init():
    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global impl, eye_pos, eye_at

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlfwRenderer(window, attach_callbacks=False)
    imgui.get_io().font_global_scale = 1.0

    df = pd.read_csv("../models/teapot_uv.tri", sep='\s+',
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
    print("Centroid:", centroid)
    print("BBox:", bbox)
    eye_pos = centroid + (0.5, 1.5, 1.5)
    eye_at = centroid + (0.5, 0, 0)

def main():
    global window

    if not glfwInit():
        glfwTerminate()
        return

    window = glfwCreateWindow(win_w, win_h, "imGui: Phong Illumination Exercise", None, None)
    glfwMakeContextCurrent(window)  
    glfwSetWindowRefreshCallback(window, refresh)
    glfwSetWindowSizeCallback(window, resize)
    glfwSetKeyCallback(window, keyboard)
    glfwSetMouseButtonCallback(window, mouse_func)
    glfwSetCursorPosCallback(window, cursor_func)
    glfwSetScrollCallback(window, scroll_func)    
    glfwSetWindowPos(window, 20, 50)    

    gl_init()
    resize(window, win_w, win_h)    
    while not glfwWindowShouldClose(window):
        if animation_on:
            animation(window)
        glfwPollEvents()
        refresh(window)
    impl.shutdown()        
    glfwDestroyWindow(window)
    glfwTerminate()

if __name__ == "__main__":
    main()