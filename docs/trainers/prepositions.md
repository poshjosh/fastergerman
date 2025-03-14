# Prompt used to generate the prepositions

List the 200 most frequently used German verbs and the specific prepositions they are typically used with.

For each verb specify the following:
-	Specific preposition that verb is typically used with.
-	An example sentence in German.
-	A translation for the sentence.
-	Four other prepositions to be used as ‘wrong’ choices in a multi-choice question.

Generate the data in json format, an example of which is shown below:

VERB_DATA = [
    {
        "verb": "warten",
        "answer": "auf",
        "example": "Ich warte ___ den Bus.",
        "translation": "I'm waiting for the bus.",
        "choices": ["mit", "für", "zu", "auf"]
    },
    {
        "verb": "denken",
        "answer": "an",
        "example": "Ich denke ___ meine Familie.",
        "translation": "I'm thinking about my family.",
        "choices": ["über", "von", "an", "mit"]
    }
]
