#!/usr/bin/python
# coding=utf-8
from flask import Flask
from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep
import json, datetime, os

from flask_slackbot import SlackBot

BASE_URL = 'http://fjolsmidjan.is/fjolsmidjan_matsedill_vikunnar'

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")

def get_menu(url):
    soup = make_soup(url)
    menu = []
    n = 0
    for i in soup.findAll("p", {"class":"rtecenter"}):
      if n == 0:
        menu.append({"week":i.find("span").get_text()})
        menu.append({i.findAll("strong")[1].get_text():[i.get_text().split("\n")[1], i.get_text().split("\n")[2]]})
      if n > 0 and n <=4:
        menu.append({i.get_text().split("\n")[0]:[i.get_text().split("\n")[1],i.get_text().split("\n")[2]]})
      # if n <= 4 and not 0:
      #   menu.append()
      #   print str(n) + i.get_text()
      n += 1
    return menu

@app.route("/today")
def today():
    menu = get_menu(BASE_URL)
    day = datetime.datetime.today().weekday() + 1
    if day < 6:
        item = menu[day]
    else:
        item = "Ekkert í dag"
    return json.dumps(item, sort_keys=True, indent=4)

@app.route("/week")
def week():
    menu = get_menu(BASE_URL)
    return json.dumps(menu, sort_keys=True, indent=4)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)