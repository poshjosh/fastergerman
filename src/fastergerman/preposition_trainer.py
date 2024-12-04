import tkinter as tk
from datetime import datetime
from tkinter import ttk
import random
from typing import List

from .default_questions import DEFAULT_QUESTIONS
from .game import Score, Settings, Question
from .game_file import delete_game, get_game_names, get_game_to_load, load_game, save_game, Game

INITIAL_GAME_NAME = "Game 1"
FONT_X_LARGE = ('Helvetica', 24, 'bold')
FONT_LARGE = ('Helvetica', 20, 'bold')
FONT_MEDIUM = ('Helvetica', 16, 'bold')
NO_GAME_NAME_SELECTION = "None"
PADDING_L = 16
PADDING_M = 8
PADDING_S = 4
QUESTIONS_LEFT = "Questions left"
STYLE_MEDIUM_TEXT = "Timer.TLabel"


class PrepositionTrainer:
    def __init__(self, root, app_name: str):
        self.root = root
        self.root.title(app_name)
        # self.root.geometry("800x600")
        self.root.geometry("1000x750")

        # Application state
        self.is_running = False
        self.current_question: Question | None = None
        self.after_id = None
        self.timer_id = None
        self.time_remaining = 0
        self.choice_buttons = []
        self.game = PrepositionTrainer._get_default_game()

        ##############
        #  Setup UI  #
        ##############

        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding=str(PADDING_L))
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure styles
        style = ttk.Style()
        style.theme_use("clam")    # "default", "alt" .....
        style.configure("Correct.TButton", background="green", foreground="white")
        style.configure(STYLE_MEDIUM_TEXT, font=FONT_MEDIUM)

        # Title
        title_label = ttk.Label(
            self.main_frame,
            text=app_name,
            font=FONT_X_LARGE
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=PADDING_L)

        # Settings Frame
        settings_frame = ttk.LabelFrame(
            self.main_frame,
            text="Settings",
            padding=str(PADDING_M)
        )
        settings_frame.grid(row=1, column=0, columnspan=3, pady=PADDING_L, sticky=(tk.W, tk.E))

        # Game to load settings
        ttk.Label(settings_frame, text="Game to load:").grid(
            row=0, column=0, padx=PADDING_S, pady=PADDING_S
        )
        game_to_load = get_game_to_load()
        self.game_to_load_var = tk.StringVar(value=game_to_load)
        game_names = get_game_names()
        game_names.insert(0, NO_GAME_NAME_SELECTION)
        self.game_to_load_combo = ttk.Combobox(
            settings_frame,
            state="readonly",
            values=game_names)
        self.game_to_load_combo.grid(row=0, column=1, padx=PADDING_S, pady=PADDING_S)
        if game_to_load and game_to_load in self.game_to_load_combo['values']:
            self.game_to_load_combo.set(game_to_load)

        self.game_to_load_combo.bind("<<ComboboxSelected>>", self.on_combo_selected)

        # Game name settings.
        ttk.Label(settings_frame, text="Save game as:").grid(
            row=1, column=0, padx=PADDING_S, pady=PADDING_S
        )
        game_to_load = self.game_to_load_var.get()
        self.save_game_as_var = tk.StringVar(
            value=INITIAL_GAME_NAME if not game_to_load else game_to_load)
        save_game_as_text = ttk.Entry(
            settings_frame,
            textvariable=self.save_game_as_var)
        save_game_as_text.grid(row=1, column=1, padx=PADDING_S, pady=PADDING_S)

        # Question display time setting
        self.question_display_time_var = tk.StringVar(
            value=str(self.game.settings.question_display_time))
        self._add_label_and_spinbox(settings_frame, 2, "Question display time (seconds):",
                                    5, 60, self.question_display_time_var)

        # Number of choices setting
        self.number_of_choices_var = tk.StringVar(value=str(self.game.settings.number_of_choices))
        self._add_label_and_spinbox(settings_frame, 3, "Number of choices:",
                                    2, 5, self.number_of_choices_var)

        # Max consecutively correct setting
        self.max_consecutively_correct_var = tk.StringVar(
            value=str(self.game.settings.max_consecutively_correct))
        self._add_label_and_spinbox(settings_frame, 4, "Max consecutively correct:",
                                    1, 5, self.max_consecutively_correct_var)

        # Display translation settings
        ttk.Label(settings_frame, text="Display translation:").grid(
            row=5, column=0, padx=PADDING_S, pady=PADDING_S
        )
        self.display_translation_var = tk.BooleanVar(value=self.game.settings.display_translation)
        display_translation_check = ttk.Checkbutton(
            settings_frame,
            variable=self.display_translation_var)
        display_translation_check.grid(row=5, column=1, padx=PADDING_S, pady=PADDING_S)

        # Start at question number:
        self.start_at_question_number_var = tk.StringVar(
            value=str(self.game.settings.start_at_question_number))
        self._add_label_and_spinbox(settings_frame, 6, "Start at question number:",
                                    1, len(DEFAULT_QUESTIONS) - 1,
                                    self.start_at_question_number_var)

        # Max number of questions
        self.max_number_of_questions_var = tk.StringVar(
            value=str(self.game.settings.max_number_of_questions))
        self._add_label_and_spinbox(settings_frame, 7, "Max number of questions:",
                                    2, len(DEFAULT_QUESTIONS), self.max_number_of_questions_var)

        # Question display area
        self.question_frame = ttk.Frame(self.main_frame, padding=str(PADDING_L))
        self.question_frame.grid(row=2, column=0, columnspan=3, pady=PADDING_L)

        self.question_label = ttk.Label(
            self.question_frame,
            text="Click Start to begin",
            font=FONT_LARGE
        )
        self.question_label.grid(row=0, column=0, pady=PADDING_M)

        # Choices frame
        self.choices_frame = ttk.Frame(self.question_frame)
        self.choices_frame.grid(row=1, column=0, pady=PADDING_M)

        # Control buttons
        self.start_button = ttk.Button(
            self.main_frame,
            text="Start",
            command=self.start_quiz
        )
        self.start_button.grid(row=3, column=0, pady=PADDING_L, padx=PADDING_S)

        self.pause_button = ttk.Button(
            self.main_frame,
            text="Pause",
            command=self.pause_quiz,
            state=tk.DISABLED
        )
        self.pause_button.grid(row=3, column=1, pady=PADDING_L, padx=PADDING_S)

        # Score display
        self.score_var = tk.StringVar(value=f"Score: {self.game.score}")
        score_label = ttk.Label(
            self.main_frame,
            textvariable=self.score_var,
            font=FONT_LARGE
        )
        score_label.grid(row=4, column=0, columnspan=3, pady=PADDING_M)

        # Questions left display
        self.questions_left_label = ttk.Label(
            self.main_frame,
            text=f"{QUESTIONS_LEFT}: ",
            style=STYLE_MEDIUM_TEXT
        )
        self.questions_left_label.grid(row=5, column=0, sticky=tk.W, padx=PADDING_M)

        # Timer display
        self.timer_label = ttk.Label(
            self.main_frame,
            text="Time: --",
            style=STYLE_MEDIUM_TEXT
        )
        self.timer_label.grid(row=5, column=2, sticky=tk.E, padx=PADDING_M)

        if game_to_load:
            self._load_game(game_to_load, self.game.settings)

    def on_combo_selected(self, _):
        game_name = self.game_to_load_combo.get()
        self.game_to_load_var.set(game_name)
        self._load_game(game_name, self.game.settings)

    def start_quiz(self):
        self.is_running = True
        self._load_game(self.game_to_load_var.get(), self._get_settings())
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.show_next_question()
        
    def pause_quiz(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self._save_game()

    def show_next_question(self):
        if not self.is_running:
            return

        # Clear previous choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
        self.choice_buttons.clear()

        if len(self.game.questions) == 0:
            self.pause_quiz()
            self.question_label.config(
                text=f"Game Completed. You scored {self.game.score.to_percent()} percent.")

            # Delete game
            delete_game(self.game.name)
            game_to_load_values = list(self.game_to_load_combo['values'])
            if self.game.name in game_to_load_values:
                game_to_load_values.remove(self.game.name)
                self.game_to_load_combo['values'] = game_to_load_values

            # Load default game, but start at next set of questions
            self._load_game(NO_GAME_NAME_SELECTION, self.game.settings.next())
            return

        self._save_game()

        # Select random question
        next_question: Question = random.choice(self.game.questions)
        if next_question == self.current_question:
            # If the same question is selected, try once more
            next_question: Question = random.choice(self.game.questions)
        self.current_question = next_question
        
        # Display question
        if self.display_translation_var.get() is True:
            question = (f"{self.current_question.example}\n\n"
                        f"({self.current_question.translation})")
        else:
            question = self.current_question.example

        self.question_label.config(text=question)
        
        # Get choices
        choices = PrepositionTrainer._get_choices(
            self.current_question.preposition,
            self.current_question.choices,
            int(self.number_of_choices_var.get())
        )
        
        # Create choice buttons
        for i, choice in enumerate(choices):
            btn = ttk.Button(
                self.choices_frame,
                text=choice,
                command=lambda c=choice: self._on_answer(c)
            )
            btn.grid(row=0, column=i, padx=PADDING_S)
            self.choice_buttons.append(btn)
            
        # Reset and start timer
        display_time: int = int(self.question_display_time_var.get())
        self.time_remaining = display_time
        self.timer_label.config(text=f"Time: {self.time_remaining}")
        self._update_timer()
            
        # Schedule next question
        self.after_id = self.root.after(
            display_time * 1000,
            self.show_next_question
        )

    @staticmethod
    def _add_label_and_spinbox(parent, row: int, label_text: str, frm: int, to: int, text_variable):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=PADDING_S, pady=PADDING_S)
        spinbox = ttk.Spinbox(
            parent,
            from_=frm,
            to=to,
            textvariable=text_variable,
            width=5
        )
        spinbox.grid(row=row, column=1, padx=PADDING_S, pady=PADDING_S)

    @staticmethod
    def _get_default_game(game_name: str = INITIAL_GAME_NAME,
                          settings: Settings = Settings.of_dict({})) -> Game:
        offset = settings.start_at_question_number
        limit = settings.max_number_of_questions
        return Game(game_name, settings,
                    PrepositionTrainer._get_default_questions(offset, limit), Score(0, 0))

    @staticmethod
    def _get_default_questions(
            first_question: int = 0, max_questions: int = len(DEFAULT_QUESTIONS)) -> List[Question]:
        questions = [Question.of_dict(e) for e in DEFAULT_QUESTIONS]
        questions = [q for q in questions if q.priority != "low"]
        last_question = first_question + max_questions
        if last_question > len(questions):
            last_question = len(questions)
        return questions[first_question:last_question]

    @staticmethod
    def _get_choices(correct: str, options: List[str], num_choices: int) -> List[str]:
        """Get a list of choices including the correct answer and random alternatives."""
        choices = [correct]
        available_alternatives = [alt for alt in options if alt != correct]
        choices.extend(random.sample(
            available_alternatives,
            min(num_choices - 1, len(available_alternatives))
        ))
        random.shuffle(choices)
        return choices

    def _load_game(self, game_name: str or None, settings: Settings):
        """
        Load a game with the specified settings.
        If the game was loaded from file, the provided settings will be ignored.
        """
        if game_name:
            if game_name == NO_GAME_NAME_SELECTION:  # reset
                self.game = PrepositionTrainer._get_default_game(
                    f"Game_{datetime.today().strftime('%Y-%m-%d_%H%M%S')}",
                    settings)
            else:
                self.game = load_game(game_name)
            self.save_game_as_var.set(self.game.name)
            self._update_settings(self.game.settings)
        else:
            self.game = PrepositionTrainer._get_default_game(settings=settings)
            if self.save_game_as_var.get() == INITIAL_GAME_NAME or not self.save_game_as_var.get():
                self.save_game_as_var.set(self.game.name)
        self._update_display()

    def _save_game(self):
        self.game = (self.game
                     .with_name(self.save_game_as_var.get())
                     .with_settings(self._get_settings()))
        save_game(self.game)

    def _update_timer(self):
        if not self.is_running:
            return

        self.time_remaining -= 1
        self.timer_label.config(text=f"Time: {self.time_remaining}")

        if self.time_remaining > 0:
            self.timer_id = self.root.after(1000, self._update_timer)
        else:
            self.show_next_question()

    def _on_answer(self, answer: str):
        # Update score
        self.game = self.game.on_question_answer(self.current_question, answer)
        self._update_display()

        # Highlight correct answer
        for btn in self.choice_buttons:
            if self.current_question.is_answer(btn['text']):
                btn.configure(style="Correct.TButton")

        # Cancel current timers
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        # Show next question after a brief delay
        self.root.after(1000, self.show_next_question)

    def _get_settings(self) -> Settings:
        return Settings(
            int(self.question_display_time_var.get()),
            int(self.number_of_choices_var.get()),
            int(self.max_consecutively_correct_var.get()),
            self.display_translation_var.get(),
            int(self.start_at_question_number_var.get()),
            int(self.max_number_of_questions_var.get()))

    def _update_settings(self, settings: Settings):
        self.question_display_time_var.set(str(settings.question_display_time))
        self.number_of_choices_var.set(str(settings.number_of_choices))
        self.max_consecutively_correct_var.set(str(settings.max_consecutively_correct))
        self.display_translation_var.set(settings.display_translation)
        self.start_at_question_number_var.set(str(settings.start_at_question_number))
        self.max_number_of_questions_var.set(str(settings.max_number_of_questions))

    def _update_display(self):
        self._update_score()
        self._update_questions_left()

    def _update_questions_left(self):
        self.questions_left_label.config(text=f"{QUESTIONS_LEFT}: {len(self.game.questions)}")

    def _update_score(self):
        self.score_var.set(f"Score: {self.game.score}")
