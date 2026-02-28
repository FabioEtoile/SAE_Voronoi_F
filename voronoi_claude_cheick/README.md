# Voronoi Diagram Studio

Implémentation complète du diagramme de Voronoi via **l'algorithme Fortune's Sweep Line**, sans bibliothèque Voronoi externe dans le script principal.

---

## Structure du projet

```
voronoi_app/
├── voronoi.py         # Algorithme Fortune (from scratch) + parser .txt
├── renderer.py        # Export PNG (Pillow) et SVG (stdlib)
├── gui.py             # Interface graphique tkinter
├── tests.py           # Tests unitaires (+ comparaison scipy)
├── sample_points.txt  # Exemple de fichier de points
└── README.md
```

---

## Installation

```bash
pip install Pillow          # Pour l'export PNG
pip install scipy numpy     # Pour les tests de comparaison (optionnel)
```

---

## Lancement

### Interface graphique
```bash
cd voronoi_claude_cheick
python gui.py
```

### Tests unitaires
```bash
python tests.py
# Ou avec unittest directement :
python -m unittest tests -v
```

---

## Format du fichier .txt

Un point par ligne, coordonnées séparées par une virgule :

```
213,247
54,424
180,29
212,237
50,370
95,26
162,300
485,174
```

Les lignes vides et les lignes commençant par `#` sont ignorées.

---

## Bibliothèques autorisées

| Module         | Usage                          |
|----------------|-------------------------------|
| `math`         | Calculs géométriques           |
| `heapq`        | File de priorité (Fortune's)   |
| `tkinter`      | Interface graphique            |
| `Pillow`       | Export PNG                     |
| stdlib (`pathlib`, `threading`, etc.) | Utilitaires |
| `scipy` (tests uniquement) | Oracle de validation |

❌ Aucune bibliothèque Voronoi dans le script principal.

---

## Algorithme

**Fortune's Sweep Line** (O(n log n)) :

1. **Events** : Site events (ajout de parabole) + Circle events (vertex Voronoi)
2. **Beach line** : Liste chaînée d'arcs paraboliques
3. **Priority queue** : Traitement des événements par ordre de y décroissant
4. **Clipping** : Cohen-Sutherland sur la bounding box

### Propriétés géométriques vérifiées
- Chaque arête est sur la médiatrice de ses deux sites adjacents
- Chaque vertex Voronoi est équidistant des 3+ sites qui l'entourent
- Cohérence avec scipy.spatial.Voronoi (nombre d'arêtes finies)

---

## Tests

| Classe                    | Description                                |
|---------------------------|--------------------------------------------|
| `TestPoint`               | Primitives géométriques                    |
| `TestEdge`                | Propriétés des arêtes + clipping           |
| `TestCohenSutherland`     | Algorithme de clipping                     |
| `TestCircumcenter`        | Calcul du circumcenter                     |
| `TestFortuneBasic`        | Cas de base de Fortune's algorithm         |
| `TestVoronoiDiagram`      | API haut niveau + bounding box             |
| `TestVoronoiCorrectness`  | Propriétés géométriques du Voronoi         |
| `TestScipyComparison`     | Comparaison avec scipy (oracle)            |
| `TestFileParser`          | Parsing des fichiers .txt                  |
| `TestEdgeProperties`      | Tests de propriétés sur les arêtes         |
