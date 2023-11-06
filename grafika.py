from PIL import Image

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

beginningVertices = (  # vertices of main pyramid
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, -1),
    (1, -1, -1)
)

edges = (  # edges of main pyramid
    (0, 1),
    (0, 2),
    (0, 3),

    (1, 2),
    (1, 3),
    (2, 3),
)

colors = (
    (1, 0, 0),
    (1, 1, 0),
    (1, 0, 1),
    (0, 0, 1),
    (0, 1, 1),
    (0, 1, 0)
)

surfaces = (  # walls of main pyramid
    (0, 1, 2),
    (0, 2, 3),
    (0, 1, 3),
    (1, 2, 3)
)

ground_vertices = ( # ground vertices on which pyramid stands on
    (-300, -1, 3000),
    (300, -1, 300),
    (-300, -1, -300),
    (300, -1, -300)
)


def ground():
    glBegin(GL_QUADS)
    for vertex in ground_vertices:
        glColor3fv((0, 0.5, 0))
        glVertex3fv(vertex)
    glEnd()


def midpoint(p1, p2):  # function returning midpoint of two points
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2


def sub_tetrahedrons(vertices):  # function which returns vertices of 4 smaller tetrahedrons
    midpoints = [midpoint(vertices[edge[0]], vertices[edge[1]]) for edge in edges]

    return [
        (vertices[0], midpoints[0], midpoints[1], midpoints[2]),
        (vertices[1], midpoints[0], midpoints[3], midpoints[4]),
        (vertices[2], midpoints[1], midpoints[3], midpoints[5]),
        (vertices[3], midpoints[2], midpoints[4], midpoints[5])
    ]


def load_texture():  # unused as of now
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    image = Image.open("image.jpg")
    image_data = image.tobytes("raw", "RGBX", 0, -1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture


def tetrahedron(vertices, check):  # function drawing a tetrahedron
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glColor3fv((1, 1, 1))
            glVertex3fv(vertices[vertex])
    glEnd()

    if check == 1:  # if we are on the last level, we paint the walls
        glBegin(GL_TRIANGLES)
        for surface in surfaces:
            for i, vertex in enumerate(surface):
                #  glColor3fv(colors[i])
                glColor3f(colors[i][0], colors[i][1], colors[i][2])
                glVertex3fv(vertices[vertex])
        glEnd()


def sierpinski(vertices, depth, texture_status):  # recursively drawing sierpinski pyramid
    if depth == 0:
        tetrahedron(vertices, texture_status)
        return
    tetrahedrons = sub_tetrahedrons(vertices)
    for tetra in tetrahedrons:
        sierpinski(tetra, depth - 1, texture_status)


def light(light_color):  # funckja odpowiadajaca za oswietlenie
    # glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 0))

    # Ustaw pozycję źródła światła jako światło kierunkowe
    light_direction = (-1, -1, -1, 0)  # Kierunek światła (x, y, z, 0 - światło kierunkowe)
    glLightfv(GL_LIGHT0, GL_POSITION, light_direction)

    # Ustaw kolor światła (RGB)
    #light_diffuse = (0, 0, 1.0, 1.0)  # Kolor światła (RGBA)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)

    glLight(GL_LIGHT0, GL_POSITION, light_color)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_color)

    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)


def sphere(radius, slices, stacks):
    quad = gluNewQuadric()
    gluQuadricTexture(quad, GL_TRUE)
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad)


def light_sphere():
    glPushMatrix()
    glTranslatef(5.0, 5.0, 5.0)
    glScalef(0.1, 0.1, 0.1)
    sphere(1, 30, 30)
    glPopMatrix()


def set_light_properties():
    # Materiał źródła światła
    glMaterialfv(GL_FRONT, GL_AMBIENT, [1.0, 1.0, 1.0, 1.0])  # Kolor światła rozproszonego
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Kolor światła rozproszonego
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # Kolor światła odbitego
    glMaterialfv(GL_FRONT, GL_SHININESS, [128.0])  # Współczynnik połysku


def main():
    rotation_status = 1
    rotation_pyramid = 0
    rotation_speed_pyramid = 0.5
    rotation_light = 0
    rotation_speed_light = 3
    texture_status = 1
    light_color = [1.0, 0.0, 0.0, 1.0]
    scale_factor = 0

    input_str = input("Enter how many levels should the pyramid have = ")
    levels = int(input_str)
    if levels > 4:
        texture_status = 0
        if levels > 6:
            levels = 6

    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    gluPerspective(70, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    #Zeby obiekty reagowaly na swiatlo
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # stop or begin rotation
                if event.key == pygame.K_r:
                    if rotation_status == 1:
                        rotation_status = 0
                    else:
                        rotation_status = 1
                # turn textures off or on
                if event.key == pygame.K_t:
                    if texture_status == 0 and levels < 5:
                        texture_status = 1
                    else:
                        texture_status = 0
                # zoom in
                if event.key == pygame.K_EQUALS:
                    if scale_factor < 3:
                        glScale(2, 2, 2)
                        scale_factor += 1
                # zoom out
                if event.key == pygame.K_MINUS:
                    if scale_factor > -3:
                        glScale(0.5, 0.5, 0.5)
                        scale_factor -= 1
                if event.key == pygame.K_7:
                    light_color = [1.0, 0.0, 0.0, 1.0]
                if event.key == pygame.K_8:
                    light_color = [0.0, 1.0, 0.0, 1.0]
                if event.key == pygame.K_9:
                    light_color = [0.0, 0.0, 1.0, 1.0]
                if event.key == pygame.K_UP:
                    glTranslatef(0, 0, 1)
                if event.key == pygame.K_DOWN:
                    glTranslatef(0, 0, -1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

        # control rotation
        rotation_pyramid += rotation_speed_pyramid if rotation_status == 1 else 0
        rotation_light += rotation_speed_light if rotation_status == 1 else 0

        # Draw and rotate pyramid
        glPushMatrix()
        # glRotatef(rotation_pyramid, 0, 1, 0)
        sierpinski(beginningVertices, levels, texture_status)
        glPopMatrix()

        # Draw and rotate light source
        glPushMatrix()
        # glTranslatef(5.0, 5.0, 5.0)
        glRotatef(rotation_light, 0, 1, 0)
        # sphere(1, 30, 30)
        light_sphere()
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
        set_light_properties()
        glPopMatrix()

        light(light_color)

        ground()


        pygame.display.flip()
        pygame.time.wait(20)


main()

