# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 20:43:58 2022

@author: swuma
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Loop through 2 Epl seasons
# For each season:
    #get starting url and request the page
    #create an empty list for storing final tables
    #get the standing table 
    #get all the club links 
    #loop through all the links
    #For each link:
        #visit the link page
        #get the fixtures table and convert to dataframe
        #get the shooting link
        #visit the shooting page
        #get the shooting table and convert to dataframe
        #merge shooting table with fixtures table
        #add club and year columns to the merged table and populate with data
        #append merged table to a list
        
    #update url with previous season url
seasons =  ["2021-2022", "2020-2021"]
all_tables = []

for season in seasons:
    standing_url = "https://fbref.com/en/comps/9/2021-2022/2021-2022-Premier-League-Stats"
    page = requests.get(standing_url)
    soup = BeautifulSoup(page.text, "lxml")
    
    previous_season = soup.find_all("div", class_="prevnext")[0]
    previous_season_link = previous_season.find_all("a")[0].get("href")
    previous_season_url = f"https://fbref.com{previous_season_link}"
    
    standing_table = soup.find_all("table", class_="stats_table")[0]
    
    links = standing_table.find_all("a")
    links = [link.get("href") for link in links]
    squad_links = [link for link in links if "squads" in link]
    squad_urls = [f"https://fbref.com{link}" for link in squad_links]
    
    for squad_url in squad_urls:
        club_stat_page = requests.get(squad_url).text
        club_stat_soup = BeautifulSoup(club_stat_page, "lxml")
        
        name = squad_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
    
        fixture_table = pd.read_html(club_stat_page, match="Scores & Fixtures")[0]
        
        match_log_types = club_stat_soup.find_all("div", class_="filter")[2]
        shooting = match_log_types.find_all("a")[1]
        shooting_link = shooting.get("href")
        shooting_url = f"https://fbref.com{shooting_link}"
        shooting_page = requests.get(shooting_url).text
        shooting_table = pd.read_html(shooting_page)[0]
        shooting_table.columns = shooting_table.columns.droplevel()
        
        merge_table = fixture_table.merge(shooting_table[["Date", "Gls", "Sh", "SoT", "SoT%", "G/Sh", "FK", "PK", "PKatt" ]], on="Date")
        merge_table = merge_table[merge_table["Comp"] == "Premier League"]
        merge_table["Club"] = name
        merge_table["Season"] = season 

        all_tables.append(merge_table) 

        time.sleep(1)
        
    standing_url = previous_season_url
    
final_df = pd.concat(all_tables)
final_df.to_csv("C:/Users/swuma/scrapping/epl.csv")
final_df.to_excel("C:/Users/swuma/scrapping/epl.xlsx")