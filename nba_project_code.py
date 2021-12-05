import requests
import json
import unittest
import os
import sqlite3

def get_scored(season1, season2, team, page):
    """
    This function takes two seasons(for example 2018,2019- will return data for 2018-2019 and 2019-2020 seasons).
    and a team. It will call the balldontlie API to get the points scored dat for that team in that season.
    It will return the data as a list integers that represent the points scored in each game that season.
    """
    points_list = []
    base_url = 'https://www.balldontlie.io/api/v1/games?seasons[]={}&seasons[]={}&team_ids[]={}&page={}'
    request_url = base_url.format(season1, season2, team, page)

    r = requests.get(request_url)
    data = r.json()
    dict_list = data

    for i in dict_list['data']:
        if i['home_team']['id'] == team:
            points_list.append((i['date'][:10],i['home_team']['id'], 0,i['home_team_score']))
        elif i['visitor_team']['id'] == team:
            points_list.append((i['date'][:10],i['visitor_team']['id'], 1,i['visitor_team_score']))

    return points_list

# Create Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def create_court_table(cur,conn):
    court = ["Home", "Away"]
    cur.execute("CREATE TABLE IF NOT EXISTS Courts(id INTEGER PRIMARY KEY, title TEXT)")
    for i in range(len(court)):
        cur.execute("INSERT OR IGNORE INTO Courts (id, title) VALUES (?,?)", (i,court[i]))
    conn.commit()

def create_teams_table(cur, conn):
    re =requests.get('https://www.balldontlie.io/api/v1/teams')
    data = re.json()
    dict_list = data
    teams = []
    cur.execute("CREATE TABLE IF NOT EXISTS Teams(id INTEGER PRIMARY KEY, title TEXT)")
    for i in dict_list['data']:
        id = i['id']
        name = i['full_name']
        cur.execute('INSERT OR IGNORE INTO Teams (id, title) VALUES (?,?)', (id, name))
    conn.commit()


def setup_points_table(data, cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Points(id INTEGER PRIMARY KEY, team_name STRING, date DATE,court INTEGER, points_scored_recieved INTEGER)")
    conn.commit()
    try:
        cur.execute('SELECT id FROM Points WHERE id  = (SELECT MAX(id) FROM Points)')
        start = cur.fetchone()
        start = start[0]
    except:
        start= 0
    count = 1
    for i in data:
        team_name = i[1]
        date = i[0]
        court = i[2]
        points = i[3]
        id = start + count
        cur.execute("INSERT OR IGNORE INTO Points (id, team_name, date, court, points_scored_recieved) VALUES(?,?,?,?,?)", (id, team_name, date, court, points))
        count += 1
    conn.commit()

def main():
    year1 = 2018
    year2 = 2019

    cur, conn = setUpDatabase('nba_game_stats.db')
    create_court_table(cur, conn)
    create_teams_table(cur, conn)

#To gather all data for both seasons, run code 6 times.
    try:
        cur.execute('SELECT id FROM Points WHERE id  = (SELECT MAX(id) FROM Points)')
        start = cur.fetchone()
        start = start[0]
        page = (start+25) / 25
    except:
        page = 1
    data = get_scored(year1, year2, 1, page)
    setup_points_table(data, cur, conn)



# def main():
#     # SETUP DATABASE AND TABLE
#     cur, conn = setUpDatabase('game_stats.db')
    
    
if __name__ == "__main__":
    main()