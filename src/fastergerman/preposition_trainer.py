import tkinter as tk
from tkinter import ttk
import random
from typing import List

from .game import Score
from .game_file import get_game_names, get_game_to_load, load_game, save_game, Game
from .german_verbs_data import VERB_DATA

FONT_X_LARGE = ('Helvetica', 24, 'bold')
FONT_LARGE = ('Helvetica', 20, 'bold')
FONT_MEDIUM = ('Helvetica', 16, 'bold')

DISPLAY_TIME_SECONDS = 30
NUM_CHOICES = 3
MAX_CONSECUTIVELY_CORRECT = 2

QUESTIONS_LEFT = "Questions left"
STYLE_MEDIUM_TEXT = "Timer.TLabel"
CONSECUTIVELY_CORRECT = 'consecutively_correct'
DEFAULT_GAME_NAME = "Game 1"


class PrepositionTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("PrepMeister Pro - German Preposition Trainer")
        # self.root.geometry("800x600")
        self.root.geometry("1000x750")

        # Application state
        self.is_running = False
        self.current_question = None
        self.display_time = DISPLAY_TIME_SECONDS
        self.num_choices = NUM_CHOICES
        self.after_id = None
        self.timer_id = None
        self.time_remaining = 0
        self.choice_buttons = []
        self.game = Game(DEFAULT_GAME_NAME, [], Score(0, 0))

        self._setup_ui()

    def _setup_ui(self):
        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure styles
        style = ttk.Style()
        style.theme_use("clam")    # "default", "alt" .....
        style.configure("Correct.TButton", background="green", foreground="white")
        style.configure(STYLE_MEDIUM_TEXT, font=FONT_MEDIUM)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="PrepMeister Pro", 
            font=FONT_X_LARGE
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=20)

        # Settings Frame
        settings_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Settings", 
            padding="10"
        )
        settings_frame.grid(row=1, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))

        # Game to load settings
        ttk.Label(settings_frame, text="Game to load:").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.game_to_load_var = tk.StringVar(value=get_game_to_load())
        game_to_load_combo = ttk.Combobox(
            settings_frame,
            state="readonly",
            values=get_game_names())
        game_to_load_combo.grid(row=0, column=1, padx=5, pady=5)

        def combo_selected(_):
            game_name = game_to_load_combo.get()
            self.save_game_as_var.set(game_name)
            self.game_to_load_var.set(game_name)

        game_to_load_combo.bind("<<ComboboxSelected>>", combo_selected)

        # Game name settings.
        ttk.Label(settings_frame, text="Save game as:").grid(
            row=1, column=0, padx=5, pady=5
        )
        game_to_load = self.game_to_load_var.get()
        self.save_game_as_var = tk.StringVar(
            value=DEFAULT_GAME_NAME if not game_to_load else game_to_load)
        save_game_as_text = ttk.Entry(
            settings_frame,
            textvariable=self.save_game_as_var)
        save_game_as_text.grid(row=1, column=1, padx=5, pady=5)

        # Display time setting
        ttk.Label(settings_frame, text="Question display time (seconds):").grid(
            row=2, column=0, padx=5, pady=5
        )
        self.question_display_time_var = tk.StringVar(value=str(DISPLAY_TIME_SECONDS))
        question_display_time_spinbox = ttk.Spinbox(
            settings_frame, 
            from_=5,
            to=60,
            textvariable=self.question_display_time_var,
            width=5
        )
        question_display_time_spinbox.grid(row=2, column=1, padx=5, pady=5)
        
        # Number of choices setting
        ttk.Label(settings_frame, text="Number of choices:").grid(
            row=3, column=0, padx=5, pady=5
        )
        self.number_of_choices_var = tk.StringVar(value=str(NUM_CHOICES))
        number_of_choices_spinbox = ttk.Spinbox(
            settings_frame, 
            from_=2, 
            to=5, 
            textvariable=self.number_of_choices_var,
            width=5
        )
        number_of_choices_spinbox.grid(row=3, column=1, padx=5, pady=5)

        # Max consecutively correct setting
        ttk.Label(settings_frame, text="Max consecutively correct:").grid(
            row=4, column=0, padx=5, pady=5
        )
        self.max_consecutively_correct_var = tk.StringVar(value=str(MAX_CONSECUTIVELY_CORRECT))
        max_consecutively_correct_spinbox = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=5,
            textvariable=self.max_consecutively_correct_var,
            width=5
        )
        max_consecutively_correct_spinbox.grid(row=4, column=1, padx=5, pady=5)

        # Display translation settings
        ttk.Label(settings_frame, text="Display translation:").grid(
            row=5, column=0, padx=5, pady=5
        )
        self.display_translation_var = tk.BooleanVar(value=True)
        display_translation_check = ttk.Checkbutton(
            settings_frame,
            variable=self.display_translation_var)
        display_translation_check.grid(row=5, column=1, padx=5, pady=5)

        # Question display area
        self.question_frame = ttk.Frame(self.main_frame, padding="20")
        self.question_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.question_label = ttk.Label(
            self.question_frame, 
            text="Click Start to begin",
            font=FONT_LARGE
        )
        self.question_label.grid(row=0, column=0, pady=10)
        
        # Choices frame
        self.choices_frame = ttk.Frame(self.question_frame)
        self.choices_frame.grid(row=1, column=0, pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(
            self.main_frame, 
            text="Start", 
            command=self.start_quiz
        )
        self.start_button.grid(row=3, column=0, pady=20, padx=5)
        
        self.pause_button = ttk.Button(
            self.main_frame, 
            text="Pause", 
            command=self.pause_quiz, 
            state=tk.DISABLED
        )
        self.pause_button.grid(row=3, column=1, pady=20, padx=5)

        # Score display
        self.score_var = tk.StringVar(value=f"Score: {self.game.score}")
        score_label = ttk.Label(
            self.main_frame, 
            textvariable=self.score_var, 
            font=FONT_LARGE
        )
        score_label.grid(row=4, column=0, columnspan=3, pady=10)

        # Questions left display
        self.questions_left_label = ttk.Label(
            self.main_frame,
            text=f"{QUESTIONS_LEFT}: ",
            style=STYLE_MEDIUM_TEXT
        )
        self.questions_left_label.grid(row=5, column=0, sticky=tk.W, padx=10)

        # Timer display
        self.timer_label = ttk.Label(
            self.main_frame,
            text="Time: --",
            style=STYLE_MEDIUM_TEXT
        )
        self.timer_label.grid(row=5, column=2, sticky=tk.E, padx=10)

    def start_quiz(self):
        self.is_running = True
        if self.game_to_load_var.get():
            self.game = load_game(self.game_to_load_var.get())
        if not self.game.questions:
            questions = [e for e in VERB_DATA if 'priority' not in e or e['priority'] != 'low']
            self.game = self.game.with_questions(questions)
        self._update_score()
        self._update_questions_left()
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.display_time = int(self.question_display_time_var.get())
        self.num_choices = int(self.number_of_choices_var.get())
        self.show_next_question()
        
    def pause_quiz(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

    def update_timer(self):
        if not self.is_running:
            return
            
        self.time_remaining -= 1
        self.timer_label.config(text=f"Time: {self.time_remaining}")
        
        if self.time_remaining > 0:
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.show_next_question()
            
    def show_next_question(self):
        if not self.is_running:
            return

        # Save game
        self.game = self.game.with_name(self.save_game_as_var.get())
        save_game(self.game)

        # Clear previous choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
        self.choice_buttons.clear()
            
        # Select random question
        next_question = random.choice(self.game.questions)
        if next_question == self.current_question:
            # If the same question is selected, try once more
            next_question = random.choice(self.game.questions)
        self.current_question = next_question
        
        # Display question
        if self.display_translation_var.get() is True:
            question = (f"{self.current_question['example']}\n\n"
                        f"({self.current_question['translation']})")
        else:
            question = self.current_question['example']

        self.question_label.config(text=question)
        
        # Get choices
        choices = self.get_choices(
            self.current_question['preposition'],
            self.current_question['alternatives'],
            self.num_choices
        )
        
        # Create choice buttons
        for i, choice in enumerate(choices):
            btn = ttk.Button(
                self.choices_frame,
                text=choice,
                command=lambda c=choice: self.check_answer(c)
            )
            btn.grid(row=0, column=i, padx=5)
            self.choice_buttons.append(btn)
            
        # Reset and start timer
        self.time_remaining = self.display_time
        self.timer_label.config(text=f"Time: {self.time_remaining}")
        self.update_timer()
            
        # Schedule next question
        self.after_id = self.root.after(
            self.display_time * 1000, 
            self.show_next_question
        )

    @staticmethod
    def get_choices(correct: str, alternatives: List[str], num_choices: int) -> List[str]:
        """Get a list of choices including the correct answer and random alternatives."""
        choices = [correct]
        available_alternatives = [alt for alt in alternatives if alt != correct]
        choices.extend(random.sample(
            available_alternatives, 
            min(num_choices - 1, len(available_alternatives))
        ))
        random.shuffle(choices)
        return choices
        
    def check_answer(self, answer: str):
        correct_preposition = self.current_question['preposition']

        # Update score
        self.game = self.game.advance_score(answer == correct_preposition)
        self._update_score()

        if answer == correct_preposition:
            self.on_answer_correct()
        else:
            self.on_answer_false()

        # Highlight correct answer
        for btn in self.choice_buttons:
            if btn['text'] == correct_preposition:
                btn.configure(style="Correct.TButton")
            # Disabling this button prevented the style above from being applied.
            # btn.configure(state=tk.DISABLED)

        # Cancel current timers
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        # Show next question after a brief delay
        self.root.after(1000, self.show_next_question)

    def on_answer_correct(self):
        if CONSECUTIVELY_CORRECT not in self.current_question:
            self.current_question[CONSECUTIVELY_CORRECT] = 1
        else:
            self.current_question[CONSECUTIVELY_CORRECT] += 1
        value: int = int(self.max_consecutively_correct_var.get())
        if self.current_question[CONSECUTIVELY_CORRECT] >= value:
            self.game.questions.remove(self.current_question)
            self._update_questions_left()

    def on_answer_false(self):
        if CONSECUTIVELY_CORRECT in self.current_question:
            self.current_question[CONSECUTIVELY_CORRECT] = 0

    def _update_questions_left(self):
        if self.game.questions:
            self.questions_left_label.config(text=f"{QUESTIONS_LEFT}: {len(self.game.questions)}")

    def _update_score(self):
        self.score_var.set(f"Score: {self.game.score}")
