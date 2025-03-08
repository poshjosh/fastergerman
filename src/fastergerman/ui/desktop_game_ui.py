import logging
import tkinter as tk
from tkinter import ttk
import random
from typing import List, Callable

from fastergerman.config import AppConfig
from fastergerman.game import Game, GameSession, Question, QuestionsLoader, Settings, \
    AbstractGameTimer, GameEventListener, GameFile
from fastergerman.game.game_session import NO_GAME_NAME_SELECTION, GameTimers
from fastergerman.i18n import DEFAULT_LANGUAGE_CODE, I18n, SETTINGS, GAME_TO_LOAD, \
    QUESTION_DISPLAY_TIME_SECONDS, NUMBER_OF_CHOICES_PER_QUESTION, MAX_CONSECUTIVE_CORRECT_ANSWERS, \
    DISPLAY_QUESTION_TRANSLATION, START_AT_QUESTION_NUMBER, MAX_NUMBER_OF_QUESTIONS, \
    START_GAME_PROMPT, START, PAUSE, SCORE, QUESTIONS_LEFT, TIME, GAME_COMPLETED_MESSAGE
from fastergerman.ui import UIGameTimer, CloseGameDialog

logger = logging.getLogger(__name__)

FONT_X_LARGE = ('Helvetica', 24, 'bold')
FONT_LARGE = ('Helvetica', 20, 'bold')
FONT_MEDIUM = ('Helvetica', 16, 'bold')
PADDING_L = 16
PADDING_M = 8
PADDING_S = 4
LABEL_STYLE = "Medium.TLabel"
CORRECT_BUTTON_STYLE = "Correct.TButton"

class DesktopGameSession(GameSession):
    def __init__(self,
                 game_file: GameFile,
                 game_counters: GameTimers,
                 questions: List[Question],
                 handle_question: Callable[[Question], None]):
        super().__init__(game_file, questions)
        self.__game_counters = game_counters
        self.__handle_question = handle_question

    def get_countdown_timer(self) -> AbstractGameTimer:
        return self.__game_counters.get_countdown_timer()

    def get_next_ques_timer(self) -> AbstractGameTimer:
        return self.__game_counters.get_next_ques_timer()
    
    def handle_question(self, question: Question):
        self.__handle_question(question)
        
    
