import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

beginningVertices = (  # wierzcholki pierwotnej piramidy
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, -1),
    (1, -1, -1)
)

edges = (  # krawedzie pierwotnej piramidy
    (0, 1),
    (0, 2),
    (0, 3),

    (1, 2),
    (1, 3),
    (2, 3),
)

colors = (
    (0.1, 0, 0.1),
    (0, 0.2, 0.2),
    (0.2, 0.3, 0),
    (0.4, 0, 0.2),
    (0, 0.7, 0.1),
    (0.1, 0, 0.9)
)

surfaces = (  # sciany pierwotnej piramidy
    (0, 1, 2),
    (0, 2, 3),
    (0, 1, 3),
    (1, 2, 3)
)


def midpoint(p1, p2):  # funckja zwracajaca srodek miedzy punktami
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2


def sub_tetrahedrons(vertices):  # funckja zwracajaca wierzcholki 4 mniejszych czworoscianow
    midpoints = [midpoint(vertices[edge[0]], vertices[edge[1]]) for edge in edges]

    return [
        (vertices[0], midpoints[0], midpoints[1], midpoints[2]),
        (vertices[1], midpoints[0], midpoints[3], midpoints[4]),
        (vertices[2], midpoints[1], midpoints[3], midpoints[5]),
        (vertices[3], midpoints[2], midpoints[4], midpoints[5])
    ]


def tetrahedron(vertices, check):  # funckja rysująca czworościan
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    if check == 1:  # jezeli jestesmy na ostatnim poziomie to kolorujemy sciany
        glBegin(GL_TRIANGLES)
        for surface in surfaces:
            for i, vertex in enumerate(surface):
                #  glColor3fv(colors[i])
                glColor3f(colors[i][0], colors[i][1], colors[i][2])
                glVertex3fv(vertices[vertex])
        glEnd()


def sierpinski(vertices, depth):
    if depth == 0:
        tetrahedron(vertices, 1)
        return
    tetrahedrons = sub_tetrahedrons(vertices)
    for tetra in tetrahedrons:
        sierpinski(tetra, depth - 1)


def light():  # funckja odpowiadajaca za oswietlenie
    # glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 0))
    glLight(GL_LIGHT0, GL_POSITION, (4.875, 4.875, 4.875, 0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (30, 30, 30, 1))

    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)


def light_source():
    light_cube_v = (
        (3.75, 3.75, 3.75),
        (4, 3.75, 3.75),
        (4, 3.75, 4),
        (3.75, 3.75, 4),

        (3.75, 4, 3.75),
        (4, 4, 3.75),
        (4, 4, 4),
        (3.75, 4, 4)
    )

    light_cube_s = (
        (0, 1, 2, 3),
        (0, 1, 4, 5),
        (0, 3, 4, 7),

        (1, 2, 5, 6),
        (2, 3, 7, 6),
        (4, 5, 6, 7)
    )

    glBegin(GL_QUADS)
    for surface in light_cube_s:
        for i, vertex in enumerate(surface):
            glColor3f(255, 255, 255)
            glVertex3fv(light_cube_v[vertex])
    glEnd()


def main():
    input_str = input("Enter how many levels should the pyramid have =")
    levels = int(input_str)
    if levels > 4:
        print("For the sake of your computer the levels number was set to 4")
        levels = 4
    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    gluPerspective(70, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    rotation_status = 1
    light_rotation = 0
    pyramid_rotation = 0
    pyramid_rotation_speed = 0.5
    light_rotation_speed = 4

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    #glTranslatef(0.5, 0, 0)
                    rotation_status = 1

                if event.key == pygame.K_DOWN:
                    rotation_status = 0
                    #glTranslatef(-0.5, 0, 0)
                if event.key == pygame.K_RIGHT:
                    glScale(2, 2, 2)
                if event.key == pygame.K_LEFT:
                    glScale(0.5, 0.5, 0.5)

        # if rotation_status == 1:
        #     glRotatef(1, 0, 1, 0)
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # light()
        # light_source()
        # sierpinski(beginningVertices, levels)
        pyramid_rotation += pyramid_rotation_speed if rotation_status == 1 else 0
        light_rotation += light_rotation_speed if rotation_status == 1 else 0
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glRotatef(light_rotation, 0, 1, 0)
        light()
        light_source()
        glPopMatrix()

        glPushMatrix()
        glRotatef(pyramid_rotation, 0, 1, 0)
        sierpinski(beginningVertices, levels)
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(20)
        

main()
