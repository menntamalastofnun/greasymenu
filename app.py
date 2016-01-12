#!/usr/bin/python
# coding=utf-8
from flask import Flask, jsonify
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
        return jsonify({
            'items': itemlist,
            'week': self.week
        })

    def slackize(self):
        """Format object as json"""
        itemlist = ""
        for i in self.items:
            itemlist += "  %s:\n    %s\n    %s\n" % (i.day, i.main, i.soup)

        return slack_response(self.week, itemlist)

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

    def slackize(self):
        text = "%s\n  %s" % (self.main, self.soup)
        return slack_response(self.day, text)

    def serialize(self):
        """Format object as json"""
        return jsonify({
            'soup': self.soup,
            'main': self.main,
            'day': self.day
        })

def slack_response(title, text):
    return jsonify({
         "response_type": "in_channel",
         "attachments": [
             {
                 "title": title,
                 "text": text,
             }
         ]
    })

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
    return menu

def get_menu_item(day):
    menu = get_menu(BASE_URL)
    if day < 5:
        return menu.items[day]
    else:
        return GreasyMenu()

@app.route("/today")
def today():
    """The menu items of the day"""
    day = datetime.datetime.today().weekday()
    return get_menu_item(day).serialize()

@app.route("/tomorrow")
def tomorrow():
    """The menu items of tomorrow"""
    day = datetime.datetime.today().weekday() + 1
    return get_menu_item(day).serialize()

@app.route("/week")
def week():
    """The menu of the week"""
    return get_menu(BASE_URL).serialize()

@app.route("/slack/today")
def slToday():
    """The menu items of the day"""
    day = datetime.datetime.today().weekday()
    return get_menu_item(day).slackize()

@app.route("/slack/tomorrow")
def slTomorrow():
    """The menu items of the day"""
    day = datetime.datetime.today().weekday() + 1
    return get_menu_item(day).slackize()

@app.route("/slack/week")
def slWeek():
    """The menu of the week"""
    return get_menu(BASE_URL).slackize()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)