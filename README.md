# TableTennisEloRating
Script for managing a table tennis table based on conventional ELO-rating

## General description
The script processes a list of matches. The matches are read from a json containing a list of matches, where each match describe
name of player 1, name of player 2, winner and match date.

The script populates a list of players as they appear in the list of matches. New players are added with default parameter values 
and recurring playes will have their values updated based on match results.

Players are differentiated by name and must be unique. A different spelling will result in a new player. And two players cannot have 
the same name and should be differentiated if so. 

The table tennis matches will always have a winner, but the script will recognise a draw if "winner":"draw". A player should not be named draw.

After successfully processing the list of matches, the development in rating is plotted as a function of time, and plotted in a pdf-report 
together with the current table sorted on elo rating.

## Description of JSON

The JSON should be on the following format:

'
[
    {
        "kamp_nr": 1,
        "player_1": "Alice",
        "player_2": "Bob",
        "winner": "Bob",
        "dato": "01.01.1970"
    },
    {
        "kamp_nr": 2,
        "player_1": "Bob",
        "player_2": "Charlie",
        "winner": "Charlie",
        "dato": "02.01.1970"
    },
    {
        "kamp_nr": 3,
        "player_1": "Charlie",
        "player_2": "Alice",
        "winner": "Alice",
        "dato": "03.01.1970"
    }
]

