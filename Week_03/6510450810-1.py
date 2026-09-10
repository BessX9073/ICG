import sys
from OpenGL.GL import *
from glfw.GLFW import *

tx, ty = 0.0, 0.0
move_speed = 0.05
angle = 0.0
rotate_on = False

def display(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    glTranslatef(tx, ty, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    
    glBegin(GL_TRIANGLES)
    glColor3f(0.0, 0.0, 0.0)
    glVertex2f(0.0, 0.2)
    glVertex2f(-0.2, -0.2)
    glVertex2f(0.2, -0.2)
    glEnd()
    
    glfwSwapBuffers(window)

def keyboard(window, key, scancode, action, mods):
    global tx, ty, rotate_on
    
    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_I:
            ty += move_speed
        elif key == GLFW_KEY_K:
            ty -= move_speed
        elif key == GLFW_KEY_J:
            tx -= move_speed
        elif key == GLFW_KEY_L:
            tx += move_speed
            
    if key == GLFW_KEY_SPACE:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            rotate_on = True
        elif action == GLFW_RELEASE:
            rotate_on = False

def main():
    global angle
    if not glfwInit(): return
    window = glfwCreateWindow(800, 600, "6510450810-1", None, None)
    glfwMakeContextCurrent(window)
    
    glClearColor(1, 0, 1, 1)
    
    glfwSetKeyCallback(window, keyboard)
    glfwSetWindowRefreshCallback(window, display)
    
    while not glfwWindowShouldClose(window):
        if rotate_on:
            angle += 2.0
            if angle >= 360.0:
                angle -= 360.0
                
        display(window)
        glfwPollEvents()
        
    glfwDestroyWindow(window)
    glfwTerminate()

if __name__ == "__main__":
    main()