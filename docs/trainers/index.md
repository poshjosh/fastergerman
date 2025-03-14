# Trainers

There could be trainers for various language constructs. For example: 
`preposition`, `verb`, `noun`, `adjective`, etc.

## Current Trainers

- [Prepositions](prepositions.md)

- [Verbs](verbs.md)

## Adding a new trainer

To add a trainer for prepositions:

### Add a source file for the trainer's questions.
Example format:
```json
{
  "type": "preposition",
  "description": "German verbs and their prepositions",
  "questions": [
    {
      "verb": "warten",
      "answer": "auf",
      "example": "Ich warte ___ den Bus.",
      "translation": "I'm waiting for the bus.",
      "choices": ["mit", "für", "zu", "auf" ]
    }
  ]
}
```
- See [this sample](../src/resources/config/questions/preposition.json)
- You can generate questions using [this prompt](./prompt.md)

### Add translations for the trainer's display name.

- See translation for `PREPOSITION_TRAINER` in [i18n.py](../src/fastergerman/i18n.py)

### Deploy the app
