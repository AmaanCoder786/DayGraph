flowchart TD

    HOME["Home<br/>/"]

    ADD["Add Habit<br/>/add-habit"]

    FORM["add_habit.html"]

    DB[("SQLite<br/>habits table")]

    HOME --> ADD

    ADD -->|"GET"| FORM
    FORM -->|"POST"| ADD

    ADD -->|"INSERT habit"| DB
    ADD -->|"redirect('/')"| HOME