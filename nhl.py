import requests
import json
import os
import sqlite3
import csv
import numpy as np
from textwrap import wrap
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter

def get_info(year1):
    """
    This function takes a draft year
    It will call the nhl API to get the mentioned data.
    It will return the data as a list of all the data from API call.
    """

    data_list = []
    base_url = 'https://records.nhl.com/site/api/draft?cayenneExp=draftYear={}'
    request_url = base_url.format(year1)

    r = requests.get(request_url)
    data = r.json()
    dict_list = data

    for x in dict_list['data']:
        data_list.append((x['id'], x['height'], x['countryCode'], x['draftDate']))
        
    return data_list

def setUpDatabase(db_name):
    """This function takes in a file name and it creates connection and cursor"""
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn

def create_country_table(cur, conn, data_list):
    """This function takes in cursor, connection and data_dict which is a dictionary consisting of country code and heigh of every player.
    It creates a table of countries information, accounts for duplicates and assignes them numbers to connect them to other table.
    The reason is to avoid duplicate data in one table."""

    cur.execute("CREATE TABLE IF NOT EXISTS Country (id INTEGER PRIMARY KEY, CountryCode TEXT)")

    country_dict = {}
    for x in data_list:
        if x[2] not in country_dict and x[2] != None:
            country_dict[x[2]] = 1   
    
    i = 1
    for code in country_dict:
        cur.execute('INSERT OR IGNORE INTO Country (id, CountryCode) VALUES (?,?)', (i, code,))
        i += 1
    conn.commit()

def create_player_table(cur, conn, data_list):
    """This function takes in cursor, connection and data_dict which is a dictionary consisting of country code and heigh of every player.
    It creates a table of players information, accounts for duplicates."""

    cur.execute("CREATE TABLE IF NOT EXISTS Players (PlayersId INTEGER PRIMARY KEY, Height INTEGER, DraftDate STRING, CountryCode INTEGER)")
    conn.commit()

    cur.execute('SELECT * from Players')
    rows = cur.fetchall()
    
    data_lst = []
    for x in rows:
        data_lst.append(x[0])

    if data_lst == []:
        count = 0
        for element in data_list:
            if element[1] != None and count < 25:
                
                cur.execute('SELECT id FROM Country WHERE CountryCode= ?', (element[2],))
                category_id = int(cur.fetchone()[0])

                cur.execute("INSERT OR IGNORE INTO Players (PlayersId, Height, DraftDate, CountryCode) VALUES (?,?,?,?)",(element[0], element[1], element[3], category_id))
            count += 1
        
        conn.commit()

    number = 0
    for item in data_list:
        
        if item[1] != None and item[0] not in data_lst and number < 25:
            cur.execute('SELECT id FROM Country WHERE CountryCode= ?', (item[2],))
            new_id = int(cur.fetchone()[0])
            cur.execute("INSERT OR IGNORE INTO Players (PlayersId, Height, DraftDate, CountryCode) VALUES (?,?,?,?)",(item[0], item[1], item[3], new_id))
            number += 1

    conn.commit()

def get_data(cur, conn):
    """This function takes in cursor and connection
    uses JOIN SQL function to gather data from two tables in teh databse and return a sorted dictionary"""

    cur.execute('SELECT Country.CountryCode, Players.Height FROM Country JOIN Players ON Players.CountryCode = Country.id')
    data = cur.fetchall()
    
    data_dict = {}
    for x in data:
        if x[0] in data_dict.keys():
            data_dict[x[0]].append(x[1])

        else:
            data_dict[x[0]] = []
            data_dict[x[0]].append(x[1])

    return data_dict

def create_calculation(data_dict, file):
    """This function takes in data_dict which is a dictionary consisting of country code and heigh of every player.
    and a file. Then it creates a path and writes calculated heights into the file with first row as a description."""
    
    dir = os.path.dirname(__file__)
    out_file = open(os.path.join(dir, file), "w")
    with open(file) as f:
        csv_writer = csv.writer(out_file, delimiter=",", quotechar='"')
        csv_writer.writerow(["Country"," Number of Players for Country", " Average Height"])
        for keys, values in data_dict.items():
            
            #the sum of heights
            total_sum = sum(values)
            
            # number of drafted players by country
            num_players = len(values)
            
            # average height per country
            average_height_per_country = total_sum / num_players
           
            # writting the txt file
            csv_writer.writerow([keys, num_players, format(average_height_per_country, ".2f")])

def bar_chart(cur, data_dict):
    """This function takes in a cursor and data_dict 
    which is a dictionary consisting of country code and heigh of every player.
    Then calculates different values to get the average and then it creates a bar graph with
    all necessary information"""

    fig = plt.figure(figsize=(20,8))
    
    country_lst = []
    avg_height = []
    total_sum = 0
    num_players = 0
    avg_line = []
    for keys, values in data_dict.items():
        country_lst.append(keys)

        total_sum += sum(values)
        num_players += len(values)

        average_height_per_country = total_sum / num_players
        avg_height.append(average_height_per_country)

    average_line = total_sum / num_players
    avg_line.append(average_line)

    # plotting the graph
    plt.bar(country_lst, avg_height, color="blue", edgecolor="black", width=0.2)
    plt.axhline(y = avg_line, color = 'r', linestyle = '-')

    # average line
    location = avg_line[0]
    plt.text(-1,location, '72.12', color="red", ha="center", va="center")

    # zoom of y-axis
    plt.ylim(71.6, 72.5)

    # legend of the graph
    plt.xlabel("Country Code")
    plt.ylabel("Average height of drafted player in inches")
    plt.title("Average height of drafted players per country")

    # displays the graph
    plt.show()

def main():
    """run the code 9 times to see visualization and to get all the data from API"""

    d_year2 = 2020
    data_list = get_info(d_year2)

    cur, conn = setUpDatabase('sports_data.db')

    # creating tables in databse
    create_country_table(cur, conn, data_list)
    create_player_table(cur, conn, data_list)

    # make sure it displays the visualization only at the end
    x = cur.execute('SELECT COUNT(*) FROM Players')
    x = cur.fetchall()
    if x[0][0] == 216:
        # gets data and stores them into a variable
        data_dict = get_data(cur, conn)
        # makes the calculation of different heights and stores them into a txt file
        create_calculation(data_dict, 'nhl_draft.txt')
        # creates a visualization graph
        bar_chart(cur, data_dict)
 
if __name__ == "__main__":
    main()