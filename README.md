# Fourmis


## Analyse à priori
Pour pouvoir établir nos stratégies de parallélisation, il est nécessaire de faire une analyse à priori de notre problème et du code en séquentiel. 

En compilant le programme principal `ants.py`, on peut observer que le labyrinthe se "stabilise" après ~4000 à 5000 exécution, c'est-à-dire qu'à partir d'un certain nombre de passage dans la boucle, les fourmis ont fait assez d'aller-retour et les phéromones se sont assez dispersées pour qu'il n'y ait plus que le véritable chemin en couleur et que les fourmis n'empruntent plus que ce chemin là. 
Pour le reste de mes simulations, j'ai donc définit `nbr_exec=5000` pour que le programme s'arrête de lui même une fois que le labyrinthe est stabilisé.
De plus, dans toutes les simulations qui suivent, certains paramètres ne changent pas et on était choisi car il permettent une simulation efficace :
`size_laby=25, 25
max_life=500
pos_nest=0,0
alpha=0,9
beta=0,99`

Ensuite, j'ai rajouté des pas de temps dans `ants.py` pour pouvoir calculer le temps de calcul et temps d'affichage à chaque simulation. 
Je voudrais faire remarquer avant toute chose que mon ordinateur est de plus en plus faible, après 7 ans d'utilisation, les résultats que j'ai obtenu dépendaient beaucoup du contexte et notamment du temps d'utilisation de mon ordinateur et de si celui-ci était branché sur secteur ou pas. J'ai donc obtenu des résultats très variables pouvant aller de 100s à 200s pour le temps total.
J'ai donc fait en sorte de faire toutes mes simulations les unes après les autres pour qu'il n'y ait pas trop de disparités : 

Ici j'obtiens donc :
food_counter=2327
Temps total=120.08254170417786
Temps de calul = 70.02479410171509
Temps d'affichage = 48.793450117111206

On observe donc que le temps d'affichage est assez conséquent dans le temps total, il représente 40,6% du temps d'exécution.
Ainsi on peut effectivement commencer par séparer l'affichage de la gestion des fourmis et phéromones.

## Stratégies de parallélisation 

### Séparation affichage - gestion des fourmis/phéromones

Dans un premier temps, on se propose de paralléliser avec deux processeurs : le processeur 0 s'occupe uniquement de l'affichage et le processeur 1 s'occupe d'effectuer les calculs. Vous pourrez trouver tous les fichiers correspondants dans le fichier *affichage-reste*.
Dans ce cas là, l'équilibre des tâches ne sera évidemment pas parfait puisque le calcul est clairement le facteur limitant dans l'exécution.

Pour séparer l'affichage du calcul, j'ai créé un nouveau fichier python `display_mpi1.py` dans lequel j'ai pris les fonctions `display` des classes `Colony` et `Pheromon`, et `GetColor` de `Pheromon` (fonctions que j'ai commenté dans `colony_mpi1.py` et `pheromone_mpi1.py`). Ainsi dans mon fichier principal `main_mpi1.py`, je peux simplement appeler ces fonctions dont les parties du code associées au processeur de rang 0.

De plus, dans la boucle d'exécution, il faut établir une connexion entre les deux processeurs car le processeur 0 a besoin des phéromones et des informations `directions`, `historic_path` et `age` de la colonie de fourmis pour pouvoir faire l'affichage. 

On obtient donc : 
Temps total=103.05959343910217
2327
Temps de calul = 96.65991544723511
Temps de communication = 6.315622091293335
Temps d'affichage = 63.289780616760254


Cela nous permet donc de calculer le speed-up :

$S(2)=\frac{t_{total-séquentiel}}{t_{total-parallèle}}=$

### Séparation affichage-calcul et répartition des fourmis entre les processeurs

Maintenant que l'on a séparer l'affichage et les calculs, c'est le temps de calcul qui limite l'exécution du programme. On peut donc essayer de répartir les fourmis entre les processus de rang autre que 0. Pour cela, on va créer une colonie par processus `local_ants` et chaque processus s'occupera de faire les calculs sur sa colonie. 

Cependant la gestion des phéromones peut ici nous poser problème. En effet, dans les calculs, les processeurs exécutent la fonction `advance` de `Colony` qui récupère la matrice des phéromones et la modifie. Mais cette modification utilise les marquages des cases voisines. Donc si on ne conserve pas l'ancienne matrice de phéromones, on risque de faire des marquages qui n'auront pas de sens.













