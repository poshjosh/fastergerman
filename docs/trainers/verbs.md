# Prompt used to generate the verbs

Generate data for the first 100 most frequently used German verbs. The data is intended to be used for language learning purposes, in a multiple choice test. Each data represents a question.
For each question specify the following:

-	The verb.
-	An example sentence in German with a blank space for the verb.
-	A translation to English for the German example sentence.
-	Four verbs to be used as choices in a multi-choice question (only one of the verbs must be the right answer).
-   The right answer.
-   The language level ranging from A1 to C2 in this order A1, A2, B1, B2, C1, C2. The language leve
    is the highest level for which the question is appropriate.

Make sure to include questions for each language level in the data.

No language level should have more than 30 percent of the questions.

Generate the data in json format, an example of which is shown below:

[
    {
        "verb": "sein",
        "example": "Ich ___ ein Student.",
        "translation": "I am a student.",
        "choices": ["bist", "sind", "ist", "sein"],
        "answer": "bin",
        "level": "A1"
    },
    {
        "verb": "entwickeln",
        "example": "Das Unternehmen ___ neue Technologien.",
        "translation": "The company develops new technologies.",
        "choices": ["entwickle", "entwickelt", "entwickeln", "entwicklest"],
        "answer": "entwickelt",
        "level": "B1"
    }
]


