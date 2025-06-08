import tkinter as tk
import re
import pandas as pd
from PIL import Image, ImageTk
import textwrap
import sys, os

from utils.helpers import resource_path

# Hierarchical course mapping: Specialty -> Semester -> [(Display Name, CSV path)]
COURSE_MAP = {
    "Network & Security": {
        "M1 First Semester (S7)": [
            ("Architectures et Infrastructures sécurisées d'entreprise (DNS, LDAP, APACHE, DHCP)",
             resource_path("assets/ldap.csv")),
        ],
        "M1 Second Semester (S8)": [
            ("Administration et Sécurité Windows",
             resource_path("assets/admin-windows-security.csv")),
            ("Delivery Management, DevOps & Pipeline",
             resource_path("assets/devops.csv")),
            ("Orchestration et Containers",
             resource_path("assets/docker_orchestration.csv"))
        ]
    },
}


# ────────────────────────────────────────────────────────────────────────────
# BACK‐BUTTON HELPER (with hover + clickable cursor)
# ────────────────────────────────────────────────────────────────────────────
def add_back_button(canvas, app, callback):
    """
    Draws a small “Back” button in the top-left corner of the given Canvas,
    wired to run `callback()` when clicked, with a colored hover effect.
    """
    btn_w, btn_h = 100, 40
    x1, y1 = 20, 20
    x2, y2 = x1 + btn_w, y1 + btn_h

    # draw the rounded rect
    rect_id = app.draw_rounded_rectangle(
        canvas,
        x1, y1, x2, y2,
        radius=10,
        fill=app.colors[app.theme]['error'],    # use “error” red for back
        outline=""
    )
    # label
    text_id = canvas.create_text(
        (x1 + x2)/2, (y1 + y2)/2,
        text="← Back",
        font=("Montserrat", 12, "bold"),
        fill="white"
    )

    # bind click + hover on both shapes
    for tag in (rect_id, text_id):
        canvas.tag_bind(tag, "<Button-1>", lambda e: callback())
        canvas.tag_bind(tag, "<Enter>", lambda e, r=rect_id: (
            canvas.itemconfig(r, fill=app.colors[app.theme]['card_hover']),
            canvas.config(cursor="hand2")
        ))
        canvas.tag_bind(tag, "<Leave>", lambda e, r=rect_id: (
            canvas.itemconfig(r, fill=app.colors[app.theme]['error']),
            canvas.config(cursor="")
        ))

    return rect_id, text_id


def add_menu_card(canvas, app, x1, y1, x2, y2, label, callback, color=None):
    fill = color or app.colors[app.theme]['card']
    # 1) rounded rect
    rect_id = app.draw_rounded_rectangle(
        canvas, x1, y1, x2, y2,
        radius=20,
        fill=fill,
        outline=app.colors[app.theme]['shadow']
    )
    # 2) centered text
    text_id = canvas.create_text(
        (x1 + x2)//2, (y1 + y2)//2,
        text=label,
        font=("Montserrat", 16, "bold"),
        fill=app.colors[app.theme]['fg'],
        width=(x2 - x1) - 40,
        justify="center"
    )
    # 3) click + hover
    for tag in (rect_id, text_id):
        canvas.tag_bind(tag, "<Button-1>", lambda e, cb=callback: cb())
        canvas.tag_bind(tag, "<Enter>",
            lambda e, r=rect_id: (
                canvas.itemconfig(r, fill=app.colors[app.theme]['card_hover']),
                canvas.config(cursor="hand2")
            )
        )
        canvas.tag_bind(tag, "<Leave>",
            lambda e, r=rect_id, col=fill: (
                canvas.itemconfig(r, fill=col),
                canvas.config(cursor="")
            )
        )
    return rect_id, text_id

