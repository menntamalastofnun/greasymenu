#!/usr/bin/python
# coding=utf-8

from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep
import json

BASE_URL = 'http://fjolsmidjan.is/fjolsmidjan_matsedill_vikunnar'

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

if __name__ == '__main__':
    menu = get_menu(BASE_URL)
    f = open('lunch.json', 'w')
    # Let's make this json pretty
    f.write(json.dumps(menu, sort_keys=True, indent=4))
    f.close