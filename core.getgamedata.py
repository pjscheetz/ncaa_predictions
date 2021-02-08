
import json
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
#import mechanicalsoup
import requests
import datetime
from datetime import timedelta
import time
import numpy as np

def get_game_history(year):
    url="http://barttorvik.com/getgamestats.php?sIndex=7&year="+year+"&tvalue=All&cvalue=All&opcvalue=All&ovalue=All&minwin=All&mindate=&maxdate=&typev=All&venvalue=All&minadjo=0&minadjd=200&mintempo=0&minppp=0&minefg=0&mintov=200&minreb=0&minftr=0&minpppd=200&minefgd=200&mintovd=0&minrebd=200&minftrd=200&mings=0&mingscript=-100&maxx=100&coach=All&opcoach=All&adjoSelect=min&adjdSelect=max&tempoSelect=min&pppSelect=min&efgSelect=min&tovSelect=max&rebSelect=min&ftrSelect=min&pppdSelect=max&efgdSelect=max&tovdSelect=min&rebdSelect=max&ftrdSelect=max&gscriptSelect=min&sortToggle=1"
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.text))
    #print(df)
    return df
#print(r.json())

def get_talent():
    url="https://barttorvik.com/effective_talent.json"
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.text))
    #print(df)
    return df

def getavgheight():
    url="https://barttorvik.com/all_avg_ht.json"
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.text))
    #print(df)
    return df

def get_eff_height():
    url="https://barttorvik.com/all_eff_ht.json"
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.text))
    #print(df)
    return df

def get_exp():
    url="https://barttorvik.com/exp_history.json"
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.text))
    #print(df)
    return df

def rowgetDataText(tr, coltag='td'):  # td (data) or th (header)
    #tr.span.decompose()
    #return [element for element in tr.find_all('td') if isinstance(element, NavigableString)]
    data=[]
    for td in tr.find_all(coltag):
        #td.find_all(text=True, recursive=False).strip()
        data.append(td.find(text=True))
    return data
    #return [td.get_text(strip=True) for td in tr.find_all(coltag)]


def get_historic_trank(date,year):
    url="http://barttorvik.com/trank-time-machine.php?date="+date+"&year="+year
    r = requests.get(url)
    soup = BeautifulSoup(r.text,features="lxml")
    table = soup.find("table")
    trs = table.find_all('tr')
    trs = trs[1:]
    #print(table)
    rows = []
    for tr in trs:  # for every table row
        rows.append(rowgetDataText(tr, 'td'))  # data row

    dftable = pd.DataFrame(rows)
    return dftable

def get_full_year_trank(year,begin,end):
    #currentdate = datetime.datetime(2020, 11, 4)
    enddate= datetime.datetime(2021, 1, 8)
    i=1
    hist_data=get_historic_trank(begin.strftime("%Y%m%d"),year)
    hist_data['date']=begin.strftime("%Y%m%d")
    currentdate = begin + timedelta(days=i)

    while currentdate<=end:
        print(currentdate.strftime("%Y%m%d"))
        temp=get_historic_trank(currentdate.strftime("%Y%m%d"),year)
        temp['date'] = currentdate.strftime("%Y%m%d")
        hist_data=hist_data.append(temp)
        currentdate = currentdate + timedelta(days=i)
    return hist_data

def get_historic_team_data(begin, end ,year,team_list):

    start_date=begin.strftime("%Y%m%d")
    end_date = end.strftime("%Y%m%d")
    url="https://barttorvik.com/trank.php?year="+year+"&begin="+start_date+"&end="+end_date
    r = requests.get(url)
    soup = BeautifulSoup(r.text,features="lxml")
    soup.span.decompose()
    table = soup.find("table")
    trs = table.find_all('tr')
    trs = trs[1:]
    # #print(table)
    rows = []
    for tr in trs:  # for every table row
        data = []
        rows.append(rowgetDataText(tr))
    dftable = pd.DataFrame(rows)
    columns = ['Rank', 'team', 'Conference', 'Games Played', 'Record', 'AdjOE', 'AdjDE', 'TRank', 'EFG%',
               'EFGD%', 'TOR', 'TORD',
               'ORB', 'DRB', 'FTR', 'FTRD', '2P%', '2P%D', '3P%', '3P%D', 'AdjT', 'WAB']
    if dftable.size>0:
        dftable = dftable[pd.notna(dftable[1])]
        dftable.columns = columns
    else:
        dftable = pd.DataFrame(columns=columns)
    dftable=pd.merge(dftable, team_list, how='right', left_on='team', right_on='Team')
    dftable=dftable.drop(['team'], axis=1)
    dftable['start_date'] = start_date
    dftable['end_date']=end_date

    return dftable

def get_full_year_historic_team_data(begin, end ,year):
    team_list=get_full_team_list(year)
    i = 1
    hist_data = get_historic_team_data(begin=begin,end=begin, year=year,team_list=team_list)
    currentdate = begin + timedelta(days=i)

    while currentdate <= end:
        #time.sleep(15)
        print(currentdate.strftime("%Y%m%d"))
        temp = get_historic_team_data(begin=begin,end=currentdate, year=year,team_list=team_list)
        hist_data = hist_data.append(temp)
        currentdate = currentdate + timedelta(days=i)
    return hist_data

def get_full_team_list(year):
    url="https://barttorvik.com/effective_talent.json"
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.text))
    #print(df)
    team_list=df[year]
    team_list=pd.DataFrame({'Team':team_list[pd.notna(team_list)].index})
    #team_list.reset_index(level=0, inplace=True)
    #team_list['team']=team_list.index

    return team_list
get_game_history("2020").to_csv('2021_rank_data.csv')
#getTeamTableData("20201201","20201202","2021").to_csv('testTeamTable.csv')
#getYearTData("2021").to_csv('2021_rank_data.csv')
#hist_data.to_csv('2019_rank_data.csv') r
#team_list=get_full_team_list("2021")
#print(team_list)

#start= datetime.datetime(2015, 11, 1)
#end= datetime.datetime(2016, 4, 7)
# #end= datetime.datetime(2016, 11, 12)
#get_full_year_historic_team_data(begin=start,end=end,year="2015").to_csv("team_stats_2015.csv")
#print(get_historic_team_data(begin=start,end=end,year="2021",team_list=team_list))
#get_historic_team_data(begin=start,end=end,year="2021").to_csv("test_team_data.csv")
#print(get_full_team_list("2021"))
#get_talent().to_csv("team_talent.csv")
#getavgheight().to_csv("team_avg_height.csv")
#get_eff_height().to_csv("team_eff_height.csv")
#get_exp().to_csv("team_exp.csv")