def home_screen(app):
    # 1) Wipe out anything except the progress bar / menu button:
    app.clear_window()

    # 2) Load & draw a full‐screen background image on a Canvas:
    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()

    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_home_tk = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(app.master, width=screen_w, height=screen_h, highlightthickness=0)
    canvas.create_image(0, 0, image=app.bg_home_tk, anchor="nw")
    canvas.pack(fill="both", expand=True)

    # draw the 32×32 PNG at top‐right (10px from each edge):
    menu_id = canvas.create_image(
        screen_w - 10 - 16,   # x = windowWidth − 10px − halfOfIconWidth
        10 + 16,              # y = 10px + halfOfIconHeight
        image=app.menu_icon,
        anchor="center"
    )
    canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())


    # 3) Compute center coordinates:
    cx = screen_w // 2
    cy = screen_h // 2

    # 4) Instead of text, load & draw title.png (transparent) at center:
    title_image = Image.open(resource_path("assets/title.png")).convert("RGBA")
    app.title_tk = ImageTk.PhotoImage(title_image)
    # Adjust the y‐offset (here: –30) so the image sits roughly where the text used to be
    canvas.create_image(cx, cy - 80, image=app.title_tk, anchor="center")

    # 5) “Let’s Get Started” button below the image:
    start_btn = tk.Button(
        app.master,
        text="Let's Get Started",
        font=("Montserrat", 16, "bold"),
        bg=app.colors[app.theme]["button"],
        fg="white",
        relief="flat",
        bd=0,
        padx=30,
        pady=10,
        cursor="hand2",
        command=lambda: specialty_screen(app)
    )
    canvas.create_window(cx, cy + 100, window=start_btn)

    # 7) Reset answers_outcome and redraw the progress bar at the bottom:
    app.answers_outcome = []
    app.update_progress_bar()


def specialty_screen(app):
    """Step 1: choose specialty."""
    # 1) Clear + progress bar
    app.clear_window()
    app.update_progress_bar()

    # 2) Full-screen background
    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()
    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_specialty_tk = ImageTk.PhotoImage(bg_image)
    canvas = tk.Canvas(app.master, width=screen_w, height=screen_h, highlightthickness=0)
    canvas.create_image(0, 0, image=app.bg_specialty_tk, anchor="nw")
    canvas.pack(fill="both", expand=True)

    # 3) Menu icon
    menu_id = canvas.create_image(
        screen_w - 10 - 16,
        10 + 16,
        image=app.menu_icon,
        anchor="center"
    )
    canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())

    # 4) Title
    cx = screen_w // 2
    cy = screen_h // 3
    canvas.create_text(
        cx, cy - 40,
        text="Choose Your Specialty",
        font=("Montserrat", 28, "bold"),
        fill=app.colors[app.theme]['fg']
    )

    # 5) Specialty cards
    card_w, card_h, gap = 600, 80, 30
    x1, x2 = cx-card_w//2, cx+card_w//2
    for i, spec in enumerate(COURSE_MAP):
        y1 = cy + i*(card_h+gap)
        cb = lambda s=spec: semester_screen(app, s)
        add_menu_card(canvas, app, x1, y1, x2, y1+card_h, spec, cb)

        # ─── back to home ───
    add_back_button(canvas, app, app.home_screen)
    app.update_progress_bar()


def semester_screen(app, specialty):
    """Step 2: choose semester."""
    app.clear_window()
    app.update_progress_bar()
    app.current_specialty = specialty

    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()
    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_semester_tk = ImageTk.PhotoImage(bg_image)
    canvas = tk.Canvas(app.master, width=screen_w, height=screen_h, highlightthickness=0)
    canvas.create_image(0, 0, image=app.bg_semester_tk, anchor="nw")
    canvas.pack(fill="both", expand=True)

    menu_id = canvas.create_image(
        screen_w - 10 - 16,
        10 + 16,
        image=app.menu_icon,
        anchor="center"
    )
    canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())

    cx, cy = screen_w // 2, screen_h // 3
    canvas.create_text(
        cx, cy - 40,
        text="Choose Semester",
        font=("Montserrat", 28, "bold"),
        fill=app.colors[app.theme]['fg']
    )

    semesters = list(COURSE_MAP[specialty].keys())
    card_w, card_h, gap = 600, 80, 30
    x1, x2 = cx-card_w//2, cx+card_w//2
    for i, sem in enumerate(semesters):
        y1 = cy + i*(card_h+gap)
        cb = lambda sem=sem: unit_screen(app, sem)
        add_menu_card(canvas, app, x1, y1, x2, y1+card_h, sem, cb)

    # ─── back to specialty ───
    add_back_button(canvas, app, lambda: specialty_screen(app))
    app.update_progress_bar()



