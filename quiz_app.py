
import pandas as pd
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.messagebox
import sys, os

from ui.screens import home_screen, specialty_screen, semester_screen, unit_screen, play_quiz
from utils.helpers import get_theme_colors, draw_rounded_rectangle
from utils.helpers import resource_path

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EFREI Quiz")
        self.master.attributes("-fullscreen", True)

        self.theme = "dark"
        self.colors = get_theme_colors(self.theme)
        self.overlay_frame = None

        # ─── Load menu PNG (32×32) ───
        menu_image = Image.open(resource_path("assets/menu.png")).convert("RGBA").resize((32, 32))
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
        self.data = pd.read_csv(resource_path("assets/ldap.csv"))
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

    def config_quiz_screen(self, csv_path):
        # Clear everything
        self.clear_window()
        self.update_progress_bar()

        # Store path so the "Start" button can pick it up
        self._pending_csv = csv_path

        # Set background image to fill entire screen
        w = self.master.winfo_screenwidth()
        h = self.master.winfo_screenheight()
        
        # Create background canvas that fills everything
        bg_canvas = tk.Canvas(
            self.master,
            width=w,
            height=h,
            highlightthickness=0
        )
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Load and set background image
        bg_image = Image.open(resource_path("assets/background_menu.png")).resize((w, h))
        self.config_bg_tk = ImageTk.PhotoImage(bg_image)
        bg_canvas.create_image(0, 0, image=self.config_bg_tk, anchor="nw")

        # Title - directly on the background canvas
        bg_canvas.create_text(
            w//2, h//2 - 220,
            text="Quiz Configuration",
            font=("Montserrat", 28, "bold"),
            fill="white",
            anchor="center"
        )

        # Subtitle - directly on the background canvas
        bg_canvas.create_text(
            w//2, h//2 - 185,
            text="Personalize your quiz experience",
            font=("Montserrat", 14),
            fill="white",
            anchor="center"
        )

        # Timer Configuration Section - directly on background
        bg_canvas.create_text(
            w//2, h//2 - 130,
            text="⏱️ Duration per Question",
            font=("Montserrat", 18, "bold"),
            fill="white",
            anchor="center"
        )

        # Timer selection variables and buttons
        self._timer_var = tk.IntVar(value=25)
        self.timer_buttons = {}
        
        timer_options = [
            (15, "Fast", "15s"),
            (25, "Balanced", "25s"),
            (50, "Thoughtful", "50s")
        ]

        button_width = 180
        button_height = 80
        start_x = w//2 - (3 * button_width + 2 * 30) // 2  # Center 3 buttons with 30px spacing

        for i, (value, label, time_text) in enumerate(timer_options):
            x = start_x + i * (button_width + 30)
            y = h//2 - 90

            # Create button canvas positioned absolutely
            btn_canvas = tk.Canvas(
                self.master,
                width=button_width,
                height=button_height,
                highlightthickness=0,
                bg=self.master.cget('bg')
            )
            btn_canvas.place(x=x, y=y)

            # Button color
            btn_color = self.colors[self.theme]['accent'] if value == 25 else self.colors[self.theme]['card_hover']
            
            # Draw rounded button
            btn_rect = self.draw_rounded_rectangle(
                btn_canvas,
                0, 0, button_width, button_height,
                radius=15,
                fill=btn_color,
                outline=""
            )

            # Button text - time
            btn_canvas.create_text(
                button_width//2, 30,
                text=time_text,
                font=("Montserrat", 14, "bold"),
                fill="white"
            )

            # Button text - label
            btn_canvas.create_text(
                button_width//2, 55,
                text=label,
                font=("Montserrat", 11),
                fill="white"
            )

            # Store button elements
            self.timer_buttons[value] = (btn_canvas, btn_rect, btn_color)

            # Bind click events
            def make_timer_click(v):
                return lambda e: self.select_timer(v)
            
            btn_canvas.bind("<Button-1>", make_timer_click(value))
            btn_canvas.bind("<Enter>", lambda e, c=btn_canvas: c.configure(cursor="hand2"))
            btn_canvas.bind("<Leave>", lambda e, c=btn_canvas: c.configure(cursor=""))

        # Questions Count Configuration Section - directly on background
        bg_canvas.create_text(
            w//2, h//2 + 20,
            text="📊 Number of Questions",
            font=("Montserrat", 18, "bold"),
            fill="white",
            anchor="center"
        )

        # Count selection variables and buttons
        self._count_var = tk.IntVar(value=50)
        self.count_buttons = {}
        
        count_options = [
            (50, "Short", "50"),
            (100, "Standard", "100"),
            (200, "Intensive", "200")
        ]

        for i, (value, label, count_text) in enumerate(count_options):
            x = start_x + i * (button_width + 30)
            y = h//2 + 60

            # Create button canvas positioned absolutely
            btn_canvas = tk.Canvas(
                self.master,
                width=button_width,
                height=button_height,
                highlightthickness=0,
                bg=self.master.cget('bg')
            )
            btn_canvas.place(x=x, y=y)

            # Button color
            btn_color = self.colors[self.theme]['accent'] if value == 50 else self.colors[self.theme]['card_hover']
            
            # Draw rounded button
            btn_rect = self.draw_rounded_rectangle(
                btn_canvas,
                0, 0, button_width, button_height,
                radius=15,
                fill=btn_color,
                outline=""
            )

            # Button text - count
            btn_canvas.create_text(
                button_width//2, 30,
                text=count_text,
                font=("Montserrat", 14, "bold"),
                fill="white"
            )

            # Button text - label
            btn_canvas.create_text(
                button_width//2, 55,
                text=label,
                font=("Montserrat", 11),
                fill="white"
            )

            # Store button elements
            self.count_buttons[value] = (btn_canvas, btn_rect, btn_color)

            # Bind click events
            def make_count_click(v):
                return lambda e: self.select_count(v)
            
            btn_canvas.bind("<Button-1>", make_count_click(value))
            btn_canvas.bind("<Enter>", lambda e, c=btn_canvas: c.configure(cursor="hand2"))
            btn_canvas.bind("<Leave>", lambda e, c=btn_canvas: c.configure(cursor=""))

        # Stats display - directly on background
        self.stats_text_id = bg_canvas.create_text(
            w//2, h//2 + 170,
            text="",
            font=("Montserrat", 12, "bold"),
            fill="white",
            anchor="center"
        )
        self.stats_canvas = bg_canvas  # Store reference for updates
        self.update_config_stats()

        # Start button - positioned absolutely
        start_canvas = tk.Canvas(
            self.master,
            width=220,
            height=50,
            highlightthickness=0,
            bg=self.master.cget('bg')
        )
        start_canvas.place(x=w//2-110, y=h//2 + 200)

        # Draw rounded start button
        self.draw_rounded_rectangle(
            start_canvas,
            0, 0, 220, 50,
            radius=15,
            fill=self.colors[self.theme]["accent"],
            outline=""
        )

        start_canvas.create_text(
            110, 25,
            text="🚀 Start Quiz",
            font=("Montserrat", 14, "bold"),
            fill="white"
        )

        # Bind start button events
        def start_quiz_click(e):
            self.play_quiz(
                self._pending_csv,
                timer=self._timer_var.get(),
                num_qs=self._count_var.get()
            )

        start_canvas.bind("<Button-1>", start_quiz_click)
        start_canvas.bind("<Enter>", lambda e: (
            start_canvas.delete("all"),
            self.draw_rounded_rectangle(start_canvas, 0, 0, 220, 50, radius=15, fill=self.colors[self.theme]["success"], outline=""),
            start_canvas.create_text(110, 25, text="🚀 Start Quiz", font=("Montserrat", 14, "bold"), fill="white"),
            start_canvas.configure(cursor="hand2")
        ))
        start_canvas.bind("<Leave>", lambda e: (
            start_canvas.delete("all"),
            self.draw_rounded_rectangle(start_canvas, 0, 0, 220, 50, radius=15, fill=self.colors[self.theme]["accent"], outline=""),
            start_canvas.create_text(110, 25, text="🚀 Start Quiz", font=("Montserrat", 14, "bold"), fill="white"),
            start_canvas.configure(cursor="")
        ))

        # Back button - positioned absolutely
        back_canvas = tk.Canvas(
            self.master,
            width=100,
            height=40,
            highlightthickness=0,
            bg=self.master.cget('bg')
        )
        back_canvas.place(x=w//2-50, y=h//2 + 270)

        # Draw red back button
        self.draw_rounded_rectangle(
            back_canvas,
            0, 0, 100, 40,
            radius=12,
            fill=self.colors[self.theme]["error"],  # Red color
            outline=""
        )

        back_canvas.create_text(
            50, 20,
            text="← Back",
            font=("Montserrat", 11, "bold"),
            fill="white"
        )

        # Bind back button events
        def back_click(e):
            __import__('ui.screens', fromlist=['specialty_screen']).specialty_screen(self)

        back_canvas.bind("<Button-1>", back_click)
        back_canvas.bind("<Enter>", lambda e: (
            back_canvas.delete("all"),
            self.draw_rounded_rectangle(back_canvas, 0, 0, 100, 40, radius=12, fill="#d32f2f", outline=""),  # Darker red
            back_canvas.create_text(50, 20, text="← Back", font=("Montserrat", 11, "bold"), fill="white"),
            back_canvas.configure(cursor="hand2")
        ))
        back_canvas.bind("<Leave>", lambda e: (
            back_canvas.delete("all"),
            self.draw_rounded_rectangle(back_canvas, 0, 0, 100, 40, radius=12, fill=self.colors[self.theme]["error"], outline=""),
            back_canvas.create_text(50, 20, text="← Back", font=("Montserrat", 11, "bold"), fill="white"),
            back_canvas.configure(cursor="")
        ))

    def select_timer(self, value):
        """Handle timer button selection"""
        self._timer_var.set(value)
        # Update button colors
        for btn_value, (canvas, rect, original_color) in self.timer_buttons.items():
            canvas.delete("all")
            color = self.colors[self.theme]['accent'] if btn_value == value else self.colors[self.theme]['card_hover']
            
            self.draw_rounded_rectangle(
                canvas,
                0, 0, 180, 80,
                radius=15,
                fill=color,
                outline=""
            )
            
            # Redraw text
            time_options = {15: ("15s", "Fast"), 25: ("25s", "Balanced"), 50: ("50s", "Thoughtful")}
            time_text, label = time_options[btn_value]
            
            canvas.create_text(
                90, 30,
                text=time_text,
                font=("Montserrat", 14, "bold"),
                fill="white"
            )
            
            canvas.create_text(
                90, 55,
                text=label,
                font=("Montserrat", 11),
                fill="white"
            )
        
        self.update_config_stats()

    def select_count(self, value):
        """Handle count button selection"""
        self._count_var.set(value)
        # Update button colors
        for btn_value, (canvas, rect, original_color) in self.count_buttons.items():
            canvas.delete("all")
            color = self.colors[self.theme]['accent'] if btn_value == value else self.colors[self.theme]['card_hover']
            
            self.draw_rounded_rectangle(
                canvas,
                0, 0, 180, 80,
                radius=15,
                fill=color,
                outline=""
            )
            
            # Redraw text
            canvas.create_text(
                90, 30,
                text=f"{btn_value}",
                font=("Montserrat", 14, "bold"),
                fill="white"
            )
            
            count_labels = {50: "Short", 100: "Standard", 200: "Intensive"}
            canvas.create_text(
                90, 55,
                text=count_labels[btn_value],
                font=("Montserrat", 11),
                fill="white"
            )
        
        self.update_config_stats()

    def update_config_stats(self):
        """Update the statistics display"""
        timer_val = self._timer_var.get()
        count_val = self._count_var.get()
        estimated_time = (timer_val * count_val) // 60
        
        stats_text = f"📈 Estimated duration: ~{estimated_time} minutes | Questions: {count_val} | Time/question: {timer_val}s"
        
        # Update the text on the background canvas
        if hasattr(self, 'stats_canvas') and hasattr(self, 'stats_text_id'):
            self.stats_canvas.itemconfig(self.stats_text_id, text=stats_text)


    def admin_security_screen(self):
        from ui.screens import admin_security_screen
        admin_security_screen(self) 
        

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
        bg_image = Image.open(resource_path("assets/background_menu.png")).resize((w, h))
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
            lambda: [self.close_menu(), specialty_screen(self)]
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
            specialty_screen(self)
        else:
            self.home_screen()

    def confirm_exit(self):
        if tk.messagebox.askyesno("Exit Confirmation", "Are you sure you want to quit the app?"):
            self.master.quit()

    def home_screen(self):
        home_screen(self)

    def play_quiz(self, csv_path, timer=25, num_qs=50):
        # timer: initial seconds per question
        # num_qs: how many questions to draw
        self.data = pd.read_csv(csv_path)
        full_data = self.data.sample(frac=1).reset_index(drop=True)
        # take only num_qs questions
        self.questions = full_data.head(num_qs)
        self.current_question = 0
        self.answers_outcome = [None] * len(self.questions)
        self.correct_streak = 0
        self.incorrect_indices = []
        # set the timer
        self.remaining_time = timer
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

