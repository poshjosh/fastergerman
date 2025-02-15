# Prompt used to generate the project

List the 200 most frequently used German verbs and the specific prepositions they are typically used with.

For each verb specify the following:
-	Specific preposition that verb is typically used with.
-	An example sentence in German.
-	A translation for the sentence.
-	Four other prepositions to be used as ‘wrong’ choices in a multi-choice question.

Generate the data in the following format:

VERB_DATA = [
{
"verb": "warten",
"preposition": "auf",
"example": "Ich warte ___ den Bus.",
"translation": "I'm waiting for the bus.",
"choices": ["mit", "für", "zu", "auf"]
},
{
"verb": "denken",
"preposition": "an",
"example": "Ich denke ___ meine Familie.",
"translation": "I'm thinking about my family.",
"choices": ["über", "von", "an", "mit"]
},
]

Write code for a python app for learning German verbs that are typically used with specific prepositions.

The app should use the previously generated data containing 200 most common German verbs that are typically used with specific prepositions.

The app should have a start screen (or home page) which displays a start and pause button.

When the start button is clicked, the app should flash one question at a time.

Each question should display a sentence with one German verb and an underlined space for the specific preposition used with that verb.

The aim is for the user to answer each question by selecting a matching preposition for the verb in the displayed question.

Each question should have between 2 and 5 choices with only one correct answer.

Each question should remain onscreen for between 3 and 30 seconds.

Each time a choice/option is selected by the user, the correct answer should be highlighted in green.

The number of successes over the total score should remain on display throughout the game.

For example, if the user has attempted 5 questions but on succeeded in answering 3, then the display should be: 3/5 succeeded.

When the pause button is clicked, the app should pause displaying questions.

On the app’s start screen or home page should be a settings section.

In the settings section, should be options for:

1.	Setting the number of choices displayed for each question, which should be between 2 and 5.
2.	Setting the period of display for each question, which should be between 3 and 30.

At the top left or right, there should be a timer countdown for each question, counting down from the period of display for that question to zero.

Give the app a befitting name.


