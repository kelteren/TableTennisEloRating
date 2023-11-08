"""The script processes a list of matches. The matches are read from a json containing a list of matches, where each match describe
name of player 1, name of player 2, winner and match date.

The script populates a list of players as they appear in the list of matches. New players are added with default parameter values 
and recurring playes will have their values updated based on match results.

Players are differentiated by name and must be unique. A different spelling will result in a new player. And two players cannot have 
the same name and should be differentiated if so. 

The table tennis matches will always have a winner, but the script will recognise a draw if "winner":"draw". A player should not be named draw.

After successfully processing the list of matches, the development in rating is plotted as a function of time, and plotted in a pdf-report 
together with the current table sorted on elo rating.

"""

# importing necessary modules
import json
import re
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from fpdf import FPDF
from tkinter import filedialog
from prettytable import PrettyTable as PrettyTable


"""
The validate_json function takes a JSON object as input and returns True if the JSON data has 
sequentially numbered "match_no", always a valid winner, and the dates are in sequence. It 
returns False otherwise.

In the main code block, we've defined the JSON data as a Python dictionary and then passed 
it to the validate_json function. The function returns a message to the console indicating 
whether the JSON data is valid or not.

The validate_json functions needs further development

"""
def validate_json(json_data):
    """
    Unfinished
    Validates the given JSON data to ensure that it has sequentially numbered "match_no",
    always a valid winner, and that the dates are in sequence.

    Args:
        json_data (dict): A dictionary representing the JSON with match data.

    Raises:
        ValueError: If any of the checks fail.

    Returns:
        None
    """
    match_no = 0
    date = ""
    for match in json_data:
        if match["match_no"] != match_no+1:
            raise ValueError("Invalid JSON data: match_no is not sequential")
        match_no = match["match_no"]
#        if match["winner"] not in [match["player_1"], match["player_2"]]:
#            raise ValueError("Invalid JSON data: Invalid winner")
#        if not re.match(r'\d{2}\.\d{2}\.\d{4}', match["dato"]):
#            print("Warning: Invalid date format. Must be dd.mm.yyyy")
#        try:
#            #FIXME change the use of datetime here, conflict with initial import and use of dt
#            dt = datetime.strptime(match["dato"], '%d.%m.%Y')
#        except ValueError:
#            raise ValueError("Invalid JSON data: Invalid date")#
#
#        if date == "":
#            date = match["dato"]
#        elif dt.date() <= datetime.strptime(date, '%d.%m.%Y').date():
#            raise ValueError("Invalid JSON data: date not sequential")
#        date = match["dato"]  


#TODO: ADD in case standard file is not found, a dialog will open to let the user specify correct file
#TODO: ADD add so that filename is collected from *kwargs if this script is run from a command line
# let the user chose a json file, and reads the list of mathces from json
# file = 'matches.json'
file_path = filedialog.askopenfilename(filetypes=(("JSON-files", "*.json"), ("All files", "*.*")))

if file_path:
    with open(file_path,'r') as f:
        #json_data = json.load(f)
        matches = json.load(f)

#FIXME: wait using this until the datetime check in validate_json() works properly
try:
    validate_json(matches)
    print("JSON data is valid", end="\n\n")
except ValueError as e:
    print(str(e))

# creates empty dictionary of players and elo ratings
players = {}
elo_data = {}

