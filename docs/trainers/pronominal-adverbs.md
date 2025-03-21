# Prompt used to generate the questions for pronominal-adverbs

A pronominal adverb is a type of adverb occurring in a number of Germanic languages, formed in
replacement of a preposition and a pronoun by turning the former into a prepositional adverb
and the latter into a locative adverb, and finally joining them in reverse order.

For example:

- In that → therein
- By this → hereby
- To this → hereto
- In which → wherein

INSTRUCTION

Generate data for the 100 most frequently used German pronominal adverbs. The data is intended to
be used for language learning purposes, in a multiple choice test. Each data represents a question.
For each question specify the following:

-	An example sentence in German with a blank space for the pronominal adverb.
-	A translation to English for the German example sentence.
-	Five pronominal adverbs to be used as choices in a multi-choice question (only one of the choices must be the right answer).
-   The right answer.
-   The language level ranging from A1 to C2 in this order A1, A2, B1, B2, C1, C2. The language level
    is the highest level for which the question is appropriate.

OUTPUT FORMAT

Generate the data in json format, an example of which is shown below:

{
    "type": "pronominal-adverb",
    "questions": [
        {
            "example": "Ich erinnere mich ___",
            "translation": "I remember that/it",
            "choices": ["darüber", "davon", "daran", "dagegen", "damit"],
            "answer": "daran",
            "level": "B2"
        },
        {
            "example": "Sie träumt schon lange ___, im Ausland zu leben.",
            "translation": "She has long dreamed of living abroad.",
            "choices": ["darüber", "davon", "daran", "dagegen", "damit"],
            "answer": "davon",
            "level": "C1"
        }
    ]
}