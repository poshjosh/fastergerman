import tkinter as tk
from fastergerman.preposition_trainer import PrepositionTrainer

if __name__ == "__main__":
    root = tk.Tk()
    app = PrepositionTrainer(root)
    root.mainloop()