class DesktopGameUI(GameEventListener, GameTimers):
    def __init__(self, root, app_config: AppConfig):
        super().__init__()
        self.session = DesktopGameSession(
            GameFile(app_config.get_app_dir()),
            self,
            QuestionsLoader().load_questions(app_config.get_preposition_trainer_question_src()),
            self.handle_question)
        self.session.add_game_event_listener(self)
        app_name = app_config.get_app_name()
        self.root = root
        self.root.title(app_name)
        # self.root.geometry("800x600")
        # self.root.geometry("1000x750")

        # Application state
        self.choice_buttons = []

        ##############
        #  Setup UI  #
        ##############

        game: Game = self.session.get_game()
        self.lang_code = app_config.get_app_language(DEFAULT_LANGUAGE_CODE)

        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding=str(PADDING_L))
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure styles
        self.style = ttk.Style()
        self.theme = "clam"    # "default", "alt" .....
        self.style.theme_use(self.theme)
        self.style.configure(CORRECT_BUTTON_STYLE, background="green", foreground="white")
        self.style.configure(LABEL_STYLE, font=FONT_MEDIUM)

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
            text=I18n.translate(self.lang_code, SETTINGS),
            padding=str(PADDING_M)
        )
        settings_frame.grid(row=1, column=0, columnspan=3, pady=PADDING_L, sticky=(tk.W, tk.E))

        # Game to load settings
        ttk.Label(settings_frame, text=I18n.translate(self.lang_code, GAME_TO_LOAD)).grid(
            row=0, column=0, padx=PADDING_S, pady=PADDING_S
        )
        last_saved_game = self.session.get_game_to_load()
        game_names = self.session.get_game_names_or_default()
        self.game_to_load_combo = ttk.Combobox(
            settings_frame,
            state="readonly",
            values=game_names)
        self.game_to_load_combo.grid(row=0, column=1, padx=PADDING_S, pady=PADDING_S)
        if last_saved_game and last_saved_game in self.game_to_load_combo['values']:
            self.game_to_load_combo.set(last_saved_game)

        def on_game_selected(_):
            self.session.handle_game_selection(self.game_to_load_combo.get())
        self.game_to_load_combo.bind("<<ComboboxSelected>>", on_game_selected)

        def update_settings(name: str, value: any):
            self.session.update_settings_value(name, value)

        # Question display time setting
        self.question_display_time_var = tk.StringVar(
            value=str(game.settings.question_display_time))
        self._add_label_and_spinbox(
            settings_frame, 2, I18n.translate(self.lang_code, QUESTION_DISPLAY_TIME_SECONDS),
            5, 60, self.question_display_time_var,
            lambda var: update_settings("question_display_time", int(var.get())))

        # Number of choices setting
        self.number_of_choices_var = tk.StringVar(value=str(game.settings.number_of_choices))
        self._add_label_and_spinbox(
            settings_frame, 3, I18n.translate(self.lang_code, NUMBER_OF_CHOICES_PER_QUESTION),
            2, 5, self.number_of_choices_var,
            lambda var: update_settings("number_of_choices", int(var.get())))

        # Max consecutively correct setting
        self.max_consecutively_correct_var = tk.StringVar(
            value=str(game.settings.max_consecutively_correct))
        self._add_label_and_spinbox(
            settings_frame, 4, I18n.translate(self.lang_code, MAX_CONSECUTIVE_CORRECT_ANSWERS),
            1, 5, self.max_consecutively_correct_var,
            lambda var: update_settings("max_consecutively_correct", int(var.get())))

        # Display translation settings
        ttk.Label(settings_frame, text=I18n.translate(self.lang_code, DISPLAY_QUESTION_TRANSLATION)).grid(
            row=5, column=0, padx=PADDING_S, pady=PADDING_S
        )
        self.display_translation_var = tk.BooleanVar(value=game.settings.display_translation)
        display_translation_check = ttk.Checkbutton(
            settings_frame,
            variable=self.display_translation_var,
            command=lambda: update_settings("display_translation", self.display_translation_var.get()))
        display_translation_check.grid(row=5, column=1, padx=PADDING_S, pady=PADDING_S)

        # Start at question number:
        self.start_at_question_number_var = tk.StringVar(
            value=str(game.settings.start_at_question_number))
        self._add_label_and_spinbox(
            settings_frame, 6, I18n.translate(self.lang_code, START_AT_QUESTION_NUMBER),
            1, self.session.get_max_questions() - 1, self.start_at_question_number_var,
            lambda var: update_settings("start_at_question_number", int(var.get())))

        # Max number of questions
        self.max_number_of_questions_var = tk.StringVar(
            value=str(game.settings.max_number_of_questions))
        self._add_label_and_spinbox(
            settings_frame, 7, I18n.translate(self.lang_code, MAX_NUMBER_OF_QUESTIONS),
            2, self.session.get_max_questions(), self.max_number_of_questions_var,
            lambda var: update_settings("max_number_of_questions", int(var.get())))

        # Question display area
        self.question_frame = ttk.Frame(self.main_frame, padding=str(PADDING_L))
        self.question_frame.grid(row=2, column=0, columnspan=3, pady=PADDING_L)

        self.question_label = ttk.Label(
            self.question_frame,
            text=I18n.translate(self.lang_code, START_GAME_PROMPT),
            font=FONT_LARGE
        )
        self.question_label.grid(row=0, column=0, pady=PADDING_M)

        # Choices frame
        self.choices_frame = ttk.Frame(self.question_frame)
        self.choices_frame.grid(row=1, column=0, pady=PADDING_M)

        # Start,Stop buttons
        self.start_button = ttk.Button(
            self.main_frame,
            text=I18n.translate(self.lang_code, START),
            command=self.session.start_game
        )
        self.start_button.grid(row=3, column=0, pady=PADDING_L, padx=PADDING_S)

        self.pause_button = ttk.Button(
            self.main_frame,
            text=I18n.translate(self.lang_code, PAUSE),
            command=self.session.pause_game,
            state=tk.DISABLED
        )
        self.pause_button.grid(row=3, column=1, pady=PADDING_L, padx=PADDING_S)

        # Score display
        self.score_var = tk.StringVar(value=f"{I18n.translate(self.lang_code, SCORE)}: {game.score}")
        score_label = ttk.Label(
            self.main_frame,
            textvariable=self.score_var,
            font=FONT_LARGE
        )
        score_label.grid(row=4, column=0, columnspan=3, pady=PADDING_M)

        # Questions left display
        self.questions_left_label = ttk.Label(
            self.main_frame,
            text=f"{I18n.translate(self.lang_code, QUESTIONS_LEFT)}: ",
            style=LABEL_STYLE
        )
        self.questions_left_label.grid(row=5, column=0, sticky=tk.W, padx=PADDING_M)

        # Timer display
        self.timer_label = ttk.Label(
            self.main_frame,
            text=f"{I18n.translate(self.lang_code, TIME)}: --",
            style=LABEL_STYLE
        )
        self.timer_label.grid(row=5, column=2, sticky=tk.E, padx=PADDING_M)

        if self.session.get_game_to_load():
            self.session.load_game(self.session.get_game_to_load(), game.settings)

        self.countdown_timer = self._create_countdown_timer()
        # TODO - This timer should change, anytime game settings.question_display_time changes.
        self.next_ques_timer = self._create_next_ques_timer()

    def close_window(self):
        logger.debug("Closing window")
        def on_ok(text: str):
            if not text:
                raise ValueError("Required: game name")
            self.session.save_game_as(text)
            self.root.destroy()
        value = None if self.game_to_load_combo.get() == NO_GAME_NAME_SELECTION \
            else self.game_to_load_combo.get()
        CloseGameDialog(self.lang_code).ask(value, on_ok)

    def on_game_loaded(self, game: Game):
        logger.debug("Game loaded: %s", game.name)
        self._update_display()
        self._update_settings(game.settings)

    def on_game_started(self, game: Game):
        logger.debug("Game started: %s", game.name)
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

    def on_game_resumed(self, game: Game):
        logger.debug("Game resumed: %s", game.name)
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

    def on_game_paused(self, game: Game):
        logger.debug("Game paused: %s", game.name)
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        # TODO - Disable question choice buttons

    def on_question(self, game: Game, question: Question):
        logger.debug("on_question, Game: %1s, question: %2s", game.name, question)

    def on_question_answered(self, game: Game, question: Question, answer: str):
        logger.debug("on_question_answered, Game: %1s, question: %2s, answer: %3s", game.name, question, answer)
        self._update_display()

        # Highlight correct answer
        for btn in self.choice_buttons:
            if question.is_answer(btn['text']):
                btn.configure(style=CORRECT_BUTTON_STYLE)

    def on_game_completed(self, game: Game):
        logger.debug("Game completed: %s", game.name)
        self.question_label.config(
            text=I18n.translate(self.lang_code, GAME_COMPLETED_MESSAGE).format(game.score.to_percent()))
        self._remove_game(game.name)

    def handle_question(self, question: Question):
        logger.debug("Handling question: %s", question)
        # Clear previous choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
        self.choice_buttons.clear()

        # Display question
        if self.display_translation_var.get() is True:
            question_example = (f"{question.example}\n\n"
                                f"({question.translation})")
        else:
            question_example = question.example

        self.question_label.config(text=question_example)

        # Get choices
        choices = self._get_choices(
            question.preposition, question.choices, int(self.number_of_choices_var.get()))

        def handle_answer(answer: str):
            self.session.handle_answer(answer)
            # Show next question after a brief delay so the user can see if they are right or wrong.
            self.root.after(2000, lambda: self.session.next_question())

        # Create choice buttons
        for i, choice in enumerate(choices):
            btn = ttk.Button(
                self.choices_frame,
                text=choice,
                command=lambda c=choice: handle_answer(c)
            )
            btn.grid(row=0, column=i, padx=PADDING_S)
            self.choice_buttons.append(btn)

    def get_countdown_timer(self) -> AbstractGameTimer:
        return self.countdown_timer

    def get_next_ques_timer(self) -> AbstractGameTimer:
        return self.next_ques_timer

    @staticmethod
    def _add_label_and_spinbox(parent, row: int, label_text: str, frm: int, to: int,
                               text_variable, command: Callable[[tk.StringVar], None]):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=PADDING_S, pady=PADDING_S)
        spinbox = ttk.Spinbox(
            parent,
            from_=frm,
            to=to,
            textvariable=text_variable,
            width=5,
            command=lambda: command(text_variable)
        )
        spinbox.grid(row=row, column=1, padx=PADDING_S, pady=PADDING_S)

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

    def _create_countdown_timer(self) -> AbstractGameTimer:
        timer = UIGameTimer(self.root, 1000)
        def update_countdown(time_remaining: int):
            self.timer_label.config(text=f"{I18n.translate(self.lang_code, TIME)}: {int(time_remaining/1000)}")
        timer.add_tick_listener(update_countdown)
        return timer

    def _create_next_ques_timer(self) -> AbstractGameTimer:
        timer = UIGameTimer(self.root, int(self.question_display_time_var.get()) * 1000)
        timer.add_tick_listener(lambda _: self.session.next_question(False))
        return timer

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
        self.questions_left_label.config(text=f"{I18n.translate(self.lang_code, QUESTIONS_LEFT)}: {len(self.session.get_game().questions)}")

    def _update_score(self):
        self.score_var.set(f"{I18n.translate(self.lang_code, SCORE)}: {self.session.get_game().score}")

    def _remove_game(self, game_name: str):
        game_to_load_values = list(self.game_to_load_combo['values'])
        if game_name in game_to_load_values:
            game_to_load_values.remove(game_name)
            self.game_to_load_combo['values'] = game_to_load_values
