# use the nhl pulled up, all info of a player and store first name and last name with countryCode for example 1 fro Canada 2 for Russia and then create another table where 1 equals Canada therefore when I join these two tables one is a key to the other one, plot for example average height for each country that players are drafted from


#first function I need to take players ID, height, country, draft date (two different tables for 2000 and 2020 + 1 table with country code USA : 1, Canada : 2)

import requests
import json
import unittest
import os
import sqlite3
import csv
import re
import numpy as np
import pandas
import matplotlib
from textwrap import wrap
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter

def get_info(year1):
    """
    This function takes two draft years 2000 and 2020, players ID, player's hieght, players country
    It will call the nhl API to get the mentioned data.
    It will return the data as a list integers that represent the points scored in each game that season.
    """

    data_list = []
    base_url = 'https://records.nhl.com/site/api/draft?cayenneExp=draftYear={}'
    request_url = base_url.format(year1)

    r = requests.get(request_url)
    data = r.json()
    dict_list = data

    for x in dict_list['data']:
        data_list.append((x['id'], x['height'], x['countryCode'], x['draftDate']))
    # print(data_list)
        
    return data_list

# Create Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn

def create_country_table(cur, conn, data_list):

    # cur.execute("DROP TABLE Country")
    cur.execute("CREATE TABLE IF NOT EXISTS Country (id INTEGER PRIMARY KEY, CountryCode TEXT)")

    country_dict = {}
    for x in data_list:
        if x[2] not in country_dict and x[2] != None:
            country_dict[x[2]] = 1   
    # print(country_dict)
    i = 1
    for code in country_dict:
        cur.execute('INSERT OR IGNORE INTO Country (id, CountryCode) VALUES (?,?)', (i, code,))
        i += 1
    conn.commit()

def create_player_table(cur, conn, data_list):

    # cur.execute("DROP TABLE Players")
    cur.execute("CREATE TABLE IF NOT EXISTS Players (PlayersId INTEGER PRIMARY KEY, Height INTEGER, DraftDate STRING, CountryCode INTEGER)")
    conn.commit()

    cur.execute('SELECT * from Players')
    rows = cur.fetchall()
    # print(rows)
    data_lst = []
    for x in rows:
        data_lst.append(x[0])
    #copy all rows in a list of tuples and then check in the condition below if element in this list of tuples
    if data_lst == []:
        count = 0
        for element in data_list:
            if element[1] != None and count < 25:
                
                cur.execute('SELECT id FROM Country WHERE CountryCode= ?', (element[2],))
                category_id = int(cur.fetchone()[0])
                # print(category_id)
                cur.execute("INSERT OR IGNORE INTO Players (PlayersId, Height, DraftDate, CountryCode) VALUES (?,?,?,?)",(element[0], element[1], element[3], category_id))
            count += 1
        
        conn.commit()

    # print(data_lst)
    number = 0
    for item in data_list:
        # print(item)
        if item[1] != None and item[0] not in data_lst and number < 25:
            cur.execute('SELECT id FROM Country WHERE CountryCode= ?', (item[2],))
            new_id = int(cur.fetchone()[0])
            # print("!!!!!!!!!!!!!!")
            cur.execute("INSERT OR IGNORE INTO Players (PlayersId, Height, DraftDate, CountryCode) VALUES (?,?,?,?)",(item[0], item[1], item[3], new_id))
            number += 1

    conn.commit()

def get_data(cur, conn):
    cur.execute('SELECT Country.CountryCode, Players.Height FROM Country JOIN Players ON Players.CountryCode = Country.id')
    data = cur.fetchall()
    #print(data)

    data_dict = {}
    for x in data:
        if x[0] in data_dict.keys():
            data_dict[x[0]].append(x[1])

        else:
            data_dict[x[0]] = []
            data_dict[x[0]].append(x[1])

    # print(data_dict)
    return data_dict

def create_calculation(data_dict, file):
    # loop through dict and put in txt
    
    dir = os.path.dirname(__file__)
    out_file = open(os.path.join(dir, file), "w")
    with open(file) as f:
        csv_writer = csv.writer(out_file, delimiter=",", quotechar='"')
        csv_writer.writerow(["Country"," Number Appearances", " Average Height"])
        for keys, values in data_dict.items():
            # print(keys)
            #the sum of heights
            total_sum = sum(values)
            # print(total_sum)
            # number of drafted players by country
            num_players = len(values)
            # print(num_players)
            # average height per country, 2 decimals
            average_height_per_country = total_sum / num_players
            # print(format(average_height_per_country, ".2f"))
            
            # writting the txt file
            csv_writer.writerow([keys, num_players, format(average_height_per_country, ".2f")])

def bar_chart(cur, data_dict):

    fig = plt.figure(figsize=(20,8))
    # ax1 = fig.add_subplot()   
    
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

    # print(country_lst)
    # print(num_players)
    # print(avg_height)

    plt.subplot(1,3,1)

    plt.bar(country_lst[:4], avg_height[:4], color="blue", width=0.2)
    plt.axhline(y = avg_line, color = 'r', linestyle = '-')

    plt.ylim(71.6, 72.5)

    plt.xlabel("Country Code")
    plt.ylabel("Average height of drafted player in inches")
    plt.title("Average height of drafted players per country")

    plt.subplot(1,3,2)
    plt.bar(country_lst[4:9], avg_height[4:9], color="yellow", width=0.2)
    plt.axhline(y = avg_line, color = 'r', linestyle = '-')

    plt.ylim(71.6, 72.5)

    plt.xlabel("Country Code")
    plt.ylabel("Average height of drafted player in inches")
    plt.title("Average height of drafted players per country")

    plt.subplot(1,3,3)
    plt.bar(country_lst[9:], avg_height[9:], color="blue", width=0.2)
    plt.axhline(y = avg_line, color = 'r', linestyle = '-')

    plt.ylim(71.6, 72.5)

    plt.xlabel("Country Code")
    plt.ylabel("Average height of drafted player in inches")
    plt.title("Average height of drafted players per country")

    fig.tight_layout(pad=2.5)

    plt.show()

    # do average of height for each country and store these values in a list so that you have list of values and each value represents avg height for particular country
    # use three things to plot: 1)x-axis countrycodes 2)y-axis bar chart values for avg height per countrycode (13 bar lines) 3) line over the chart signifying the average for all countries

def main():

    d_year2 = 2020
    data_list = get_info(d_year2)

    cur, conn = setUpDatabase('nhl_draft_data.db')

    create_country_table(cur, conn, data_list)
    create_player_table(cur, conn, data_list)

    data_dict = get_data(cur, conn)

    create_calculation(data_dict, 'nhl_draft.txt')

    bar_chart(cur, data_dict)
 
if __name__ == "__main__":
    main()