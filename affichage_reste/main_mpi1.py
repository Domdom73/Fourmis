import numpy as np
import pygame as pg
import maze_mpi1
import pheromone_mpi1
import colony_mpi1
import direction_mpi1 as d
import display_mpi1
from mpi4py import MPI

UNLOADED, LOADED = False, True
exploration_coefs = 0.

comm=MPI.COMM_WORLD
rank=comm.Get_rank()
size=comm.Get_size()


if __name__ == "__main__":
    import sys
    import time

    #initialisation des pas de temps
    deb_total=time.time()
    tps_total=0
    tps_calcul=0
    tps_display=0
    tps_comm=0

    #initialisation taille du labyrinthe
    size_laby = 25, 25
    if len(sys.argv) > 2:
        size_laby = int(sys.argv[1]),int(sys.argv[2])

    #initialisation de pygame
    pg.init()
    resolution = size_laby[1]*8, size_laby[0]*8
    screen = pg.display.set_mode(resolution)
    
    #initialisation des différentes données et du labyrinthe
    nb_ants = size_laby[0]*size_laby[1]//4
    max_life = 500
    if len(sys.argv) > 3:
        max_life = int(sys.argv[3])
    pos_food = size_laby[0]-1, size_laby[1]-1
    pos_nest = 0, 0
    a_maze = maze_mpi1.Maze(size_laby, 12345)
   
    #initialisation de la colonie
    ants = colony_mpi1.Colony(nb_ants, pos_nest, max_life)

    #partie de l'initialisation de la colonie qui correspond à l'affichage et qu'on peut donc paralléliser
    if rank==0:
        sprites = []
        img = pg.image.load("ants.png").convert_alpha()
        for i in range(0, 32, 8):
            sprites.append(pg.Surface.subsurface(img, i, 0, 8, 8))

    unloaded_ants = np.array(range(nb_ants))

    #initialisation données phéromones
    alpha = 0.9
    beta  = 0.99
    if len(sys.argv) > 4:
        alpha = float(sys.argv[4])
    if len(sys.argv) > 5:
        beta = float(sys.argv[5])

    #initialisation de la matrice de phéromones
    pherom = pheromone_mpi1.Pheromon(size_laby, pos_food, alpha, beta)

    #premier affichage de labyrinthe
    if rank==0:
        deb_display=time.time()
        mazeImg = a_maze.display()
        tps_display+=time.time()-deb_display

    
    food_counter = 0
    
    
    temp_age=ants.age
    temp_directions=ants.directions
    temp_historic_path=ants.historic_path
    temp_pheromon=pherom.pheromon

    snapshop_taken = False
    nbr_exec=5000
    for i in range(5000):
        if rank==0:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)

        deb = time.time()

        #affichage de la colonie et des phéromones
        if rank==0:
            deb_display=time.time()
            display_mpi1.display_Pheromon(temp_pheromon, screen)
            screen.blit(mazeImg, (0, 0))
            display_mpi1.display_Colony(sprites, temp_directions, temp_historic_path, temp_age, screen)
            pg.display.update()
            tps_display+=time.time()-deb_display
        
        #calculs de l'avancement de la colonie
        if rank==1:
            deb_calcul=time.time()
            food_counter = ants.advance(a_maze, pos_food, pos_nest, pherom, food_counter)
            pherom.do_evaporation(pos_food)
            tps_calcul+=time.time()-deb_calcul

            #envoi des données au processeur 0, données nécessaires pour l'affichage
            deb_comm=time.time()
            comm.send(food_counter, dest=0, tag=0)
            comm.send(pherom.pheromon, dest=0, tag=1)
            comm.send(ants.directions, dest=0, tag=3)
            comm.send(ants.historic_path, dest=0, tag=4)
            comm.send(ants.age, dest=0, tag=5)
            comm.send(deb_comm,dest=0,tag=6)
        
        
        if rank==0:
            #réception des données qui serviront à l'affichage dans la prochaine itération
            food_counter=comm.recv(source=1, tag=0)
            temp_pheromon=comm.recv(source=1, tag=1)
            temp_directions=comm.recv(source=1, tag=3)
            temp_historic_path=comm.recv(source=1, tag=4)
            temp_age=comm.recv(source=1, tag=5)
            deb_comm=comm.recv(source=1, tag=6)
            tps_comm+=time.time()-deb_comm

            #screenshot de la première fourmi qui atteint la nourriture
            if food_counter == 1 and not snapshop_taken:
                pg.image.save(screen, "MyFirstFood.png")
                snapshop_taken = True
            # pg.time.wait(500)
            end=time.time()
            print(f"FPS : {1./(end-deb):6.2f}, nourriture : {food_counter:7d}", end='\r')

    #calcul et affichage des différents temps
    tps_total=time.time()-deb_total
    if rank==1:
        comm.send(tps_calcul, dest=0)
    if rank==0:
        tps_calcul=comm.recv(source=1)
        print(f"Temps total={tps_total}")
        print(f"Temps de calcul = {tps_calcul}")
        print(f"Temps de communication = {tps_comm}")
        print(f"Temps d'affichage = {tps_display}")

