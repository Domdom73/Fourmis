import numpy as np
import pygame as pg
import maze_mpi2
import pheromone_mpi2
import colony_mpi2
import direction_mpi2 as d
import display_mpi2
from mpi4py import MPI

UNLOADED, LOADED = False, True

exploration_coefs = 0.

comm=MPI.COMM_WORLD
rank=comm.Get_rank()
nbp=comm.Get_size()


if __name__ == "__main__":
    import sys
    import time

    size_laby = 25, 25
    if len(sys.argv) > 2:
        size_laby = int(sys.argv[1]),int(sys.argv[2])

    pg.init()
    resolution = size_laby[1]*8, size_laby[0]*8
    screen = pg.display.set_mode(resolution)
    
    nb_ants = size_laby[0]*size_laby[1]//4

    max_life = 500
    if len(sys.argv) > 3:
        max_life = int(sys.argv[3])

    local_nb_ants= nb_ants//(nbp-1)
    if rank==1:
        local_nb_ants+=nb_ants%(nbp-1)
    if rank==0:
        local_nb_ants=0
        max_life=0
    

    pos_food = size_laby[0]-1, size_laby[1]-1
    pos_nest = 0, 0

    a_maze = maze_mpi2.Maze(size_laby, 12345)
        

    local_ants = colony_mpi2.Colony(local_nb_ants, pos_nest, max_life)

    if rank==0:
        sprites = []
        img = pg.image.load("ants.png").convert_alpha()
        for i in range(0, 32, 8):
            sprites.append(pg.Surface.subsurface(img, i, 0, 8, 8))

    local_unloaded_ants = np.array(range(local_nb_ants))
    alpha = 1
    beta  = 0.99
    if len(sys.argv) > 4:
        alpha = float(sys.argv[4])
    if len(sys.argv) > 5:
        beta = float(sys.argv[5])

    pherom = pheromone_mpi2.Pheromon(size_laby, pos_food, alpha, beta)

    if rank==0:
        mazeImg = a_maze.display()

    
    global_food_counter = np.zeros(1)
    local_food_counter =np.zeros(1)

    temp_age=None
    temp_directions=None
    temp_historic_path=None
    temp_pherom=None
    if rank==0:
        temp_age=np.zeros(local_ants.age.shape)
        temp_directions=np.zeros(local_ants.directions.shape)
        temp_historic_path=np.zeros(local_ants.historic_path.shape)
        temp_pherom=np.zeros(pherom.pheromon.shape)

    snapshop_taken = False
    while True:

        if rank==0:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)

        deb = time.time()

        if rank==0:

            display_mpi2.display_Pheromon(pherom.pheromon, screen)
            screen.blit(mazeImg, (0, 0))
            display_mpi2.display_Colony(sprites, temp_directions, temp_historic_path, temp_age, screen)
            pg.display.update()
    

        local_food_counter[0] = local_ants.advance(a_maze, pos_food, pos_nest, pherom, global_food_counter[0])
        
        comm.Reduce(local_food_counter, global_food_counter, op=MPI.SUM, root=0)
        

        temp_age=None
        temp_directions=None
        temp_historic_path=None
        temp_pherom=None
        displacements=None
        if rank==0: 
            temp_age=np.zeros(local_ants.age.shape)
            temp_directions=np.zeros(local_ants.directions.shape)
            temp_historic_path=np.zeros(local_ants.historic_path.shape)
            temp_pherom=np.zeros(pherom.pheromon.shape)

        comm.Gatherv(local_ants.directions, temp_directions, root=0)
        comm.Gatherv(local_ants.historic_path, temp_historic_path, root=0)
        comm.Gatherv(local_ants.age, temp_age, root=0)

        pherom.do_evaporation(pos_food)
        comm.Reduce(temp_pherom, pherom.pheromon, op=MPI.MAX, root=0)
        
        if rank==0:
            end=time.time()

            if global_food_counter == 1 and not snapshop_taken:
                pg.image.save(screen, "MyFirstFood.png")
                snapshop_taken = True
            # pg.time.wait(500)
            print(f"FPS : {1./(end-deb):6.2f}, nourriture : {global_food_counter[0]:7f}", end='\r')
