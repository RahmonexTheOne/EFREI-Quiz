import pandas as pd
import tkinter as tk
from ui.screens import home_screen, start_screen, play_quiz
from utils.helpers import get_theme_colors, draw_rounded_rectangle

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EFREI Quiz")
        self.master.attributes("-fullscreen", True)

        self.theme = "dark"
        self.colors = get_theme_colors(self.theme)

        self.exit_btn = tk.Button(
            self.master,
            text="Exit",
            font=("Montserrat", 12, "bold"),
            bg=self.colors[self.theme]["error"],
            fg="white",
            command=self.master.quit,
            relief="flat"
        )
        self.exit_btn.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

        self.progress_canvas = tk.Canvas(
            self.master,
            height=10,
            bg=self.colors[self.theme]['bg'],
            highlightthickness=0
        )
        self.progress_canvas.pack(side="bottom", fill="x")

        self.master.bind("<Configure>", lambda e: self.update_progress_bar())

        self.data = pd.read_csv("assets/ldap.csv")
        self.current_question = 0
        self.selected_answers = set()
        self.answers_outcome = []

        self.master.configure(bg=self.colors[self.theme]['bg'])
        self.home_screen()

    def draw_rounded_rectangle(self, *args, **kwargs):
        return draw_rounded_rectangle(*args, **kwargs)

    def home_screen(self):
        home_screen(self)

    def start_screen(self):
        start_screen(self)

    def play_quiz(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.questions = self.data.sample(frac=1).reset_index(drop=True)
        self.current_question = 0
        self.answers_outcome = [None] * len(self.questions)
        self.display_question()


    def display_question(self):
        from ui.screens import display_question
        q_data = self.questions.iloc[self.current_question]
        q_type = q_data['Type']  # Ensure it's extracted from q_data
        display_question(self, q_type, q_data)


    def update_timer(self):
        self.timer_label.configure(text=f"{self.remaining_time}s")
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            if self.action_btn.cget("text") == "Submit":
                self.check_answer()
                self.action_btn.configure(text="Next", command=self.on_action_btn)

    def on_action_btn(self):
        if self.action_btn.cget("text") == "Submit":
            self.check_answer()
            self.action_btn.configure(text="Next", command=self.on_action_btn)
        else:
            self.next_question()

    def toggle_selection(self, index):
        c, text = self.choice_buttons[index]
        if index in self.selected_answers:
            self.selected_answers.remove(index)
            c.itemconfig(1, fill=self.colors[self.theme]['card_hover'])
        else:
            self.selected_answers.add(index)
            c.itemconfig(1, fill=self.colors[self.theme]['accent'])

    def check_answer(self):
        if hasattr(self, 'timer_id') and self.timer_id:
            self.master.after_cancel(self.timer_id)

        found_correct = False
        found_incorrect = False

        for idx, (c, text) in enumerate(self.choice_buttons):
            if text in self.correct_answers:
                c.itemconfig(1, fill=self.colors[self.theme]['success'])
                if idx in self.selected_answers:
                    found_correct = True
            else:
                if idx in self.selected_answers:
                    c.itemconfig(1, fill=self.colors[self.theme]['error'])
                    found_incorrect = True

        q_correct = (found_correct and not found_incorrect)
        self.answers_outcome[self.current_question] = q_correct
        self.update_progress_bar()

    def next_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.show_result()
        else:
            self.display_question()

    def update_progress_bar(self):
        from ui.screens import update_progress_bar
        update_progress_bar(self)

    def show_result(self):
        from ui.screens import show_result
        show_result(self)

    def clear_window(self):
        for widget in self.master.winfo_children():
            if widget not in (self.exit_btn, self.progress_canvas):
                widget.destroy()
