"""Dialogues et fenêtres auxiliaires pour la GUI."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional


def ask_open_file(parent: tk.Widget) -> Optional[Path]:
    """Affiche un dialogue d'ouverture de fichier filtré sur .txt."""
    path = filedialog.askopenfilename(
        parent=parent,
        title="Charger un fichier de coordonnées",
        filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
    )
    return Path(path) if path else None


def ask_save_file(parent: tk.Widget, fmt: str) -> Optional[Path]:
    """Affiche un dialogue de sauvegarde pour PNG ou SVG."""
    if fmt == "PNG":
        filetypes = [("Image PNG", "*.png")]
        default_ext = ".png"
    else:
        filetypes = [("Fichier SVG", "*.svg")]
        default_ext = ".svg"

    path = filedialog.asksaveasfilename(
        parent=parent,
        title=f"Exporter en {fmt}",
        filetypes=filetypes,
        defaultextension=default_ext,
    )
    return Path(path) if path else None


def show_error(parent: tk.Widget, title: str, message: str) -> None:
    """Affiche un message d'erreur."""
    messagebox.showerror(title, message, parent=parent)


def show_info(parent: tk.Widget, title: str, message: str) -> None:
    """Affiche un message d'information."""
    messagebox.showinfo(title, message, parent=parent)
