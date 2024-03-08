# Fourmis


## Analyse à priori
Pour pouvoir établir nos stratégies de parallélisation, il est nécessaire de faire une analyse à priori de notre problème et du code en séquentiel. 

En compilant le programme principal `ants.py`, on peut observer que le labyrinthe se "stabilise" après ~4000 à 5000 exécutions, c'est-à-dire qu'à partir d'un certain nombre de passage dans la boucle, les fourmis ont fait assez d'aller-retour et les phéromones se sont assez dispersées pour qu'il n'y ait plus que le véritable chemin en couleur et que les fourmis n'empruntent plus que ce chemin là. 
Pour le reste de mes simulations, j'ai donc définit `nbr_exec=5000` pour que le programme s'arrête de lui même une fois que le labyrinthe est stabilisé.
De plus, dans toutes les simulations qui suivent, certains paramètres ne changent pas et ont été choisis car il permettent une simulation efficace et analysable :
`
size_laby=25, 25
max_life=500
pos_nest=0,0
alpha=0,9
beta=0,99`

Ensuite, j'ai rajouté des pas de temps dans `ants.py` pour pouvoir calculer le temps de calcul et temps d'affichage à chaque simulation. 

Ici j'obtiens donc :

food_counter = 2327

Temps total=72.92769002914429

Temps de calul = 44.51706290245056

Temps d'affichage = 27.271523475646973

On observe donc que le temps d'affichage est assez conséquent : il représente 37,3% du temps d'exécution (en moyenne aux alentours de 40%). Il paraît donc très pertinent de commencer par la séparation de l'affichage et des calculs. 


## Stratégies de parallélisation 

### Séparation affichage - gestion des fourmis/phéromones

Dans un premier temps, on se propose de paralléliser avec deux processeurs : le processeur 0 s'occupe uniquement de l'affichage et le processeur 1 s'occupe d'effectuer les calculs. Tous les fichiers correspondants se trouvent dans le dossier *affichage-reste*.
Dans ce cas là, l'équilibre des tâches ne sera évidemment pas parfait puisque le calcul est clairement le facteur limitant dans l'exécution.

Pour séparer l'affichage du calcul, j'ai créé un nouveau fichier python `display_mpi1.py` dans lequel j'ai pris les fonctions `display` des classes `Colony` et `Pheromon`, et `GetColor` de `Pheromon` (fonctions que j'ai commenté dans `colony_mpi1.py` et `pheromone_mpi1.py`). Ainsi dans mon fichier principal `main_mpi1.py`, je peux simplement appeler ces fonctions dont les parties du code associées au processeur de rang 0.

De plus, dans la boucle d'exécution, il faut établir une connexion entre les deux processeurs car le processeur 0 a besoin des phéromones et des informations `directions`, `historic_path` et `age` de la colonie de fourmis pour pouvoir faire l'affichage. 

On obtient donc avec la ligne de commande : `mpirun -np 2 python3 main_mpi1.py`
food_counter = 2327

Temps total = 49.962143898010254

Temps de calul = 47.044970750808716

Temps de communication = 2.62005615234375

Temps d'affichage = 32.070555210113525


Cela nous permet donc de calculer le speed-up :

$S(2)=\frac{t_{total-séquentiel}}{t_{total-parallèle}}=\frac{72.92769002914429}{49.962143898010254}=1,46$

C'est un speed-up tout à fait convenable qui nous permet de valider cette parallélisation. De plus le temps de communication est largement négligeable par rapport aux temps de calcul et d'affichage ce qui est aussi bon signe.

### Séparation affichage-calcul et répartition des fourmis entre les processeurs

Si le temps d'exécution a diminué après la séparation de l'affichage et du calcul, c'est toujours le temps de calcul qui limite l'exécution du programme. On peut donc essayer de répartir les fourmis entre les processus de rang autre que 0 pour idéalement diviser le temps de calcul par le nombre de processeur (moins 1 car le processeur 0 ne fera pas de calculs de colonie). Pour cela, on va créer une colonie par processus `local_ants` et chaque processus s'occupera de faire les calculs sur sa colonie. 

Cependant la gestion des phéromones peut ici nous poser problème. En effet, dans les calculs, les processeurs exécutent la fonction `advance` de `Colony` qui récupère la matrice des phéromones et la modifie. Mais cette modification utilise les marquages des cases voisines : si on ne conserve pas l'ancienne matrice de phéromones, on risque de faire des marquages qui n'auront pas de sens. 


### Partitions du labyrinthe
On peut enfin se poser la question d'une potentielle partition du labyrinthe. On pourrait s'inspirer du jeu de la vie en commençant par diviser le labyrinthe en deux puis en quatre. Cependant les questions que l'on se pose seront quand même bien différentes. En effet, si dans le jeu de la vie on utilisait des *cellules fantômes* pour communiquer les informations entre les processus, ici nous aurons le problème des fourmis qui passent d'une partie à une autre. 
De plus, il faudra aussi se poser la question de l'équilibre des charges. En effet, si on fait des captures du labyrinthe à des moments assez aléatoires comme ci-dessus, on peut voir que certaines parties du labyrinthe ne sont pas atteintes par les fourmis. De plus, les fourmis peuvent parfois se concentrer dans certaines parties du labyrinthe ce qui surchargerait un processeur par rapport aux autres. 
