def unit_screen(app, semester):
    """Step 3: choose unit."""
    app.clear_window()
    app.update_progress_bar()
    app.current_semester = semester

    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()
    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_unit_tk = ImageTk.PhotoImage(bg_image)
    canvas = tk.Canvas(app.master, width=screen_w, height=screen_h, highlightthickness=0)
    canvas.create_image(0, 0, image=app.bg_unit_tk, anchor="nw")
    canvas.pack(fill="both", expand=True)

    menu_id = canvas.create_image(
        screen_w - 10 - 16,
        10 + 16,
        image=app.menu_icon,
        anchor="center"
    )
    canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())

    cx, cy = screen_w // 2, screen_h // 3
    canvas.create_text(
        cx, cy - 40,
        text="Choose Unit",
        font=("Montserrat", 28, "bold"),
        fill=app.colors[app.theme]['fg']
    )

    units = COURSE_MAP[app.current_specialty][semester]
    card_w, card_h, gap = 800, 80, 30
    x1, x2 = cx-card_w//2, cx+card_w//2
    for i, (label, path) in enumerate(units):
        y1 = cy + i*(card_h+gap)
        cb = lambda p=path: app.play_quiz(p)
        add_menu_card(canvas, app, x1, y1, x2, y1+card_h, label, cb)

    # ─── back to semester ───
    add_back_button(canvas, app, lambda: semester_screen(app, app.current_specialty))
    app.update_progress_bar()





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
    # 1) Clear the window except for the progress bar:
    app.clear_window()
    app.update_progress_bar()

    # 2) Draw the full‐screen background image on one Canvas:
    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()

    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_question_tk = ImageTk.PhotoImage(bg_image)

    bg_canvas = tk.Canvas(
        app.master,
        width=screen_w,
        height=screen_h,
        highlightthickness=0
    )
    bg_canvas.create_image(0, 0, image=app.bg_question_tk, anchor="nw")
    bg_canvas.pack(fill="both", expand=True)

    # 3) Draw the menu icon in the top‐right of that Canvas:
    menu_id = bg_canvas.create_image(
        screen_w - 10 - 16,
        10 + 16,
        image=app.menu_icon,
        anchor="center"
    )
    bg_canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())

    # ────────────────────────────────────────────────────────────────────────────
    # 4) Determine how tall the card must be, based on content:
    # ────────────────────────────────────────────────────────────────────────────
    inset = 8  # pixels of padding around the frame

    # a) Title “Question X/Y” + timer area: roughly 40px for title + 30px top padding
    title_region_h = 40 + 30

    # b) Question text box: we fix its width to inner_w - 100, then wrap text
    #    to count lines. Each line ~ 20px tall, plus top/bottom padding for that box.

    # Compute inner_w (temporarily assume card_w = 800, will recalc later).
    card_w = 800
    inner_w_temp = card_w - inset * 2
    question_box_w = inner_w_temp - 100

    # Wrap the question text at approx (characters per line) = question_box_w // avg_char_px.
    # A rough average of 8 pixels per character for Montserrat‐14.
    approx_chars_per_line = max(int(question_box_w / 8), 20)
    wrapped = textwrap.wrap(q_data['Title'], width=approx_chars_per_line)
    num_lines = max(len(wrapped), 1)
    # Each line about 24px high (font size 14 + some spacing). Plus 20px vertical padding.
    question_region_h = num_lines * 24 + 20

    # c) Choices: each choice canvas we use height=50 + 10px vertical margin => 60px per choice
    import re, pandas as pd
    if override_choices:
        choice_texts = override_choices
    else:
        choice_columns = sorted(
            [col for col in q_data.index if 'Choice' in col],
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
        )
        choice_texts = [q_data[col] for col in choice_columns if pd.notna(q_data[col])]

    n_choices = len(choice_texts)
    choices_region_h = n_choices * 60 + 10  # +10 extra top padding

    # d) Submit button region: 45px high + 20px bottom padding
    submit_region_h = 45 + 20

    # e) Timer and some top padding: the timer label is 20px tall + 10px top margin
    timer_region_h = 60 + 10

    # f) Title region above question box already counted in title_region_h

    # Sum everything to get total content height inside the card:
    total_content_h = (
        timer_region_h +
        title_region_h +
        question_region_h +
        choices_region_h +
        submit_region_h +
        20  # some buffer between choices and submit
    )

    # Now final card height = inset*2 + total_content_h
    card_h = inset * 2 + total_content_h
    card_w = 800  # keep width fixed

    # Compute card's coordinates:
    cx, cy = screen_w // 2, screen_h // 2
    x1 = cx - (card_w // 2)
    y1 = cy - (card_h // 2)
    x2 = cx + (card_w // 2)
    y2 = cy + (card_h // 2)
    radius = 40

    # 5a) Drop‐shadow behind the card (offset by 6 px):
    app.draw_rounded_rectangle(
        bg_canvas,
        x1 + 6, y1 + 6,
        x2 + 6, y2 + 6,
        radius=radius,
        fill="#111111",
        outline=""
    )
    # 5b) The card itself:
    app.draw_rounded_rectangle(
        bg_canvas,
        x1, y1, x2, y2,
        radius=radius,
        fill=app.colors[app.theme]['card'],
        outline=app.colors[app.theme]['shadow']
    )

    # 6) Place a Frame slightly inset so its square corners stay hidden behind the card’s rounded edges:
    inner_x1 = x1 + inset
    inner_y1 = y1 + inset
    inner_w = card_w - inset * 2
    inner_h = card_h - inset * 2

    content_frame = tk.Frame(
        app.master,
        bg=app.colors[app.theme]['card']
    )
    content_frame.place(
        x=inner_x1,
        y=inner_y1,
        width=inner_w,
        height=inner_h
    )

    # ────────────────────────────────────────────────────────────────────────────
    # 7) Timer label (top‐right):
    # ────────────────────────────────────────────────────────────────────────────
    # Load & resize your timer PNG to a 60×60 square:
    #    (assumes "assets/timer_box.png" is a transparent circle or stopwatch‐shaped image)
    timer_img = Image.open(resource_path("assets/timer_box.png")).convert("RGBA").resize((60, 60))
    app.timer_img_tk = ImageTk.PhotoImage(timer_img)

    # Create a Canvas exactly 60×60 px, with the same background as the card:
    timer_canvas = tk.Canvas(
        content_frame,
        width=60,
        height=60,
        bg=app.colors[app.theme]['card'],   # so no white “canvas” shows
        highlightthickness=0
    )
    timer_canvas.pack(anchor="ne", pady=5, padx=5)

    # Now draw the actual timer‐circle PNG on top of that shadow:
    timer_canvas.create_image(0, 0, image=app.timer_img_tk, anchor="nw")

    # Overlay the countdown text in dark blue (#1E90FF) at the center of the 60×60 box:
    app.timer_text_id = timer_canvas.create_text(
        30, 35,                      # center of a 60×60 square
        text="25s",
        font=("Montserrat", 12, "bold"),
        fill="#1E90FF"               # dark‐blue instead of green
    )

    # Initialize your countdown variable and kick off the timer loop:
    app.remaining_time = 25
    app.timer_canvas = timer_canvas     # so update_timer() can find it
    app.update_timer()

    # ────────────────────────────────────────────────────────────────────────────
    # 8) “Question X/Y” title:
    # ────────────────────────────────────────────────────────────────────────────
    tk.Label(
        content_frame,
        text=f"Question {app.current_question + 1}/{len(app.questions)}",
        font=("Montserrat", 18, "bold"),
        bg=app.colors[app.theme]['card'],
        fg=app.colors[app.theme]['fg']
    ).pack(pady=(10, 10))

    # ────────────────────────────────────────────────────────────────────────────
    # 9) Draw the rounded‐corner sub‐box for the question text:
    # ────────────────────────────────────────────────────────────────────────────
    canvas_w = inner_w - 40   # match the width used by each choice box

    q_canvas = tk.Canvas(
        content_frame,
        width=canvas_w,
        height=question_region_h,
        bg=app.colors[app.theme]['card'],
        highlightthickness=0
    )
    # give a bit more top/bottom and left/right padding
    q_canvas.pack(pady=(10, 15), padx=20)

    app.draw_rounded_rectangle(
        q_canvas,
        0, 0,
        canvas_w, question_region_h,
        radius=20,
        fill=app.colors[app.theme]['question_bg'],
        outline=""
    )
    q_canvas.create_text(
        canvas_w // 2,
        question_region_h // 2,
        text=q_data['Title'],
        font=("Montserrat", 14, "bold"),
        fill=app.colors[app.theme]['fg'],
        width=canvas_w - 20,   # give 10px side padding inside the box
        justify="center"
    )

    # ────────────────────────────────────────────────────────────────────────────
    # 10) Choices area (packed inside choice_holder):
    # ────────────────────────────────────────────────────────────────────────────
    choice_holder = tk.Frame(content_frame, bg=app.colors[app.theme]['card'])
    choice_holder.pack(padx=20, pady=(5, 10), fill="x")

    import pandas as pd, re
    if override_choices:
        choice_texts = override_choices
    else:
        choice_columns = sorted(
            [col for col in q_data.index if 'Choice' in col],
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
        )
        choice_texts = [q_data[col] for col in choice_columns if pd.notna(q_data[col])]

    correct_indices = [int(x.strip()) - 1 for x in str(q_data['Correct']).split(',') if x.strip().isdigit()]
    app.correct_answers = [choice_texts[i] for i in correct_indices if 0 <= i < len(choice_texts)]

    app.choice_buttons = []
    app.selected_answers = set()

    for idx, choice_text in enumerate(choice_texts):
        c = tk.Canvas(
            choice_holder,
            height=50,
            bg=app.colors[app.theme]['card'],
            highlightthickness=0
        )
        c.pack(fill="x", pady=5)
        canvas_w = inner_w - 40  # same width as question sub‐box + margins

        app.draw_rounded_rectangle(
            c,
            5, 5,
            canvas_w - 5, 50 - 5,
            radius=20,
            fill=app.colors[app.theme]['card_hover'],
            outline=app.colors[app.theme]['accent']
        )
        c.create_oval(15, 15, 35, 35, fill=app.colors[app.theme]['accent'])
        c.create_text(
            25, 25,
            text=chr(65 + idx),
            fill="white",
            font=("Montserrat", 10, "bold")
        )
        c.create_text(
            50, 25,
            text=choice_text,
            anchor="w",
            font=("Montserrat", 12),
            width=canvas_w - 100,
            fill=app.colors[app.theme]['fg']
        )
        c.bind("<Button-1>", lambda e, i=idx: app.toggle_selection(i))
        app.choice_buttons.append((c, choice_text))

    # ────────────────────────────────────────────────────────────────────────────
    # 11) “Submit” button as a Canvas, packed under the choices:
    # ────────────────────────────────────────────────────────────────────────────
    btn_w, btn_h = 140, 45
    btn_radius = 20

    submit_canvas = tk.Canvas(
        content_frame,
        width=btn_w,
        height=btn_h,
        highlightthickness=0,
        bg=app.colors[app.theme]['card']
    )
    submit_canvas.pack(anchor="e", pady=(0, 10), padx=20)

    rect_id = app.draw_rounded_rectangle(
        submit_canvas,
        0, 0, btn_w, btn_h,
        radius=btn_radius,
        fill=app.colors[app.theme]['button'],
        outline=""
    )
    text_id = submit_canvas.create_text(
        btn_w // 2,
        btn_h // 2,
        text="Submit",
        font=("Montserrat", 14, "bold"),
        fill="white"
    )

    # 12) Handle Submit → Next transition:
    def on_submit(e=None):
        # Prevent double‐click
        submit_canvas.config(state="disabled")

        # a) Check the answer
        app.check_answer()

        # b) Change text to “Next”
        submit_canvas.itemconfig(text_id, text="Next")

        # c) Rebind clicks to next_question()
        submit_canvas.tag_unbind(rect_id, "<Button-1>")
        submit_canvas.tag_unbind(text_id, "<Button-1>")
        submit_canvas.tag_bind(rect_id, "<Button-1>", lambda e: app.next_question())
        submit_canvas.tag_bind(text_id, "<Button-1>", lambda e: app.next_question())

        # Re‐enable
        submit_canvas.config(state="normal")

    # Initial binding for “Submit”
    submit_canvas.tag_bind(rect_id, "<Button-1>", on_submit)
    submit_canvas.tag_bind(text_id, "<Button-1>", on_submit)

    # Hover effects for the button
    def on_hover_enter(e):
        submit_canvas.itemconfig(rect_id, fill=app.colors[app.theme]['card_hover'])
        submit_canvas.config(cursor="hand2")
    def on_hover_leave(e):
        submit_canvas.itemconfig(rect_id, fill=app.colors[app.theme]['button'])
        submit_canvas.config(cursor="")

    submit_canvas.tag_bind(rect_id, "<Enter>", on_hover_enter)
    submit_canvas.tag_bind(text_id, "<Enter>", on_hover_enter)
    submit_canvas.tag_bind(rect_id, "<Leave>", on_hover_leave)
    submit_canvas.tag_bind(text_id, "<Leave>", on_hover_leave)

    # ────────────────────────────────────────────────────────────────────────────
    # 13) “Correct streak” indicator (if any) – unchanged
    # ────────────────────────────────────────────────────────────────────────────
    if getattr(app, "correct_streak", 0) >= 5:
        streak_label = tk.Label(
            app.master,
            text=f"🔥 {app.correct_streak} bonnes réponses d’affilée !",
            font=("Montserrat", 12, "bold"),
            fg=app.colors[app.theme]['success'],
            bg="" 
        )
        streak_label.place(relx=0.5, rely=0.85, anchor="center")
        app.streak_label = streak_label
    else:
        if hasattr(app, 'streak_label'):
            app.streak_label.destroy()
            del app.streak_label

#--------------------------------------------------------
# Fill Question
#--------------------------------------------------------    
import tkinter as tk
from PIL import Image, ImageTk

def display_fill_question(app, q_data):
    # 1) Clear the window (keeps only progress bar):
    app.clear_window()
    app.update_progress_bar()

    # 2) Draw full‐screen background image:
    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()

    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_fill_tk = ImageTk.PhotoImage(bg_image)

    bg_canvas = tk.Canvas(app.master, width=screen_w, height=screen_h, highlightthickness=0)
    bg_canvas.create_image(0, 0, image=app.bg_fill_tk, anchor="nw")
    bg_canvas.pack(fill="both", expand=True)

    # 3) Draw the menu icon in the top‐right corner:
    menu_id = bg_canvas.create_image(
        screen_w - 10 - 16,
        10 + 16,
        image=app.menu_icon,
        anchor="center"
    )
    bg_canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())

    # 4) Create the card container in the center for the fill‐in question:
    card_w, card_h = 700, 350

    # — remove bg="" here; the rounded rectangle will cover the canvas —
    container = tk.Canvas(
        app.master,
        width=card_w,
        height=card_h,
        highlightthickness=0
    )
    container.place(relx=0.5, rely=0.5, anchor="center")

    # Draw the rounded card
    app.draw_rounded_rectangle(
        container,
        0, 0, card_w, card_h,
        radius=30,
        fill=app.colors[app.theme]["card"],
        outline=app.colors[app.theme]["shadow"]
    )

    # Place a Frame inside for labels, dropdown, feedback, etc.
    wrap_frame = tk.Frame(container, bg=app.colors[app.theme]["card"])
    container.create_window(card_w//2, card_h//2, window=wrap_frame)

    # 5) Question number + title
    tk.Label(
        wrap_frame,
        text=f"Question {app.current_question+1}/{len(app.questions)}",
        font=("Montserrat", 18, "bold"),
        bg=app.colors[app.theme]["card"],
        fg=app.colors[app.theme]["fg"]
    ).pack(pady=(20, 10))

    tk.Label(
        wrap_frame,
        text=q_data["Title"],
        font=("Montserrat", 14),
        bg=app.colors[app.theme]["card"],
        fg=app.colors[app.theme]["fg"],
        wraplength=650
    ).pack()

    # 6) Dropdown for fill‐in choices (sample options)
    options = [
        "Infrastructure as Code", "Pipeline", "Deployment", "Provisioning",
        "Version Control", "Automation", "Monitoring", "Containerization"
    ]
    app.fill_var = tk.StringVar()
    app.fill_dropdown = tk.OptionMenu(wrap_frame, app.fill_var, *options)
    app.fill_dropdown.config(font=("Montserrat", 14), width=40)
    app.fill_dropdown.pack(pady=20)

    # 7) Feedback label (initially blank)
    app.feedback_label = tk.Label(
        wrap_frame,
        font=("Montserrat", 12, "bold"),
        bg=app.colors[app.theme]["card"],
        fg=app.colors[app.theme]["fg"]
    )
    app.feedback_label.pack()

    app.correct_answers = [str(q_data["Correct"]).strip()]

    # 8) Submit button
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

    app.action_btn = tk.Button(
        wrap_frame,
        text="Submit",
        font=("Montserrat", 14, "bold"),
        bg=app.colors[app.theme]["button"],
        fg="white",
        relief="flat",
        command=check_choice,
        cursor="hand2",
        padx=20,
        pady=10
    )
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
    # 1) Wipe out everything except progress bar / menu icon:
    app.clear_window()

    # 2) Full‐screen background:
    screen_w = app.master.winfo_screenwidth()
    screen_h = app.master.winfo_screenheight()

    bg_image = Image.open(resource_path("assets/background_menu.png")).resize((screen_w, screen_h))
    app.bg_result_tk = ImageTk.PhotoImage(bg_image)

    bg_canvas = tk.Canvas(app.master, width=screen_w, height=screen_h, highlightthickness=0)
    bg_canvas.create_image(0, 0, image=app.bg_result_tk, anchor="nw")
    bg_canvas.pack(fill="both", expand=True)

    # 3) Draw the menu icon in the top‐right:
    menu_id = bg_canvas.create_image(
        screen_w - 10 - 16,
        10 + 16,
        image=app.menu_icon,
        anchor="center"
    )
    bg_canvas.tag_bind(menu_id, "<Button-1>", lambda e: app.show_menu())

    # 4) Compute and draw a centered “result card” with drop‐shadow:
    card_w, card_h = 500, 520
    cx, cy = screen_w // 2, screen_h // 2
    x1 = cx - card_w // 2
    y1 = cy - card_h // 2
    x2 = cx + card_w // 2
    y2 = cy + card_h // 2
    radius = 30

    # 4a) Drop‐shadow (offset by 6 px)
    app.draw_rounded_rectangle(
        bg_canvas,
        x1 + 6, y1 + 6,
        x2 + 6, y2 + 6,
        radius=radius,
        fill="#111111",
        outline=""
    )

    # 4b) The card itself
    app.draw_rounded_rectangle(
        bg_canvas,
        x1, y1, x2, y2,
        radius=radius,
        fill=app.colors[app.theme]["card"],
        outline=app.colors[app.theme]["shadow"]
    )

    # 5) Place an inner Frame so its square edges stay hidden behind the rounding
    inset = 8
    inner_x1 = x1 + inset
    inner_y1 = y1 + inset
    inner_w = card_w - inset * 2
    inner_h = card_h - inset * 2

    content_frame = tk.Frame(app.master, bg=app.colors[app.theme]["card"])
    content_frame.place(x=inner_x1, y=inner_y1, width=inner_w, height=inner_h)

    # 6) Compute the score / percentage
    score = sum(1 for x in app.answers_outcome if x)
    total = len(app.answers_outcome)
    percentage = int(round((score / total) * 100)) if total > 0 else 0

    # 7) Draw a big “Quiz Complete!” header (centered near top of card)
    tk.Label(
        content_frame,
        text="🎉 Quiz Complete! 🎉",
        font=("Montserrat", 24, "bold"),
        bg=app.colors[app.theme]["card"],
        fg=app.colors[app.theme]["fg"]
    ).pack(pady=(20, 10))

    # 8) Draw a circular percentage chart using a small Canvas
    #    - We’ll draw a light‐gray circle, then an arc in “accent” color for the percentage.
    circle_d = 200  # diameter
    margin = 10
    circle_x = inner_w // 2 - circle_d // 2
    circle_y = 60 + margin

    chart_canvas = tk.Canvas(
        content_frame,
        width=circle_d + margin * 2,
        height=circle_d + margin * 2,
        bg=app.colors[app.theme]["card"],
        highlightthickness=0
    )
    chart_canvas.place(x=circle_x - margin, y=circle_y - margin)

    # 8a) Background circle (light gray)
    chart_canvas.create_oval(
        margin, margin, circle_d + margin, circle_d + margin,
        outline=app.colors[app.theme]["shadow"],
        width=8,
        fill=""
    )

    # 8b) Percentage arc (from 90° descending by % of 360)
    extent_angle = int(360 * (percentage / 100))
    chart_canvas.create_arc(
        margin, margin, circle_d + margin, circle_d + margin,
        start=90,  # start at top
        extent=-extent_angle,  # negative for clockwise
        style="arc",
        outline=app.colors[app.theme]["accent"],
        width=8
    )

    # 8c) Overlay the percentage text in center
    chart_canvas.create_text(
        circle_d // 2 + margin,
        circle_d // 2 + margin,
        text=f"{percentage}%",
        font=("Montserrat", 20, "bold"),
        fill=app.colors[app.theme]["fg"]
    )

    # 9) Display the “You answered X/Y correctly” text underneath the circle:
    tk.Label(
        content_frame,
        text=f"You answered {score} of {total} questions correctly!",
        font=("Montserrat", 14),
        bg=app.colors[app.theme]["card"],
        fg=app.colors[app.theme]["fg"]
    ).place(relx=0.5, y=circle_y + circle_d + margin + 40, anchor="n")
    # 10) Create two rounded‐corner “button” areas at the bottom of the card.
    #     We’ll draw them as Canvas shapes + text + click bindings.

    btn_w, btn_h = 160, 50
    btn_radius = 20
    btn_spacing = 20

    # a) “Play Again” button (accent color)
    play_x = inner_w // 2 - btn_w - btn_spacing // 2
    play_y = inner_h - btn_h - 30

    play_canvas = tk.Canvas(
        content_frame,
        width=btn_w,
        height=btn_h,
        highlightthickness=0,
        bg=app.colors[app.theme]["card"]
    )
    play_canvas.place(x=play_x, y=play_y)

    play_rect = app.draw_rounded_rectangle(
        play_canvas,
        0, 0, btn_w, btn_h,
        radius=btn_radius,
        fill=app.colors[app.theme]["accent"],
        outline=""
    )
    play_text = play_canvas.create_text(
        btn_w // 2,
        btn_h // 2,
        text="Play Again",
        font=("Montserrat", 14, "bold"),
        fill="white"
    )

    # Hover + click for Play Again
    def play_enter(e):
        play_canvas.itemconfig(play_rect, fill=app.colors[app.theme]["card_hover"])
        play_canvas.config(cursor="hand2")
    def play_leave(e):
        play_canvas.itemconfig(play_rect, fill=app.colors[app.theme]["accent"])
        play_canvas.config(cursor="")

    play_canvas.tag_bind(play_rect, "<Enter>", play_enter)
    play_canvas.tag_bind(play_text, "<Enter>", play_enter)
    play_canvas.tag_bind(play_rect, "<Leave>", play_leave)
    play_canvas.tag_bind(play_text, "<Leave>", play_leave)
    play_canvas.tag_bind(play_rect, "<Button-1>", lambda e: app.specialty_screen(app))
    play_canvas.tag_bind(play_text, "<Button-1>", lambda e: app.specialty_screen(app))

    # b) “Retry Incorrect” or “Back to Main Menu” button (button color / fallback)
    if app.incorrect_indices:
        btn_label = "Retry Incorrect"
        btn_command = lambda: app.play_incorrect_quiz()
        btn_fill = app.colors[app.theme]["button"]
    else:
        btn_label = "Back to Main Menu"
        btn_command = lambda: app.home_screen()
        btn_fill = app.colors[app.theme]["button"]

    back_x = inner_w // 2 + btn_spacing // 2
    back_y = play_y

    back_canvas = tk.Canvas(
        content_frame,
        width=btn_w,
        height=btn_h,
        highlightthickness=0,
        bg=app.colors[app.theme]["card"]
    )
    back_canvas.place(x=back_x, y=back_y)

    back_rect = app.draw_rounded_rectangle(
        back_canvas,
        0, 0, btn_w, btn_h,
        radius=btn_radius,
        fill=btn_fill,
        outline=""
    )
    back_text = back_canvas.create_text(
        btn_w // 2, btn_h // 2,
        text=btn_label,
        font=("Montserrat", 14, "bold"),
        fill="white"
    )

    # Hover + click for Retry/Back
    def back_enter(e):
        back_canvas.itemconfig(back_rect, fill=app.colors[app.theme]["card_hover"])
        back_canvas.config(cursor="hand2")
    def back_leave(e):
        back_canvas.itemconfig(back_rect, fill=btn_fill)
        back_canvas.config(cursor="")

    back_canvas.tag_bind(back_rect, "<Enter>", back_enter)
    back_canvas.tag_bind(back_text, "<Enter>", back_enter)
    back_canvas.tag_bind(back_rect, "<Leave>", back_leave)
    back_canvas.tag_bind(back_text, "<Leave>", back_leave)
    back_canvas.tag_bind(back_rect, "<Button-1>", lambda e: btn_command())
    back_canvas.tag_bind(back_text, "<Button-1>", lambda e: btn_command())

    # 11) Finally, redraw the progress bar at the bottom of the root window (unchanged):
    app.master.configure(bg=app.colors[app.theme]["bg"])
    app.update_progress_bar()