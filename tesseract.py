import pygame
import os
from math import cos, sin, pi
import numpy as np
import colorsys

os.environ["SDL_VIDEO_CENTERED"] = '1'
WIDTH, HEIGHT = 800, 800

BLACK = (0, 0, 0)
hue = 0

pygame.init()
pygame.display.set_caption("4D Cube Projection")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

angle = 0
speed = 0.008
cube_position = [WIDTH // 2, HEIGHT // 2]
scale = 15000

points = [
    [[-1], [-1], [1], [1]],
    [[1], [-1], [1], [1]],
    [[1], [1], [1], [1]],
    [[-1], [1], [1], [1]],
    [[-1], [-1], [-1], [1]],
    [[1], [-1], [-1], [1]],
    [[1], [1], [-1], [1]],
    [[-1], [1], [-1], [1]],
    [[-1], [-1], [1], [-1]],
    [[1], [-1], [1], [-1]],
    [[1], [1], [1], [-1]],
    [[-1], [1], [1], [-1]],
    [[-1], [-1], [-1], [-1]],
    [[1], [-1], [-1], [-1]],
    [[1], [1], [-1], [-1]],
    [[-1], [1], [-1], [-1]]]

projected_points = [j for j in range(len(points))]


def rotations_3d():
    global angle

    c = cos(angle)
    s = sin(angle)

    rotation_x = [[1, 0, 0],
                  [0, c, -s],
                  [0, s, c]]

    rotation_y = [[c, 0, -s],
                  [0, 1, 0],
                  [s, 0, c]]

    rotation_z = [[c, -s, 0],
                  [s, c, 0],
                  [0, 0, 1]]

    rotation_xy = [[c, -s, 0, 0],
                   [s, c, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]]

    rotation_xz = [[c, 0, -s, 0],
                   [0, 1, 0, 0],
                   [s, 0, c, 0],
                   [0, 0, 0, 1]]

    rotation_yz = [[1, 0, 0, 0],
                   [0, c, -s, 0],
                   [0, s, c, 0],
                   [0, 0, 0, 1]]

    tesseract_rotation = [[1, 0, 0],
                          [0, cos(-pi / 2), -sin(-pi / 2)],
                          [0, sin(-pi / 2), cos(-pi / 2)]]

    return rotation_x, rotation_y, rotation_z, rotation_xy, rotation_xz, rotation_yz, tesseract_rotation


def rotations_4d():
    global angle

    c = cos(angle)
    s = sin(angle)

    rotation_xw = [[c, 0, 0, -s],
                   [0, 1, 0, 0],
                   [0, 0, 1, 0],
                   [s, 0, 0, c]]

    rotation_yw = [[1, 0, 0, 0],
                   [0, c, 0, -s],
                   [0, 0, 1, 0],
                   [0, s, 0, c]]

    rotation_zw = [[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, c, -s],
                   [0, 0, s, c]]

    return rotation_xw, rotation_yw, rotation_zw


def projection(rotation_axis, rotation_plane, rotation_4D, rotation_tesseract):
    index = 0

    for point in points:
        rotated_3D = np.matmul(rotation_plane, point)
        rotated_3D = np.matmul(rotation_4D, rotated_3D)

        distance = 10
        w = 1 / (distance - rotated_3D[3][0])
        projection_matrix4 = [[w, 0, 0, 0],
                              [0, w, 0, 0],
                              [0, 0, w, 0]]

        projected_3D = np.matmul(projection_matrix4, rotated_3D)
        rotated_2D = np.matmul(rotation_tesseract, projected_3D)

        z = 1 / (distance - (rotated_2D[2][0] + rotated_3D[3][0]))
        projection_matrix = [[z, 0, 0],
                             [0, z, 0]]

        rotated_2D = np.matmul(rotation_axis, projected_3D)
        projected_2D = np.matmul(projection_matrix, rotated_2D)

        x = int(projected_2D[0][0] * scale) + cube_position[0]
        y = int(projected_2D[1][0] * scale) + cube_position[1]

        projected_points[index] = [x, y]
        # pygame.draw.circle(screen, (255, 0, 0), (x, y), 8) # Display corners
        index += 1


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def connect_points(p1, p2, proj_points, offset):
    a = proj_points[p1 + offset]
    b = proj_points[p2 + offset]
    pygame.draw.line(screen, hsv2rgb(hue, 1, 1), (a[0], a[1]), (b[0], b[1]), 5)


def draw_edges(proj_points):
    # Small cube
    for m in range(4):
        connect_points(m, (m + 1) % 4, proj_points, 8)
        connect_points(m + 4, (m + 1) % 4 + 4, proj_points, 8)
        connect_points(m, m + 4, proj_points, 8)

    # Big cube
    for m in range(4):
        connect_points(m, (m + 1) % 4, proj_points, 0)
        connect_points(m + 4, (m + 1) % 4 + 4, proj_points, 0)
        connect_points(m, m + 4, proj_points, 0)

    # Connecting small and big cubes
    for m in range(8):
        connect_points(m, m + 8, proj_points, 0)


def main():
    # 3D rotations
    rotation_x, rotation_y, rotation_z, rotation_xy, rotation_xz, rotation_yz, tesseract_rotation = rotations_3d()

    # 4D rotations
    rotation_xw, rotation_yw, rotation_zw = rotations_4d()

    # Projection from 4D to 2D
    projection(rotation_x, rotation_xy, rotation_zw, tesseract_rotation)

    # Draw edges
    draw_edges(projected_points)


run = True
while run:

    clock.tick(FPS)
    screen.fill(BLACK)

    main()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.update()
    hue += 0.0002
    angle += speed
