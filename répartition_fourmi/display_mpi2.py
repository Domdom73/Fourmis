import numpy as np
import pygame as pg
import maze_mpi2
import pheromone_mpi2
import colony_mpi2
import direction_mpi2 as d

#display colony
def display_Colony(sprites, directions, historic_path, age, screen):
    [screen.blit(sprites[directions[i]], (8*historic_path[i, age[i], 1], 8*historic_path[i, age[i], 0])) for i in range(directions.shape[0])]

#display phéromone
def getColor(pheromon, i: int, j: int):
    val = max(min(pheromon[i, j], 1), 0)
    return [255*(val > 1.E-16), 255*val, 128.]
def display_Pheromon(pheromon, screen):
    [[screen.fill(getColor(pheromon, i, j), (8*(j-1), 8*(i-1), 8, 8)) for j in range(1, pheromon.shape[1]-1)] for i in range(1, pheromon.shape[0]-1)]