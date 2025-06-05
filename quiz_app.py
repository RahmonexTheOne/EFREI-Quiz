
import pandas as pd
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.messagebox
from ui.screens import home_screen, start_screen, play_quiz
from utils.helpers import get_theme_colors, draw_rounded_rectangle

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EFREI Quiz")
        self.master.attributes("-fullscreen", True)

        self.theme = "dark"
        self.colors = get_theme_colors(self.theme)
        self.overlay_frame = None

        # Load menu icon
        menu_image = Image.open("assets/menu.png").convert("RGBA").resize((32, 32))
        self.menu_icon = ImageTk.PhotoImage(menu_image)

        self.menu_btn = tk.Button(
            self.master,
            image=self.menu_icon,
            bg=self.colors[self.theme]["card_hover"],
            activebackground=self.colors[self.theme]["card_hover"],
            bd=0,
            command=self.show_menu,
            relief="flat"
        )
        self.menu_btn.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

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
        self.incorrect_indices = []

        self.master.configure(bg=self.colors[self.theme]['bg'])
        self.home_screen()

    def draw_rounded_rectangle(self, *args, **kwargs):
        return draw_rounded_rectangle(*args, **kwargs)

    def styled_button(self, parent, text, command, bg):
        btn = tk.Button(
            parent,
            text=text,
            font=("Montserrat", 14, "bold"),
            bg=bg,
            fg="white",
            activebackground=self.colors[self.theme]["card_hover"],
            relief="flat",
            command=command,
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10
        )
        btn.pack(pady=10, fill="x", padx=20)

    def show_menu(self):
        if self.overlay_frame:
            return

        self.overlay_frame = tk.Canvas(self.master,
                                       width=self.master.winfo_screenwidth(),
                                       height=self.master.winfo_screenheight(),
                                       highlightthickness=0)
        self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        bg_image = Image.open("assets/background_menu.png").resize(
            (self.master.winfo_screenwidth(), self.master.winfo_screenheight())
        )
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)
        self.overlay_frame.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

        menu_x = self.master.winfo_screenwidth() // 2 - 150
        menu_y = self.master.winfo_screenheight() // 2 - 150
        menu_width = 300
        menu_height = 420
        radius = 25

        draw_rounded_rectangle(
            self.overlay_frame,
            menu_x, menu_y,
            menu_x + menu_width, menu_y + menu_height,
            radius=radius,
            fill=self.colors[self.theme]["card"],
            outline=""
        )

        menu_frame = tk.Frame(self.overlay_frame, bg=self.colors[self.theme]["card"])
        self.overlay_frame.create_window(menu_x + menu_width // 2,
                                         menu_y + menu_height // 2,
                                         window=menu_frame,
                                         anchor="center")

        tk.Label(
            menu_frame,
            text="Menu",
            font=("Montserrat", 18, "bold"),
            bg=self.colors[self.theme]["card"],
            fg=self.colors[self.theme]["fg"]
        ).pack(pady=(10, 20))

        self.styled_button(menu_frame, "Reset Quiz", lambda: [self.close_menu(), self.start_screen()], self.colors[self.theme]["button"])
        self.styled_button(menu_frame, "Back to Main Menu", lambda: [self.close_menu(), self.home_screen()], self.colors[self.theme]["button"])
        self.styled_button(menu_frame, "Exit App", self.confirm_exit, self.colors[self.theme]["error"])
        self.styled_button(menu_frame, "❌ Close Menu", self.close_menu, self.colors[self.theme]["card_hover"])

    def close_menu(self):
        if self.overlay_frame:
            self.overlay_frame.destroy()
            self.overlay_frame = None
            self.bg_image_tk = None

    def get_current_screen_id(self):
        if hasattr(self, 'questions') and self.current_question < len(self.questions):
            return "quiz"
        elif self.answers_outcome == []:
            return "home"
        else:
            return "start"

    def restore_previous_screen(self):
        self.menu_overlay.destroy()
        if self.previous_screen == "quiz":
            self.display_question()
        elif self.previous_screen == "start":
            self.start_screen()
        else:
            self.home_screen()

    def confirm_exit(self):
        if tk.messagebox.askyesno("Exit Confirmation", "Are you sure you want to quit the app?"):
            self.master.quit()

    def home_screen(self):
        home_screen(self)

    def start_screen(self):
        start_screen(self)

    def play_quiz(self, csv_path):
        self.data = pd.read_csv(csv_path)
        full_data = self.data.sample(frac=1).reset_index(drop=True)
        self.questions = full_data.head(50)
        self.current_question = 0
        self.answers_outcome = [None] * len(self.questions)
        self.correct_streak = 0
        self.incorrect_indices = []
        self.display_question()

    def play_incorrect_quiz(self):
        self.questions = self.questions.iloc[self.incorrect_indices].reset_index(drop=True)
        self.current_question = 0
        self.answers_outcome = [None] * len(self.questions)
        self.correct_streak = 0
        self.display_question()

    def display_question(self):
        from ui.screens import display_question
        q_data = self.questions.iloc[self.current_question]
        q_type = q_data['Type']
        display_question(self, q_type, q_data)

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            return  # Avoid updating a destroyed widget

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

        if q_correct:
            self.correct_streak += 1
        else:
            self.correct_streak = 0
            self.incorrect_indices.append(self.current_question)

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
        protected_widgets = [
            getattr(self, 'progress_canvas', None),
            getattr(self, 'exit_btn', None),
            getattr(self, 'menu_btn', None)
        ]
        for widget in self.master.winfo_children():
            if widget not in protected_widgets:
                widget.destroy()
