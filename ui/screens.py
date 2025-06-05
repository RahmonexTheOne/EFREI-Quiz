import tkinter as tk
import re
import pandas as pd

def home_screen(app):
    app.clear_window()
    frame = tk.Frame(app.master, bg=app.colors[app.theme]['card'])
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.configure(highlightthickness=2, highlightbackground=app.colors[app.theme]['shadow'])

    tk.Label(frame, text="EFREI Quiz", font=("Montserrat", 34, "bold"),
             bg=app.colors[app.theme]['card'], fg=app.colors[app.theme]['fg']).pack(pady=(50, 20))

    tk.Label(frame, text="Challenge yourself with randomly generated quizzes",
             font=("Montserrat", 16), bg=app.colors[app.theme]['card'], fg=app.colors[app.theme]['fg']).pack(pady=(0, 30))

    tk.Button(frame, text="Let's Get Started", font=("Montserrat", 16, "bold"),
              bg=app.colors[app.theme]['button'], fg="white", command=app.start_screen,
              relief="flat", padx=30, pady=10).pack(pady=(0, 50))

    app.answers_outcome = []
    app.update_progress_bar()

def start_screen(app):
    app.clear_window()

    title_label = tk.Label(
        app.master,
        text="Play Quiz",
        font=("Montserrat", 28, "bold"),
        justify="center",
        bg=app.colors[app.theme]['bg'],
        fg=app.colors[app.theme]['fg']
    )
    title_label.pack(pady=(100, 30))

    subtitle = tk.Label(
        app.master,
        text="Choose the unit to prepare:",
        font=("Montserrat", 16),
        bg=app.colors[app.theme]['bg'],
        fg=app.colors[app.theme]['fg']
    )
    subtitle.pack(pady=(0, 10))

    # --- LDAP Unit ---
    ldap_label = tk.Label(
        app.master,
        text="Architectures et Infrastructures sécurisées d'entreprise (DNS, LDAP, APACHE, DHCP)",
        font=("Montserrat", 14),
        wraplength=700,
        bg=app.colors[app.theme]['card'],
        fg=app.colors[app.theme]['fg'],
        padx=30,
        pady=20,
        relief="flat",
        cursor="hand2",
        bd=3
    )
    ldap_label.pack(pady=20)
    ldap_label.configure(highlightthickness=2, highlightbackground=app.colors[app.theme]['shadow'])
    ldap_label.bind("<Enter>", lambda e: ldap_label.configure(bg=app.colors[app.theme]['card_hover']))
    ldap_label.bind("<Leave>", lambda e: ldap_label.configure(bg=app.colors[app.theme]['card']))
    ldap_label.bind("<Button-1>", lambda e: app.play_quiz("assets/ldap.csv"))

    # --- DevOps Unit ---
    devops_label = tk.Label(
        app.master,
        text="Delivery Management, DevOps & Pipeline",
        font=("Montserrat", 14),
        wraplength=700,
        bg=app.colors[app.theme]['card'],
        fg=app.colors[app.theme]['fg'],
        padx=30,
        pady=20,
        relief="flat",
        cursor="hand2",
        bd=3
    )
    devops_label.pack(pady=20)
    devops_label.configure(highlightthickness=2, highlightbackground=app.colors[app.theme]['shadow'])
    devops_label.bind("<Enter>", lambda e: devops_label.configure(bg=app.colors[app.theme]['card_hover']))
    devops_label.bind("<Leave>", lambda e: devops_label.configure(bg=app.colors[app.theme]['card']))
    devops_label.bind("<Button-1>", lambda e: app.play_quiz("assets/devops.csv"))



def play_quiz(app):
    app.questions = app.data.sample(frac=1).reset_index(drop=True)
    app.current_question = 0
    app.answers_outcome = [None] * len(app.questions)
    app.display_question()

#--------------------------------------------------------
# MCQ Question
#--------------------------------------------------------
def display_question(app, q_type, q_data):
    q_type = q_type.strip().upper()
    if q_type == "MCQ":
        display_mcq_question(app, q_data)
    elif q_type == "TF":
        display_mcq_question(app, q_data, override_choices=["Vrai", "Faux"])
    elif q_type == "FILL":
        display_mcq_question(app, q_data)
    elif q_type == "SHORT":
        display_fill_question(app, q_data)
    elif q_type == "MATCH":
        display_fill_question(app, q_data)
    else:
        raise ValueError(f"Unknown question type: {q_type}")
        

