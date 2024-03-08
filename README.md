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

Dans un premier temps, on se propose de paralléliser avec deux processeurs : le processeur 0 s'occupe uniquement de l'affichage et le processeur 1 s'occupe d'effectuer les calculs.
Dans ce cas là, l'équilibre des tâches ne sera évidemment pas parfait puisque le calcul est clairement le facteur limitant dans l'exécution.










