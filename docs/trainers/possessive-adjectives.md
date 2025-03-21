# Prompt used to generate the questions for possessive-adjectives

Generate data for the 100 most frequently used German possessive adjectives. The data is intended to 
be used for language learning purposes, in a multiple choice test. Each data represents a question.
For each question specify the following:

-	An example sentence in German with a blank space for the possessive adjective.
-	A translation to English for the German example sentence.
-	Five possessive adjectives to be used as choices in a multi-choice question (only one of the choices must be the right answer).
-   The right answer.
-   The language level ranging from A1 to C2 in this order A1, A2, B1, B2, C1, C2. The language level
    is the highest level for which the question is appropriate.

Make sure to include questions for each language level in the data.

No language level should have more than 30 percent of the questions.

Generate the data in json format, an example of which is shown below:

[
    {
        "example": "Kann ich ___ Telefonnummer haben?",
        "translation": "Can I have your telephone number?",
        "choices": ["dein", "ihre", "ihren", "ihres", "ihrem"],
        "answer": "ihre",
        "level": "A2"
    },
    {
        "verb": "entwickeln",
        "example": "Sie nimmt ein Medikament. ___ Medikament schmeckt nicht gut.",
        "translation": "She takes medicine. Her medicine doesn't taste good.",
        "choices": ["Sein", "Ihres", "Ihr", "Ihren", "Ihrem"],
        "answer": "Ihr",
        "level": "B1"
    }
]


