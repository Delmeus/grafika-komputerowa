
import math
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


beginningVertices = (  # vertices of main pyramid
    (-1, 0, -2/3),
    (1, 0, -2/3),
    (0, 0, 4/3),
    (0, math.sqrt(20) / 3, 0)
)

edges = (  # edges of main pyramid
    (0, 1),
    (0, 2),
    (0, 3),

    (1, 2),
    (1, 3),
    (2, 3)
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

ground_vertices = ( # ground vertices on which pyramid stands on - was used with ground()
    (150, 0, 150),
    (150, 0, -150),
    (-150, 0, -150),
    (-150, 0, 150)
)


def calculate_normal(vertices, surface):
    p0 = vertices[surface[0]]
    p1 = vertices[surface[1]]
    p2 = vertices[surface[2]]

    v1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    v2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])

    normal = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )

    length = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
    normal = (normal[0] / length, normal[1] / length, normal[2] / length)

    return normal


def load_ground(): # load ground with texture
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    texture_surface = pygame.image.load("sand.jpg")
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)

    width, height = texture_surface.get_width(), texture_surface.get_height()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    step_size = 10
    for x in range(-30, 30, step_size):
        for z in range(-30, 30, step_size):
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex3fv((x, 0, z))

            glTexCoord2f(1, 0)
            glVertex3fv((x + step_size, 0, z))

            glTexCoord2f(1, 1)
            glVertex3fv((x + step_size, 0, z + step_size))

            glTexCoord2f(0, 1)
            glVertex3fv((x, 0, z + step_size))
            glEnd()

    glDisable(GL_TEXTURE_2D)


def ground(): # old ground method, not used anymore
    glBegin(GL_QUADS)
    for vertex in ground_vertices:
        glColor3fv((0, 0.4, 0))
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
            normal = calculate_normal(vertices, surface)
            glNormal3fv(normal)
            for i, vertex in enumerate(surface):
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


def directional_light(light_color, light_direction_position):  # method for directional light
    glLightfv(GL_LIGHT1, GL_POSITION, light_direction_position)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light_color)
    glLight(GL_LIGHT1, GL_POSITION, light_color)
    glLightfv(GL_LIGHT1, GL_AMBIENT, light_color)

    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)


def sphere(radius, slices, stacks, color):
    quad = gluNewQuadric()
    glColor4f(color[0], color[1], color[2], 0.5)
    gluQuadricTexture(quad, GL_TRUE)
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad)


def light_position(t):
    x = 2 * math.cos(t)
    y = 2 * math.sin(t)
    return [x, y]


def light_sphere(x, y, z, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(0.1, 0.1, 0.1)
    sphere(1, 30, 30, color)
    glPopMatrix()


def set_light_properties(color):
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
    glMaterialfv(GL_FRONT, GL_SPECULAR, color)
    glMaterialfv(GL_FRONT, GL_SHININESS, [0.1])


def main():
    # directional light variables
    light_direction_position = [1, 1, 1, 0.0]
    rotation_status = True
    rotation_pyramid = 0
    rotation_speed_pyramid = 0.5
    rotation_light = True
    texture_status = 1
    light_color = [1.0, 1.0, 1.0, 1.0]
    radius = 0
    light_type = 0

    input_str = input("Enter how many levels should the pyramid have = ")
    levels = int(input_str)
    if levels > 4:
        texture_status = 0
        if levels > 6:
            levels = 6

    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(70, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, -1, -5)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_BLEND)

    # point light
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.2)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.01)
    # directional light
    glLightfv(GL_LIGHT1, GL_SPOT_CUTOFF, 75.0)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 0.2)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.01)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.1)

    set_light_properties(light_color)
    while True:
        # controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                # zoom in and out (mouse)
                if event.button == 4:
                    glTranslatef(0, 0, 1.0)
                if event.button == 5:
                    glTranslatef(0, 0, -1.0)

            if event.type == pygame.KEYDOWN:
                # stop or start pyramid rotation
                if event.key == pygame.K_r:
                    rotation_status = not rotation_status
                # stop or start light rotation
                if event.key == pygame.K_y:
                    rotation_light = not rotation_light

                # turn textures off or on
                if event.key == pygame.K_t:
                    if texture_status == 0 and levels < 5:
                        texture_status = 1
                    else:
                        texture_status = 0

                # choose type of light
                if event.key == pygame.K_l:
                    if light_type == 0:
                        light_type = 1
                        glDisable(GL_LIGHT0)
                        glEnable(GL_LIGHT1)
                    else:
                        glDisable(GL_LIGHT1)
                        glEnable(GL_LIGHT0)
                        light_type = 0

                # directional light color
                if event.key == pygame.K_7:
                    light_color = [0.5, 0.0, 0.0, 1.0]
                if event.key == pygame.K_8:
                    light_color = [0.0, 0.5, 0.0, 1.0]
                if event.key == pygame.K_9:
                    light_color = [0.0, 0.0, 0.5, 1.0]
                if event.key == pygame.K_0:
                    light_color = [1.0, 1.0, 1.0, 1.0]

                # directional light position
                if event.key == pygame.K_a:
                    light_direction_position[0] -= 0.2
                if event.key == pygame.K_d:
                    light_direction_position[0] += 0.2
                if event.key == pygame.K_w:
                    light_direction_position[1] += 0.2
                if event.key == pygame.K_s:
                    light_direction_position[1] -= 0.2
                if event.key == pygame.K_q:
                    light_direction_position[2] += 0.2
                if event.key == pygame.K_e:
                    light_direction_position[2] -= 0.2

                # camera movement
                if event.key == pygame.K_UP:
                    glTranslatef(0, -0.5, 0)
                if event.key == pygame.K_DOWN:
                    glTranslatef(0, 0.5, 0)
                if event.key == pygame.K_LEFT:
                    glTranslatef(0.5, 0, 0)
                if event.key == pygame.K_RIGHT:
                    glTranslatef(-0.5, 0, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # control rotation
        rotation_pyramid += rotation_speed_pyramid if rotation_status else 0

        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, 50.0)
        # Draw and rotate pyramid
        glRotatef(rotation_pyramid, 0, 1, 0)
        sierpinski(beginningVertices, levels, texture_status)
        glPopMatrix()

        # Draw ground
        glPushMatrix()
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, 50.0)
        load_ground()
        glPopMatrix()

        # Draw and rotate light source
        if light_type == 0:
            glPushMatrix()
            if rotation_light:
                radius = radius + 0.01
            light_x, light_y = light_position(radius)
            light_sphere(light_x, 0.75, light_y, (1.0, 1.0, 1.0))
            glLightfv(GL_LIGHT0, GL_POSITION, [light_x, 0.75, light_y, 1])
            glPopMatrix()
        # Directional light
        else:
            glPushMatrix()
            directional_light(light_color, light_direction_position)
            light_sphere(light_direction_position[0], light_direction_position[1], light_direction_position[2], light_color)
            glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, light_direction_position)

            glPopMatrix()
        set_light_properties(light_color)
        pygame.display.flip()
        pygame.time.wait(10)


main()

