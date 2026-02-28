import tkinter as tk
from gui.interface import VoronoiGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = VoronoiGUI(root)
    root.mainloop()