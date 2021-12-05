import requests
import json
import unittest
import os
import sqlite3

def get_scored(season1, season2, team):
    """
    This function takes two seasons(for example 2018,2019- will return data for 2018-2019 and 2019-2020 seasons).
    and a team. It will call the balldontlie API to get the points scored dat for that team in that season.
    It will return the data as a list integers that represent the points scored in each game that season.
    """
    page = 1
    scored_home_list = []
    scored_away_list = []
    base_url = 'https://www.balldontlie.io/api/v1/games?seasons[]={}&seasons[]={}&team_ids[]={}&page={}'
    request_url = base_url.format(season1, season2, team, page)

    r = requests.get(request_url)
    data = r.json()
    dict_list = data
    # data = r.text
    # dict_list = json.loads(data)
    # print(dict_list)
    total_pages = dict_list['meta']['total_pages']

    for page in range(total_pages):
        for i in dict_list['data']:
            if i['home_team']['id'] == team:
                scored_home_list.append((i['date'][:10],i['home_team']['full_name'],i['home_team_score']))
            elif i['visitor_team']['id'] == team:
                scored_away_list.append((i['date'][:10],i['visitor_team']['full_name'],i['visitor_team_score']))
        page += 1
        base_url = 'https://www.balldontlie.io/api/v1/games?seasons[]={}&seasons[]={}&team_ids[]={}&page={}'
        request_url = base_url.format(season1, season2, team, page)
        r = requests.get(request_url)
        data = r.json()
        dict_list = data

    print(scored_home_list)
        # print("Number of items: *{}*".format(len(scored_home_list)))
    print()
    print(scored_away_list)
        # print("Number of items: *{}*".format(len(scored_away_list)))

    # return scored_home_list, scored_away_list

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

def setup_points_table(cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Points(id INTEGER PRIMARY KEY, team_name STRING, date DATE,court INTEGER, points_scored_recieved INTEGER)")
    conn.commit()
    # count = 0
    # try:

    
# def add_data_to_db(scored, recieved, cur, conn):

    

def main():
    year1 = 2018
    year2 = 2019
    list = get_scored(year1, year2, 1)
    print(list)

    cur, conn = setUpDatabase('nba_game_stats.db')
    create_court_table(cur, conn)
    setup_points_table(cur,conn)



# def main():
#     # SETUP DATABASE AND TABLE
#     cur, conn = setUpDatabase('game_stats.db')
    
    
if __name__ == "__main__":
    main()