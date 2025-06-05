
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

        # ─── Load menu PNG (32×32) ───
        menu_image = Image.open("assets/menu.png").convert("RGBA").resize((32, 32))
        self.menu_icon = ImageTk.PhotoImage(menu_image)

        # ─── Progress bar (same as before) ───
        self.progress_canvas = tk.Canvas(
            self.master,
            height=10,
            bg=self.colors[self.theme]['bg'],
            highlightthickness=0
        )
        self.progress_canvas.pack(side="bottom", fill="x")
        self.master.bind("<Configure>", lambda e: self.update_progress_bar())

        # ─── Initial data, etc. ───
        self.data = pd.read_csv("assets/ldap.csv")
        self.current_question = 0
        self.selected_answers = set()
        self.answers_outcome = []
        self.incorrect_indices = []

        # Make sure clear_window() will _not_ destroy this menu_btn:
        # (we’ll update clear_window() below)
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

        w = self.master.winfo_screenwidth()
        h = self.master.winfo_screenheight()

        # 1) Create a full-screen Canvas overlay
        self.overlay_frame = tk.Canvas(
            self.master,
            width=w,
            height=h,
            highlightthickness=0
        )
        self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 2) Draw the background_menu.png stretched to fill the window
        bg_image = Image.open("assets/background_menu.png").resize((w, h))
        self.menu_bg_tk = ImageTk.PhotoImage(bg_image)
        self.overlay_frame.create_image(0, 0, image=self.menu_bg_tk, anchor="nw")

        # 3) Semi-transparent “dimming” layer on top (stipple ≈ 50% opacity)
        self.overlay_frame.create_rectangle(
            0, 0, w, h,
            fill="black",
            stipple="gray25",  # makes the black semi-transparent
            outline=""
        )

        # 4) Draw a centered “menu card” with drop-shadow
        card_w, card_h = 350, 420
        card_x = (w - card_w) // 2
        card_y = (h - card_h) // 2
        radius = 25

        # 4a) Drop-shadow behind the card (offset by 6 px)
        self.draw_rounded_rectangle(
            self.overlay_frame,
            card_x + 6, card_y + 6,
            card_x + card_w + 6, card_y + card_h + 6,
            radius=radius,
            fill="#111111",  # dark shadow
            outline=""
        )

        # 4b) The actual “menu card” on top
        self.draw_rounded_rectangle(
            self.overlay_frame,
            card_x, card_y,
            card_x + card_w, card_y + card_h,
            radius=radius,
            fill=self.colors[self.theme]["card"],     # your dark card color
            outline=self.colors[self.theme]["shadow"]  # subtle outline
        )

        # 5) Draw the “Menu” title at the top of the card
        cx = card_x + card_w // 2
        self.overlay_frame.create_text(
            cx, card_y + 40,
            text="Menu",
            font=("Montserrat", 20, "bold"),
            fill=self.colors[self.theme]["fg"]
        )

        # 6) Create the four menu “buttons” (rounded rectangles + text)
        btn_w = card_w - 60   # leave 30 px padding on each side
        btn_h = 55
        btn_radius = 20
        spacing = 25          # vertical gap between buttons
        start_y = card_y + 90 # first button’s top edge

        def make_button(label, y_offset, base_color, callback):
            x1 = cx - btn_w // 2
            y1 = y_offset
            x2 = cx + btn_w // 2
            y2 = y_offset + btn_h

            # 6a) Draw the rounded-corner rectangle
            rect_id = self.draw_rounded_rectangle(
                self.overlay_frame,
                x1, y1, x2, y2,
                radius=btn_radius,
                fill=base_color,
                outline=""
            )

            # 6b) Draw the label, centered
            text_id = self.overlay_frame.create_text(
                cx, y1 + btn_h // 2,
                text=label,
                font=("Montserrat", 14, "bold"),
                fill="white"
            )

            # 6c) Bind click + hover behavior on both rect and text
            for tag in (rect_id, text_id):
                # Click → run the callback
                self.overlay_frame.tag_bind(tag, "<Button-1>", lambda e: callback())

                # Hover enter → lighten the fill and show hand cursor
                self.overlay_frame.tag_bind(tag, "<Enter>", 
                    lambda e, rid=rect_id: (
                        self.overlay_frame.itemconfig(rid, fill=self.colors[self.theme]["card_hover"]),
                        self.overlay_frame.config(cursor="hand2")
                    )
                )
                # Hover leave → revert fill and cursor
                self.overlay_frame.tag_bind(tag, "<Leave>", 
                    lambda e, rid=rect_id, col=base_color: (
                        self.overlay_frame.itemconfig(rid, fill=col),
                        self.overlay_frame.config(cursor="")
                    )
                )

            return rect_id, text_id

        # 7) “Reset Quiz” (accent color)
        make_button(
            "Reset Quiz",
            start_y,
            self.colors[self.theme]["accent"],
            lambda: [self.close_menu(), self.start_screen()]
        )

        # 8) “Back to Main Menu” (accent color)
        make_button(
            "Back to Main Menu",
            start_y + btn_h + spacing,
            self.colors[self.theme]["accent"],
            lambda: [self.close_menu(), self.home_screen()]
        )

        # 9) “Exit App” (error/red color)
        make_button(
            "Exit App",
            start_y + 2*(btn_h + spacing),
            self.colors[self.theme]["error"],
            self.confirm_exit
        )

        # 10) “❌ Close Menu” (card_hover color)
        make_button(
            "❌ Close Menu",
            start_y + 3*(btn_h + spacing),
            self.colors[self.theme]["card_hover"],
            self.close_menu
        )




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
        # if the timer Canvas was destroyed or doesn’t exist, bail out
        if not hasattr(self, 'timer_canvas') or not self.timer_canvas.winfo_exists():
            return

        # Update the overlaid text to show the new remaining_time (in seconds)
        self.timer_canvas.itemconfig(self.timer_text_id, text=f"{self.remaining_time}s")

        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            # … when time is up, you can auto‐submit or whatever you want:
            self.check_answer()



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
            # getattr(self, 'menu_btn', None)  ← remove this line entirely
        ]
        for widget in self.master.winfo_children():
            if widget not in protected_widgets:
                widget.destroy()

