import tkinter as tk
import pandas as pd
import re
from utils.helpers import get_colors, draw_rounded_rectangle

class QuestionScreen:
    def __init__(self, app):
        self.app = app
        self.master = app.master
        self.colors = get_colors(app.theme)

    def start(self):
        self.app.questions = self.app.data.sample(frac=1).reset_index(drop=True)
        self.app.current_question = 0
        self.app.answers_outcome = [None] * len(self.app.questions)
        self.display_question()

    def display_question(self):
        self.clear_window()

        q_data = self.app.questions.iloc[self.app.current_question]
        correct_indices = [int(x.strip()) - 1 for x in str(q_data['Correct']).split(',') if x.strip().isdigit()]

        choice_columns = sorted([col for col in q_data.index if 'Choice' in col],
                                key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
        choices = [q_data[col] for col in choice_columns if pd.notna(q_data[col])]
        self.correct_answers = [choices[i] for i in correct_indices if 0 <= i < len(choices)]

        title = tk.Label(self.master, text=f"Question {self.app.current_question + 1}/{len(self.app.questions)}",
                         font=("Montserrat", 18, "bold"), bg=self.colors['bg'], fg=self.colors['fg'])
        title.pack(pady=10)

        question = tk.Label(self.master, text=q_data['Title'], wraplength=800,
                            font=("Montserrat", 14, "bold"), bg=self.colors['card'], fg=self.colors['fg'])
        question.pack(pady=10)

        self.buttons = []
        self.selected = set()

        for idx, text in enumerate(choices):
            b = tk.Button(self.master, text=f"{chr(65+idx)}. {text}",
                          font=("Montserrat", 12), bg=self.colors['card_hover'], fg="white",
                          command=lambda i=idx: self.toggle_choice(i))
            b.pack(pady=5)
            self.buttons.append(b)

        submit_btn = tk.Button(self.master, text="Submit", font=("Montserrat", 14, "bold"),
                               bg=self.colors['button'], fg="white", command=self.check_answer)
        submit_btn.pack(pady=20)

    def toggle_choice(self, idx):
        if idx in self.selected:
            self.selected.remove(idx)
            self.buttons[idx].config(bg=self.colors['card_hover'])
        else:
            self.selected.add(idx)
            self.buttons[idx].config(bg=self.colors['accent'])

    def check_answer(self):
        found_correct = found_incorrect = False
        for i, btn in enumerate(self.buttons):
            if btn['text'][3:] in self.correct_answers:
                btn.config(bg=self.colors['success'])
                if i in self.selected:
                    found_correct = True
            elif i in self.selected:
                btn.config(bg=self.colors['error'])
                found_incorrect = True

        q_correct = found_correct and not found_incorrect
        self.app.answers_outcome[self.app.current_question] = q_correct
        self.master.after(2000, self.next_question)

    def next_question(self):
        self.app.current_question += 1
        if self.app.current_question >= len(self.app.questions):
            self.show_results()
        else:
            self.display_question()

    def show_results(self):
        self.clear_window()
        correct = sum(1 for res in self.app.answers_outcome if res)
        total = len(self.app.answers_outcome)

        result_label = tk.Label(self.master, text=f"You got {correct}/{total} correct!",
                                font=("Montserrat", 24), bg=self.colors['bg'], fg=self.colors['fg'])
        result_label.pack(pady=50)

        restart_btn = tk.Button(self.master, text="Play Again", font=("Montserrat", 16),
                                bg=self.colors['success'], fg="white", command=lambda: HomeScreen(self.app).render())
        restart_btn.pack()

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()