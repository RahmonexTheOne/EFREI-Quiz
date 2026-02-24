import tkinter as tk
from quiz_app import QuizApp
from utils.music import MusicManager

if __name__ == "__main__":
    root = tk.Tk()

    music_manager = MusicManager()
    music_manager.start()

    app = QuizApp(root)
    app.music = music_manager

    root.mainloop()