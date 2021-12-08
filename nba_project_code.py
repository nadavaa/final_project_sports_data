import requests
import json
import unittest
import os
import sqlite3
import matplotlib
import matplotlib.pyplot as plt

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
    cur.execute("CREATE TABLE IF NOT EXISTS Points(id INTEGER PRIMARY KEY, team_name STRING, date DATE,court INTEGER, points_scored INTEGER)")
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
        cur.execute("INSERT OR IGNORE INTO Points (id, team_name, date, court, points_scored) VALUES(?,?,?,?,?)", (id, team_name, date, court, points))
        count += 1
    conn.commit()

def avg_points_scored(cur,conn):
    cur.execute('''SELECT Teams.title as team_name, strftime('%m', Points.date) as month, Courts.title as court, AVG(Points.points_scored) as avg_scored
                    FROM Points
                    JOIN Teams
                    ON Teams.id = Points.team_name
                    JOIN Courts
                    ON Points.court = Courts.id
                    WHERE Points.court = 0
                    GROUP BY strftime('%m', Points.date)
                    ORDER BY month ="04", month ="03", month ="02", month= "01", month= "12", month ="11", month ="10"''')
    home = cur.fetchall()

    cur.execute('''SELECT Teams.title as team_name, strftime('%m', Points.date) as month, Courts.title as court, AVG(Points.points_scored) as avg_scored
                    FROM Points
                    JOIN Teams
                    ON Teams.id = Points.team_name
                    JOIN Courts
                    ON Points.court = Courts.id
                    WHERE Points.court = 1
                    GROUP BY strftime('%m', Points.date)
                    ORDER BY month ="04", month ="03", month ="02", month= "01", month= "12", month ="11", month ="10"''')
    away = cur.fetchall()

    with open('data_file.txt', 'w') as f:
        f.write('(Team, Month, Court, avg points scored)')
        f.write('\n\n')
        f.write('Home Game Data')
        f.write('\n')
        for i in home:
            f.write(str(i))
            f.write('\n')
        
        f.write('Away Game Data')
        f.write('\n')
        for i in away:
            f.write(str(i))
            f.write('\n')


    return home, away

def viz_one(data):
    team = data[0][0][0]
    months = []
    points_home = []
    points_away = []
    for i in data[0]:
        months.append(i[1])
        points_home.append(i[3])
    for i in data[1]:
        points_away.append(i[3])

    fig,ax = plt.subplots()
    # plot the home points data
    ax.plot(months, points_home, 'bo-', label="Points Scored at Home")
    # plot the away points data
    ax.plot(months, points_away, 'ro-', label="Points Scored Away")
    ax.legend()
    ax.set(xlabel='Month', ylabel='Number of Points', title='{} avg Number of Points Scored per Month- Home vs. Away'.format(team))
    ax.grid()
    fig.savefig('scored.png')
    plt.show()

def main():
    #----------------------------------
    #   index      team
    #----------------------------------
    #   1	    Atlanta Hawks
    #   2	    Boston Celtics
    #   3	    Brooklyn Nets
    #   4	    Charlotte Hornets
    #   5	    Chicago Bulls
    #   6	    Cleveland Cavaliers
    #   7	    Dallas Mavericks
    #   8	    Denver Nuggets
    #   9	    Detroit Pistons
    #   10	    Golden State Warriors
    #   11	    Houston Rockets
    #   12	    Indiana Pacers
    #   13	    LA Clippers
    #   14	    Los Angeles Lakers
    #   15	    Memphis Grizzlies
    #   16	    Miami Heat
    #   17	    Milwaukee Bucks
    #   18	    Minnesota Timberwolves
    #   19	    New Orleans Pelicans
    #   20	    New York Knicks
    #   21	    Oklahoma City Thunder
    #   22	    Orlando Magic
    #   23	    Philadelphia 76ers
    #   24	    Phoenix Suns
    #   25	    Portland Trail Blazers
    #   26	    Sacramento Kings
    #   27	    San Antonio Spurs
    #   28	    Toronto Raptors
    #   29	    Utah Jazz
    #   30	    Washington Wizards
    # ----------------------------  

    # Choose what team and season you are interested in viewing
    # Then, run code at least 6 times to get full data

    year1 = 2018
    year2 = 2019
    team = 1

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
    data = get_scored(year1, year2, team, page)
    setup_points_table(data, cur, conn)
    avg = avg_points_scored(cur,conn)
    viz_one(avg)

    
    
if __name__ == "__main__":
    main()