# Prompt used to generate the questions for conjunctions

Generate data for the 100 most frequently used German conjunctions. The data is intended to
be used for language learning purposes, in a multiple choice test. Each data represents a question.
For each question specify the following:

-	An example sentence in German with a blank space for the conjunction.
-	A translation to English for the German example sentence.
-	Five conjunctions to be used as choices in a multi-choice question (only one of the choices must be the right answer).
-   The right answer.
-   The language level ranging from A1 to C2 in this order A1, A2, B1, B2, C1, C2. The language level
    is the highest level for which the question is appropriate.

OUTPUT FORMAT

Generate the data in json format, an example of which is shown below:

{
    "type": "conjunction",
    "questions": [
        {
            "example": "Ich bin müde, ___ ich muss zur Schule gehen.",
            "translation": "I am tired, but I have to go to school.",
            "choices": ["oder", "deshalb", "aber", "denn", "anstatt"],
            "answer": "aber",
            "level": "A2"
        },
        {
            "example": "___ ich jung war, war ich sehr frech.",
            "translation": "When I was young, I was very cheeky.",
            "choices": ["Wenn", "Als", "Anstatt", "Bevor", "Dass"],
            "answer": "Als",
            "level": "B1"
        }
    ]
}

Here is a list of German conjunctions:

#1 Aber – But
#2 Denn – Because
#3 Doch – After All, But
#4 Natürlich – Naturally, Of Course
#5 Obwohl – Although, Even Though
#6 Sonst – Otherwise, Or
#7 Weil – Because
#8 Zum Beispiel – For Example
Speak Like A Native With These German Conjunctions Of Time
#9 Am Anfang, Anfangs – At First, At the Beginning
#10 Am Ende, Endlich, Zum Schluss, Schließlich – Lastly, Finally, In the End
#11 Auf Einmal – Suddenly, At Once
#12 Bald – Soon, Shortly
#13 Bisher – Up Until Now, So Far
#14 Damals – Back Then
#15 Danach – After, Afterward
#16 Dann – Then
#17 Eher – More Likely, Rather
#18 Früher, Vorher – Back Then, Earlier, Previously
#19 Gleichzeitig, Zur Gleichen Zeit – At the Same Time, Simultaneously
#20 Immer Noch – Still
#21 In der Zukunft, Zukünftig – In The Future
#22 Inzwischen – Meanwhile, In The Meantime
#23 Jetzt – Now
#24 Mittlerweile, Unterdessen – Meanwhile, For The Time Being
#25 Nachdem – After
#26 Nachher – Later, Afterward
#27 Neulich – Recently
#28 Noch – Still
#29 Plötzlich – Suddenly
#30 Schließlich – Eventually, After All, Ultimately
#31 Seitdem, Seither – Since Then
#32 Sobald – As Soon As
#33 Vor Kurzem – Recently, Lately
#34 Zuerst – First, At First
#35 Zuletzt – At the End, Last
#36 Zum Ersten/Zweiten Mal – For The First/Second Time
#37 Zunächst – For Now, First of All
German Connectors To Express Your Opinions
#38 Auf der anderen Seite, Andererseits – On The Other Hand
#39 Auf der einen Seite, Einerseits – On The One Hand
#40 Auf jeden Fall, Jedenfalls – Definitely, In Any Case
#41 Aus diesem Grund – For This Reason
#42 Es scheint mir, dass – It Seems To Me That…
#43 Sozusagen – So To Speak, In A Matter Of Speaking
German Connecting Words To Transition Topics
#44 Also – Hence, So
#45 Außerdem – In Addition, Besides
#46 Beispielsweise, Zum Beispiel – For Example
#47 Das Heißt – That Means
#48 Deshalb, Deswegen – That's Why
#49 Ganz im Gegenteil – On The Contrary
#50 Immerhin – After All, At Least
#51 Wobei – Whereby
#52 Zumindest – At Least
Improve Your German With These Connectors
#53 Daher, Darum – Therefore, Because Of That
#54 Daraufhin – Consequently, Subsequently, With Regard To
#55 Darüber Hinaus – Furthermore, In Addition
#56 Dennoch, Jedoch – Nevertheless, Yet, Still
#57 Im Wesentlichen – Essentially, Fundamentally
#58 Indessen – Meanwhile
#59 Stattdessen – Instead
German Connecting Words To Add Emphasis
#60 Eben, Gerade – Just
#61 Einmal – Once
#62 Erst – Only
#63 Grundsätzlich – Basically
#64 Im Großen und Ganzen – Overall
#65 Kurz Gesagt – In A Nutshell
#66 Tatsächlich – Actually, Really
#67 Trotzdem – Nevertheless, Nonetheless
#68 Übrigens – By The Way
#69 Weiter – Further
#70 Wenigstens – At Least
#71 Zumeist – Mostly 

Use the above list to generate more questions. Exclude those conjunctions for which you 
already generated questions in the last chats today