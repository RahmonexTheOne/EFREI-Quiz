# EFREI-Quiz

EFREI-Quiz is a Python-based quiz application that uses **Tkinter** for the user interface and **pandas** to load question data from a CSV file. It presents multiple-choice questions in a modern, full-screen GUI, tracks user choices, and displays correct/incorrect answers. A progress bar at the bottom shows each question’s correctness status.

## Features

- **Full-screen** windowed mode with an Exit button  
- **Progress bar** at the bottom that updates as you answer  
- **Timer** for each question, auto-submitting when time runs out  
- **Partial correctness** approach or all-or-nothing for multiple-correct answers  
- **Rounded, modern UI** with accent colors  
- **CSV-based** question data loading (via `pandas`)

## Project Structure

```
EFREI-Quiz/
│
├── data/
│   └── ldap.csv        # CSV file with your quiz questions
├── main.py             # Your main EFREI-Quiz application code
├── requirements.txt    # Dependencies (pandas)
└── README.md           # This file
```

## Prerequisites

- **Python 3.7+** (recommended)
- **pip** (typically included with Python)
- **CSV file** (e.g., `ldap.csv`) placed in a `data/` folder

## Installation on Windows

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/RahmonexTheOne/EFREI-Quiz.git
   ```
   or download and unzip.

2. **Navigate** to the project folder:
   ```bash
   cd EFREI-Quiz
   ```

3. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   ```
   This creates a folder called `venv/` that holds an isolated Python environment.

4. **Activate** your virtual environment:
   ```bash
   venv\Scripts\activate
   ```
   Your terminal prompt should show `(venv)` afterwards.

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   This installs **pandas** (and anything else in `requirements.txt`).

## Usage

1. **Activate** your virtual environment (if not already):
   ```bash
   venv\Scripts\activate
   ```
2. **Run** the quiz:
   ```bash
   python main.py
   ```
   The quiz opens in full-screen mode.

3. **Exit** either by clicking the **Exit** button at the top-right, or pressing `Ctrl + C` in the terminal.

## CSV Format

In `data/ldap.csv`, each row might look like:

```
Type,Title,Choice,Choice.2,Choice.3,Choice.4,Correct
MCQ,Which port is default for LDAP?,389,443,53,25,1
...
```

Where:
- **Title** = question text  
- **Choice, Choice.2, ...** = answer options  
- **Correct** = 1-based index(es) of the correct answer(s) (e.g., `1` means the first choice, `2` means the second, etc.)

## License

*(Add your license details here if you wish.)*

## Contributing

1. Fork this repository  
2. Create a new branch  
3. Make your changes, commit, and push  
4. Submit a pull request

## Contact

- **Author**: Bilel RAHMOUNI
