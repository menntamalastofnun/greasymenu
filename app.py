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

class GreasyWeek:
    """Object that represents the weeks menu"""
    def __init__(self):
        self.week = None
        self.items = []

    def set_week(self, week):
        self.week = week

    def add_item(self, item):
        self.items.append(item)

    def serialize(self):
        """Format object as json"""
        itemlist = []
        for i in self.items:
            itemlist.append({
                'soup': i.soup,
                'main': i.main,
                'day': i.day
                })
        return json.dumps({
            'items': itemlist,
            'week': self.week},
            indent=4)

    def print_menu(self):
        """Useful print function for the week menu"""
        print("%s" % self.week)
        for i in self.items:
            print(" %s\n  %s\n  %s" % (i.day, i.main, i.soup))

class GreasyMenu:
    """Object for the days menu"""
    def __init__(self, day="Enginn", main="Ekkert", soup="Engin"):
        self.day = day
        self.main = main
        self.soup = soup

    def serialize(self):
        """Format object as json"""
        return json.dumps({
            'soup': self.soup,
            'main': self.main,
            'day': self.day
        }, indent=4)

def make_soup(url):
    """Get page and save the soup"""
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")

def get_menu(url):
    """Scrape the menu page"""
    soup = make_soup(url)
    menu = GreasyWeek()
    n = 0
    for i in soup.findAll("p", {"class":"rtecenter"}):
      if n == 0:
        menu.set_week(i.find("span").get_text())
        item = GreasyMenu(i.findAll("strong")[1].get_text(), i.get_text().split("\n")[1], i.get_text().split("\n")[2])
        menu.add_item(item)
      elif n > 0 and n < 5:
        item = GreasyMenu(i.findAll("strong")[0].get_text(), i.get_text().split("\n")[1], i.get_text().split("\n")[2])
        menu.add_item(item)
      elif n >= 5:
        break
      n += 1
    #menu.print_menu()
    return menu

@app.route("/today")
def today():
    """The menu items of the day"""
    menu = get_menu(BASE_URL)
    day = datetime.datetime.today().weekday()
    if day < 5:
        item = menu.items[day]
    else:
        item = "Ekkert í dag"
    return item.serialize()

@app.route("/week")
def week():
    """The menu of the week"""
    return get_menu(BASE_URL).serialize()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)