def display_mcq_question(app, q_data, override_choices=None):
    app.clear_window()
    app.update_progress_bar()

    container_canvas = tk.Canvas(app.master, bg=app.colors[app.theme]['bg'], highlightthickness=0)
    container_canvas.place(relx=0.5, rely=0.45, anchor="center", width=800, height=500)

    app.draw_rounded_rectangle(container_canvas, 0, 0, 800, 500, radius=40,
        fill=app.colors[app.theme]['card'], outline=app.colors[app.theme]['shadow'])

    content_frame = tk.Frame(container_canvas, bg=app.colors[app.theme]['card'])
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    app.timer_label = tk.Label(content_frame, text="25s", font=("Montserrat", 12, "bold"),
        bg=app.colors[app.theme]['timer_bg'], fg=app.colors[app.theme]['timer_fg'])
    app.timer_label.pack(anchor="ne", pady=5)
    app.remaining_time = 25
    app.update_timer()

    tk.Label(content_frame, text=f"Question {app.current_question+1}/{len(app.questions)}",
        font=("Montserrat", 18, "bold"), bg=app.colors[app.theme]['card'],
        fg=app.colors[app.theme]['fg']).pack()

    question_canvas = tk.Canvas(content_frame, width=700, height=80,
        bg=app.colors[app.theme]['card'], highlightthickness=0)
    question_canvas.pack(pady=(10,5))
    app.draw_rounded_rectangle(question_canvas, 0, 0, 700, 80, radius=20,
        fill=app.colors[app.theme]['question_bg'], outline="")
    question_canvas.create_text(350, 40, text=q_data['Title'], font=("Montserrat", 14, "bold"),
        fill=app.colors[app.theme]['fg'], width=650, justify="center")

    choice_frame = tk.Frame(content_frame, bg=app.colors[app.theme]['card'])
    choice_frame.pack(pady=(5,10))

    if override_choices:
        choice_texts = override_choices
    else:
        choice_columns = sorted([col for col in q_data.index if 'Choice' in col],
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
        choice_texts = [q_data[col] for col in choice_columns if pd.notna(q_data[col])]

    correct_indices = [int(x.strip()) - 1 for x in str(q_data['Correct']).split(',') if x.strip().isdigit()]
    app.correct_answers = [choice_texts[i] for i in correct_indices if 0 <= i < len(choice_texts)]

    app.choice_buttons = []
    app.selected_answers = set()

    for idx, choice_text in enumerate(choice_texts):
        c = tk.Canvas(choice_frame, width=700, height=50,
            bg=app.colors[app.theme]['card'], highlightthickness=0)
        c.pack(pady=5)
        app.draw_rounded_rectangle(c, 5, 5, 695, 45, radius=20,
            fill=app.colors[app.theme]['card_hover'], outline=app.colors[app.theme]['accent'])
        c.create_oval(15, 15, 35, 35, fill=app.colors[app.theme]['accent'])
        c.create_text(25, 25, text=chr(65+idx), fill="white", font=("Montserrat", 10, "bold"))
        c.create_text(50, 25, text=choice_text, anchor="w", font=("Montserrat", 12),
            width=600, fill=app.colors[app.theme]['fg'])
        c.bind("<Button-1>", lambda e, i=idx: app.toggle_selection(i))
        app.choice_buttons.append((c, choice_text))

    app.action_btn = tk.Button(content_frame, text="Submit", font=("Montserrat", 14, "bold"),
        bg=app.colors[app.theme]['button'], fg="white", relief="flat",
        padx=20, pady=10, command=app.on_action_btn)
    app.action_btn.pack(anchor="e", pady=10)

    # --- Correct Streak Message (outside content box) ---
    if getattr(app, "correct_streak", 0) >= 5:
        streak_label = tk.Label(
            app.master,
            text=f"🔥 {app.correct_streak} bonnes réponses d’affilée !",
            font=("Montserrat", 12, "bold"),
            fg=app.colors[app.theme]['success'],
            bg=app.colors[app.theme]['bg']
        )
        streak_label.place(relx=0.5, rely=0.85, anchor="center")
        # Save reference if you want to clear later
        app.streak_label = streak_label
    else:
        # Remove old streak label if it exists and streak drops
        if hasattr(app, 'streak_label'):
            app.streak_label.destroy()
            del app.streak_label



#--------------------------------------------------------
# Fill Question
#--------------------------------------------------------    
def display_fill_question(app, q_data):
    app.clear_window()
    app.update_progress_bar()

    container = tk.Frame(app.master, bg=app.colors[app.theme]["card"])
    container.place(relx=0.5, rely=0.45, anchor="center", width=700, height=350)

    tk.Label(container, text=f"Question {app.current_question+1}/{len(app.questions)}",
             font=("Montserrat", 18, "bold"), bg=app.colors[app.theme]["card"],
             fg=app.colors[app.theme]["fg"]).pack(pady=(20, 10))

    tk.Label(container, text=q_data["Title"], font=("Montserrat", 14),
             bg=app.colors[app.theme]["card"], fg=app.colors[app.theme]["fg"], wraplength=650).pack()

    # Simulated options for fill-in (could be dynamically generated or from file later)
    options = [
        "Infrastructure as Code", "Pipeline", "Deployment", "Provisioning",
        "Version Control", "Automation", "Monitoring", "Containerization"
    ]

    app.fill_var = tk.StringVar()
    app.fill_dropdown = tk.OptionMenu(container, app.fill_var, *options)
    app.fill_dropdown.config(font=("Montserrat", 14), width=40)
    app.fill_dropdown.pack(pady=20)

    app.feedback_label = tk.Label(container, font=("Montserrat", 12, "bold"),
                                  bg=app.colors[app.theme]["card"], fg=app.colors[app.theme]["fg"])
    app.feedback_label.pack()

    app.correct_answers = [str(q_data["Correct"]).strip()]

    def check_choice():
        selected = app.fill_var.get().strip().lower()
        expected = app.correct_answers[0].strip().lower()

        if selected == expected:
            app.feedback_label.configure(text="✅ Correct!", fg=app.colors[app.theme]["success"])
            app.answers_outcome[app.current_question] = True
        else:
            app.feedback_label.configure(
                text=f"❌ Incorrect. Correct answer: {app.correct_answers[0]}",
                fg=app.colors[app.theme]["error"]
            )
            app.answers_outcome[app.current_question] = False

        app.update_progress_bar()
        app.action_btn.configure(text="Next", command=app.on_action_btn)

    app.action_btn = tk.Button(container, text="Submit", font=("Montserrat", 14, "bold"),
                               bg=app.colors[app.theme]["button"], fg="white", relief="flat",
                               command=check_choice)
    app.action_btn.pack(pady=10)


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

def show_result(app):
    app.clear_window()
    app.master.configure(bg=app.colors[app.theme]['bg'])

    score = sum(1 for x in app.answers_outcome if x)
    total = len(app.answers_outcome)
    percentage = round((score / total) * 100)

    # 🎉 Header
    result = tk.Label(
        app.master,
        text="🎉 Quiz Complete! 🎉",
        font=("Montserrat", 28, "bold"),
        bg=app.colors[app.theme]['bg'],
        fg=app.colors[app.theme]['fg']
    )
    result.pack(pady=40)

    score_label = tk.Label(
        app.master,
        text=f"You answered {score} out of {total} questions correctly ({percentage}%)!",
        font=("Montserrat", 20),
        bg=app.colors[app.theme]['bg'],
        fg=app.colors[app.theme]['fg']
    )
    score_label.pack(pady=20)

    # Play Again (full quiz)
    restart_btn = tk.Button(
        app.master,
        text="Play Again",
        font=("Montserrat", 18, "bold"),
        bg=app.colors[app.theme]['success'],
        fg="white",
        command=app.start_screen,
        padx=20,
        pady=10,
        relief="flat"
    )
    restart_btn.pack(pady=20)

    # Retry Incorrect Questions
    if app.incorrect_indices:
        retry_btn = tk.Button(
            app.master,
            text="Retry Incorrect Questions",
            font=("Montserrat", 16, "bold"),
            bg=app.colors[app.theme]['button'],
            fg="white",
            command=app.play_incorrect_quiz,
            padx=20,
            pady=10,
            relief="flat"
        )
        retry_btn.pack()