for match in matches:
    """loops trough the matches in the list, in case a player is not in the players dictionary,
    the player will be added to the dictionary with initial rating, zero games played and 
    standard k-factor

    players added gets an initial 1200 elo rating dated the day before the first match played. this 
    might appear odd when a new player joins the rating system, but is not a real problem. no need 
    to change unless there is a more elegant way of doing it

    when two players meet in a match, the expected score/rating is calculated based on standard
    elo-formula and used for calculation of new rating based on actual match result

    after one match is processed, date in the player dictionay is updated, and the new player 
    strength is saved. The new player rating is stored in two places; as current value in player{}
    and as last value in elo_data{}

    this means that the sequence of matches played matters, as the new expected score will be
    updated immediately after a match is played, while in reality the expected score should be 
    the same for at least all matches on the same day/in the same tournament.
    """
    
    # reads and formats the date from the current match
    match_date = dt.datetime.strptime(match['date'], '%d.%m.%Y')

    # sets the date for the last played match for use in the PDF-report title field
    last_match_date = max([dt.datetime.strptime(match['date'], '%d.%m.%Y') for match in matches]).strftime('%Y-%m-%d')

    # sets the date for the last played match for use in the PDF-report title field
    num_matches = len([(match['match_no']) for match in matches])

    # in case new player not in the list, new player is added with initial values. initial rating is set for the day before first match played
    if match['player_1'] not in players:
        players[match['player_1']] = {'rating': 1200, 'games_played': 0, 'games_won': 0, 'games_lost': 0, 'k_factor': 32}
        initial_date = match_date - dt.timedelta(days=1)
        elo_data[match['player_1']] = {initial_date:1200}
    if match['player_2'] not in players:
        players[match['player_2']] = {'rating': 1200, 'games_played': 0, 'games_won': 0, 'games_lost': 0, 'k_factor': 32}
        initial_date = match_date - dt.timedelta(days=1)
        elo_data[match['player_2']] = {initial_date:1200}

    # read players and result from current match
    player_1 = match['player_1']
    player_2 = match['player_2']
    winner = match['winner']

    # reads current rating of players, this will be set to 1200 if first match
    player_1_rating = players[player_1]['rating']
    player_2_rating = players[player_2]['rating']

    # reads current k-factor of players, this will be set to 32 if first match
    #TODO: insert breakpoint in k-factor here;elo<2100: K=32, 2100
    #TODO: insert breakpoint in k-factor based on number of games played, at least 30 games played before changing k-factor?
    player_1_k_factor = players[player_1]['k_factor']
    player_2_k_factor = players[player_2]['k_factor']

    # value used for new rating is set based on the result
    # ! note that this formula caters for a draw result which can be gives as "winner": "draw", unless a player is named draw
    if winner == player_1:  # winner must be given in json with name of player who wins, fx "winner":"Alice"
        player_1_score = 1
        player_2_score = 0
        players[player_1]['games_won'] += 1
        players[player_2]['games_lost'] += 1  
    elif winner == player_2:
        player_1_score = 0
        player_2_score = 1
        players[player_2]['games_won'] += 1
        players[player_1]['games_lost'] += 1 
    else:
        print("fant en kamp uten vinner: kamp nr:", match['match_no'])
        player_1_score = 0.5
        player_2_score = 0.5

    # expected score is calculated based on elo-strength of each player, standard implementation
    player_1_expected_score = 1 / (1 + 10**((player_2_rating - player_1_rating) / 400))
    player_2_expected_score = 1 / (1 + 10**((player_1_rating - player_2_rating) / 400))
    
    # new score is calculated based on expected result
    player_1_new_rating = player_1_rating + player_1_k_factor * (player_1_score - player_1_expected_score)
    player_2_new_rating = player_2_rating + player_2_k_factor * (player_2_score - player_2_expected_score)
    
    # new score is stored in players{}
    players[player_1]['rating'] = player_1_new_rating
    players[player_2]['rating'] = player_2_new_rating

    # last score is stored in players{} along with match date
    # if current match is on the same date as a previous match, the previous score on the same day will 
    # be overwritten. this is not a bug
    elo_data[player_1][match_date] = player_1_new_rating
    elo_data[player_2][match_date] = player_2_new_rating

    # number of matches in players{} is incremented
    players[player_1]['games_played'] += 1
    players[player_2]['games_played'] += 1
    
# prints a table using the module PrettyTable
# dictionary of players is sorted on rating before each player is added to the table with
# the columns name, rating, matches played, matches won and matches lost

t = PrettyTable(['Name','Rating','Played','Won','Lost'])
sorted_players = sorted(players.items(), key=lambda x: x[1]['rating'], reverse=True)
for player, properties in sorted_players:
    t.add_row([player, round(properties["rating"], 0), properties["games_played"], properties["games_won"], properties["games_lost"]])
t.align['Name'] = 'r'

# plotting elo rating development for each player based on list in elo_data{}
for player, ratings in elo_data.items():
    dates = list(ratings.keys())
    ratings = list(ratings.values())
    plt.plot(dates, ratings,'-x', label=player)

plt.xlabel('Date')
plt.ylabel('Elo development')
plt.title('Elo development of players \n vs date played')
plt.legend()

# formats dates on x-axis as year-month-day
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#TODO: set tick intervals on x-akse to 1/10 - 1/15 of the width of the x-axis/time period
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))  # setting tick inteval to avoid packed x-axis
plt.gcf().autofmt_xdate()  # rotating date labels for better visibility

# created pdf-report
class PDF(FPDF):
    def header(self):
#        self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 18)
        self.cell(80)
        self.cell(30, 10, '<title of the report>', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', '', 16)
pdf.ln(10)

# adds table in the pdf-report
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Current table', 0, 1, 'L')
pdf.set_font('Arial', '', 16)
pdf.cell(0, 10, f'A total of {num_matches} matches has been played up until {last_match_date}', 0, 1, 'L')  # Include last match date in the title
pdf.set_font('Courier', '', 16)
pdf.ln(5)
pdf.multi_cell(0, 5, t.get_string(), 0, 'L')
pdf.ln(10)
pdf.set_font('Arial', '', 16)

# adding figure to pdf-report
plt.savefig('elo_rating.png')
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Player statistics - Elo rating over time', 0, 1, 'L')
pdf.set_font('Arial', '', 16)
pdf.ln(5)
pdf.image('elo_rating.png', x=10, y=None, w=180)

# assembling filename from current date and text-string
title = dt.datetime.today().strftime('%Y-%m-%d') + ' - Table tennis elo rating.pdf'
pdf.output(title, 'F')

pdf.close()
plt.close()


'''
#TODO: ADD if relevant
# check if this file is run as a independent program of as an imported module i another program
# if run as independent program, rund main()

if __name__ == "__main__"
    main()

'''