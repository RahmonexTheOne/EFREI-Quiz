import tkinter as tk
from tkinter import messagebox
import pandas as pd
import random
import re

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EFREI Quiz")
        # Force full screen
        self.master.attributes("-fullscreen", True)

        # Colors, theme
        self.theme = "dark"
        self.colors = {
            "dark": {
                "bg": "#1e1f29",
                "fg": "white",
                "card": "#2c2f3a",
                "card_hover": "#3b3e4c",
                "success": "#2ecc71",  # green
                "error": "#e74c3c",    # red
                "button": "#8e44ad",
                "shadow": "#15161e",
                "accent": "#6c5ce7",
                "question_bg": "#1a1b25",
                "timer_bg": "#1c2c1c",
                "timer_fg": "#2ecc71"
            }
        }

        # Create an 'Exit' button at top-right
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

        # Create the progress bar once at the bottom
        self.progress_canvas = tk.Canvas(
            self.master,
            height=10,
            bg=self.colors[self.theme]['bg'],
            highlightthickness=0
        )
        self.progress_canvas.pack(side="bottom", fill="x")

        # Redraw progress bar on window resize
        self.master.bind("<Configure>", lambda e: self.update_progress_bar())

        # Load quiz data
        self.data = pd.read_csv("data/ldap.csv")

        # Initialize quiz state
        self.current_question = 0
        self.selected_answers = set()
        # For each question: True=correct, False=incorrect, None=unanswered
        self.answers_outcome = []

        self.master.configure(bg=self.colors[self.theme]['bg'])

        self.home_screen()

    # --- UTILITY FUNCTION FOR ROUNDED RECT ---
    def draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """Draws a smooth rounded rectangle on the canvas."""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def home_screen(self):
        """Initial EFREI Quiz home screen."""
        self.clear_window()

        frame = tk.Frame(self.master, bg=self.colors[self.theme]['card'], bd=0)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.configure(highlightthickness=2, highlightbackground=self.colors[self.theme]['shadow'])

        title = tk.Label(
            frame, text="EFREI Quiz",
            font=("Montserrat", 34, "bold"),
            bg=self.colors[self.theme]['card'],
            fg=self.colors[self.theme]['fg']
        )
        title.pack(pady=(50, 20))

        subtitle = tk.Label(
            frame,
            text="Challenge yourself with randomly generated quizzes",
            font=("Montserrat", 16),
            bg=self.colors[self.theme]['card'],
            fg=self.colors[self.theme]['fg']
        )
        subtitle.pack(pady=(0, 30))

        start_btn = tk.Button(
            frame,
            text="Let's Get Started",
            font=("Montserrat", 16, "bold"),
            bg=self.colors[self.theme]['button'],
            fg="white",
            command=self.start_screen,
            relief="flat",
            padx=30,
            pady=10
        )
        start_btn.pack(pady=(0, 50))

        # Reset the progress bar to empty
        self.answers_outcome = []
        self.update_progress_bar()

    def start_screen(self):
        """Shows 'Play Quiz' + unit selection screen."""
        self.clear_window()

        title_label = tk.Label(
            self.master,
            text="Play Quiz",
            font=("Montserrat", 28, "bold"),
            justify="center",
            bg=self.colors[self.theme]['bg'],
            fg=self.colors[self.theme]['fg']
        )
        title_label.pack(pady=(100, 30))

        subtitle = tk.Label(
            self.master,
            text="Choose the unit to prepare:",
            font=("Montserrat", 16),
            bg=self.colors[self.theme]['bg'],
            fg=self.colors[self.theme]['fg']
        )
        subtitle.pack(pady=(0, 10))

        unit_label = tk.Label(
            self.master,
            text="Architectures et Infrastructures sécurisées d'entreprise (DNS, LDAP, APACHE, DHCP)",
            font=("Montserrat", 14),
            wraplength=700,
            bg=self.colors[self.theme]['card'],
            fg=self.colors[self.theme]['fg'],
            padx=30,
            pady=20,
            relief="flat",
            cursor="hand2",
            bd=3
        )
        unit_label.pack(pady=20)
        unit_label.configure(highlightthickness=2, highlightbackground=self.colors[self.theme]['shadow'])

        # Hover effects
        unit_label.bind("<Enter>", lambda e: unit_label.configure(bg=self.colors[self.theme]['card_hover']))
        unit_label.bind("<Leave>", lambda e: unit_label.configure(bg=self.colors[self.theme]['card']))

        # Start quiz
        unit_label.bind("<Button-1>", lambda e: self.play_quiz())

    def play_quiz(self):
        """Shuffle questions, reset counters, show first question."""
        self.questions = self.data.sample(frac=1).reset_index(drop=True)
        self.current_question = 0
        # Each question outcome is None initially
        self.answers_outcome = [None] * len(self.questions)

        self.display_question()

    def display_question(self):
        """All the UI for one question: 
           - big rounded container 
           - timer top-right 
           - question in smaller rounded rect 
           - choices with less spacing 
           - submit/next bottom-right 
        """
        self.clear_window()
        self.update_progress_bar()

        # Big outer canvas for the container
        container_canvas = tk.Canvas(self.master, bg=self.colors[self.theme]['bg'], highlightthickness=0)
        container_canvas.place(relx=0.5, rely=0.45, anchor="center", width=800, height=500)

        # Draw big corner rectangle
        self.draw_rounded_rectangle(
            container_canvas,
            0, 0, 800, 500,
            radius=40,
            fill=self.colors[self.theme]['card'],
            outline=self.colors[self.theme]['shadow']
        )

        # Frame on top for content
        content_frame = tk.Frame(container_canvas, bg=self.colors[self.theme]['card'])
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Timer in top-right
        self.timer_label = tk.Label(
            content_frame,
            text="25s",
            font=("Montserrat", 12, "bold"),
            bg=self.colors[self.theme]['timer_bg'],
            fg=self.colors[self.theme]['timer_fg']
        )
        self.timer_label.pack(anchor="ne", pady=5)
        self.remaining_time = 25
        self.update_timer()

        # Title for question number
        title_label = tk.Label(
            content_frame,
            text=f"Question {self.current_question+1}/{len(self.questions)}",
            font=("Montserrat", 18, "bold"),
            bg=self.colors[self.theme]['card'],
            fg=self.colors[self.theme]['fg']
        )
        title_label.pack()

        # Smaller question box
        question_canvas = tk.Canvas(content_frame, width=700, height=80, bg=self.colors[self.theme]['card'], highlightthickness=0)
        question_canvas.pack(pady=(10,5))  # smaller vertical gap
        self.draw_rounded_rectangle(
            question_canvas, 0, 0, 700, 80,
            radius=20,
            fill=self.colors[self.theme]['question_bg'],
            outline=""
        )

        # Draw the question text
        q_data = self.questions.iloc[self.current_question]
        question_canvas.create_text(
            350, 40,  # center
            text=q_data['Title'],
            font=("Montserrat", 14, "bold"),
            fill=self.colors[self.theme]['fg'],
            width=650,
            justify="center"
        )

        # Choices
        choice_frame = tk.Frame(content_frame, bg=self.colors[self.theme]['card'])
        choice_frame.pack(pady=(5,10))  # less vertical space

        choice_columns = sorted(
            [col for col in q_data.index if 'Choice' in col],
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
        )
        choice_texts = [q_data[col] for col in choice_columns if pd.notna(q_data[col])]

        correct_indices = [int(x.strip()) - 1 for x in str(q_data['Correct']).split(',') if x.strip().isdigit()]
        self.correct_answers = [choice_texts[i] for i in correct_indices if 0 <= i < len(choice_texts)]

        self.choice_buttons = []
        self.selected_answers = set()

        for idx, choice_text in enumerate(choice_texts):
            c = tk.Canvas(choice_frame, width=700, height=50, bg=self.colors[self.theme]['card'], highlightthickness=0)
            c.pack(pady=5)  # less space
            # Rounded rect for each choice
            self.draw_rounded_rectangle(
                c, 5, 5, 695, 45, radius=20,
                fill=self.colors[self.theme]['card_hover'],
                outline=self.colors[self.theme]['accent']
            )
            # A, B, C, D circle
            c.create_oval(15, 15, 35, 35, fill=self.colors[self.theme]['accent'])
            c.create_text(25, 25, text=chr(65+idx), fill="white", font=("Montserrat", 10, "bold"))

            c.create_text(50, 25, text=choice_text, anchor="w", font=("Montserrat", 12), width=600,
                          fill=self.colors[self.theme]['fg'])

            c.bind("<Button-1>", lambda e, i=idx: self.toggle_selection(i))
            self.choice_buttons.append((c, choice_text))

        # Submit / Next button pinned bottom-right
        self.action_btn = tk.Button(
            content_frame,
            text="Submit",
            font=("Montserrat", 14, "bold"),
            bg=self.colors[self.theme]['button'],
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.on_action_btn
        )
        self.action_btn.pack(anchor="e", pady=10)

    def update_timer(self):
        """Same logic for countdown or forced submit."""
        if getattr(self, 'remaining_time', 0) > 0:
            self.timer_label.configure(text=f"{self.remaining_time}s")
            self.remaining_time -= 1
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            if self.action_btn.cget("text") == "Submit":
                self.check_answer()
                self.action_btn.configure(text="Next", command=self.on_action_btn)

    def on_action_btn(self):
        """Two-step: 'Submit' => highlight => 'Next' => next question."""
        if self.action_btn.cget("text") == "Submit":
            self.check_answer()
            self.action_btn.configure(text="Next", command=self.on_action_btn)
        else:
            self.next_question()

    def toggle_selection(self, index):
        """(Design: no changes here) Partial correctness logic is unchanged."""
        c, text = self.choice_buttons[index]
        if index in self.selected_answers:
            self.selected_answers.remove(index)
            c.itemconfig(1, fill=self.colors[self.theme]['card_hover'])
        else:
            self.selected_answers.add(index)
            c.itemconfig(1, fill=self.colors[self.theme]['accent'])

    def check_answer(self):
        """(Design only) No logic changes. We keep your partial correctness approach."""
        if hasattr(self, 'timer_id') and self.timer_id:
            self.master.after_cancel(self.timer_id)

        found_correct = False
        found_incorrect = False

        for idx, (c, text) in enumerate(self.choice_buttons):
            if text in self.correct_answers:
                # correct box = green
                c.itemconfig(1, fill=self.colors[self.theme]['success'])
                # partial correctness
                if idx in self.selected_answers:
                    found_correct = True
            else:
                # not correct
                if idx in self.selected_answers:
                    c.itemconfig(1, fill=self.colors[self.theme]['error'])
                    found_incorrect = True

        q_correct = (found_correct and not found_incorrect)
        self.answers_outcome[self.current_question] = q_correct
        self.update_progress_bar()

    def next_question(self):
        """Unchanged logic."""
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.show_result()
        else:
            self.display_question()

    def update_progress_bar(self):
        """Same logic: if partial correctness => green if at least one correct and no wrong."""
        if not hasattr(self, 'progress_canvas') or not self.progress_canvas.winfo_exists():
            return

        self.progress_canvas.delete("all")
        total_q = len(self.answers_outcome)
        if total_q == 0:
            return

        bar_width = self.progress_canvas.winfo_width()
        if bar_width <= 1:
            bar_width = self.master.winfo_width()

        seg_width = max(bar_width / total_q, 1)
        for i in range(total_q):
            x1 = i * seg_width
            x2 = x1 + seg_width

            outcome = self.answers_outcome[i]
            if outcome is True:
                color = self.colors[self.theme]['success']
            elif outcome is False:
                color = self.colors[self.theme]['error']
            else:
                color = "#666666"

            self.progress_canvas.create_rectangle(
                x1, 0, x2, 30,
                fill=color,
                outline=self.colors[self.theme]['bg']
            )

    def show_result(self):
        """Unchanged final screen."""
        self.clear_window()
        self.master.configure(bg=self.colors[self.theme]['bg'])

        result = tk.Label(
            self.master,
            text="🎊 Quiz Complete! 🎊",
            font=("Montserrat", 28, "bold"),
            bg=self.colors[self.theme]['bg'],
            fg=self.colors[self.theme]['fg']
        )
        result.pack(pady=40)

        correct_count = sum(1 for outcome in self.answers_outcome if outcome)
        total_count = len(self.answers_outcome)

        score_label = tk.Label(
            self.master,
            text=f"You answered {correct_count} out of {total_count} questions correctly!",
            font=("Montserrat", 20),
            bg=self.colors[self.theme]['bg'],
            fg=self.colors[self.theme]['fg']
        )
        score_label.pack(pady=20)

        restart_btn = tk.Button(
            self.master,
            text="Play Again",
            font=("Montserrat", 18, "bold"),
            bg=self.colors[self.theme]['success'],
            fg="white",
            command=self.home_screen,
            padx=20,
            pady=10,
            relief="flat"
        )
        restart_btn.pack(pady=30)

    def clear_window(self):
        """No logic changed. Just skip destroying the exit btn & progress canvas."""
        for widget in self.master.winfo_children():
            if widget not in (self.exit_btn, self.progress_canvas):
                widget.destroy()

# ---------- MAIN LAUNCHER ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
