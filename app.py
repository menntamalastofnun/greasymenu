#!/usr/bin/python
# coding=utf-8
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep
from datetime import date, timedelta
import json, datetime, os, re

from flask_slackbot import SlackBot

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


class GreasyMenu:
    """Object for the days menu"""
    def __init__(self, day="Enginn", main="Ekkert", soup="Engin"):
        self.day = day
        self.main = main
        self.soup = soup

    def slackize(self):
        """Make menu ready for posting on slack"""
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
    """Makes Slack-ready jsonified response"""
    return jsonify({
         "response_type": "in_channel",
         "attachments": [
             {
                 "title": title,
                 "text": text,
             }
         ]
    })

def make_soup():
    """Get page and return beautiful soup"""
    html = urlopen('http://fjolsmidjan.is/fjolsmidjan_matsedill_vikunnar').read()
    return BeautifulSoup(html, "lxml")

def get_menu():
    """Scrape the menu page"""
    months = [u'',u'Janúar',u'Febrúar',u'Mars',u'Apríl',u'Maí',u'Júní',u'Júlí',u'Ágúst',u'September',u'Október',u'Nóvember',u'Desember']
    soup = make_soup()
    menu = GreasyWeek()
    weekday = datetime.datetime.today().weekday()
    firstday = datetime.datetime.today().date() - timedelta(days=weekday)
    lastday = firstday + timedelta(days=4)
    menu.set_week("Vikan %s. - %s. %s" % (str(firstday.day), str(lastday.day), months[datetime.datetime.today().month]))
    for i in soup.findAll(text=re.compile(ur'.*(M\xe1nu|\xderi\xf0ju|Mi\xf0viku|Fimmtu|F\xf6stu)dagur.*', re.UNICODE)):
        day = i.parent.get_text().strip()
        main = i.parent.nextSibling.nextSibling
        soup = main.nextSibling.nextSibling
        item = GreasyMenu(day, main.strip(), soup.strip())
        menu.add_item(item)
    return menu

def get_menu_item(day):
    """Gets menu item for selected day"""
    menu = get_menu()
    if day < 5:
        return menu.items[day]
    else:
        return GreasyMenu()

@app.route("/today")
def today():
    """The menu items of the day"""
    day = date.today().weekday()
    return get_menu_item(day).serialize()

@app.route("/tomorrow")
def tomorrow():
    """The menu items of tomorrow"""
    day = date.today().weekday() + 1
    return get_menu_item(day).serialize()

@app.route("/week")
def week():
    """The menu of the week"""
    return get_menu().serialize()

@app.route("/slack/today", methods=["POST"])
def slToday():
    """The menu items of the day for Slack"""
    day = date.today().weekday()
    return get_menu_item(day).slackize()

@app.route("/slack/tomorrow", methods=["POST"])
def slTomorrow():
    """The menu items of the day for Slack"""
    day = date.today().weekday() + 1
    return get_menu_item(day).slackize()

@app.route("/slack/week", methods=["POST"])
def slWeek():
    """The menu of the week for Slack"""
    return get_menu().slackize()

@app.route("/slack/help", methods=["POST"])
def slHelp():
    """"Sends available commands"""
    text = "Hvað er í matinn?\nHvað er í matinn á morgun?\nMatseðill vikunnar?"
    return slack_response("Skipanir", text)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
