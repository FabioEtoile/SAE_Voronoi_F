# Générateur de Diagramme de Voronoi

**Projet SAE - Implémentation d’un diagramme de Voronoi avec interface graphique**

---

## 📋 Description

Application Python permettant de générer des **diagrammes de Voronoi** à partir de points 2D.  
L’application propose une interface graphique conviviale (Tkinter) pour charger des points via fichier `.txt` ou saisie manuelle, visualiser le résultat en temps réel et exporter en PNG ou SVG.

---

## ✨ Fonctionnalités

- Chargement de points depuis un fichier `.txt` (format : `x,y` par ligne)
- Saisie manuelle des points (format : `x1,y1 ; x2,y2 ; ...`)
- Visualisation interactive sur canvas (redimensionnable)
- Export au format **PNG** ou **SVG**
- Algorithme robuste gérant les cas dégénérés (points proches, colinéaires)
- Suite de tests unitaires complète

---

## 🛠 Technologies utilisées

- **Python 3.12**
- **Tkinter** – Interface graphique
- **Pillow** – Export PNG
- **svgwrite** – Export SVG
- **SciPy + NumPy** – Calcul du diagramme de Voronoi (via Qhull)
- **unittest** – Tests unitaires

**Algorithme principal :** Dual de la triangulation de Delaunay (Qhull)

---

## 🚀 Installation

```bash
# 1. Cloner ou extraire le projet
# 2. Aller à la racine du projet
cd voronoi_grok_david

# 3. Créer un environnement virtuel (recommandé)
python -m venv .venv
.venv\Scripts\activate    # Windows

# 4. Installer les dépendances
pip install -r requirements.txt