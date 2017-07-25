import json
import requests
import time
import urllib
import config
from bs4 import BeautifulSoup
import html5lib
from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dbhelperow import DBHelper

db = DBHelper()

TOKEN = config.ow_bot_token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

source = urllib.request.urlopen('https://playoverwatch.com/en-us/blog/').read()
soup = BeautifulSoup(source, 'html5lib')
latest_article = soup.find(class_='link-title')

def get_url(url):
    # Downloads content from URL and returns as a string
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    # Uses string response from get_url and parses into Python Dict
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    # Bot API to retrieve list of updates from Telegram
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

# def get_last_chat_id_and_text(updates):
#     # Inelegant solution to get chat_id and message text of most recent message sent
#     num_updates = len(updates["result"])
#     last_update = num_updates - 1
#     text = updates["result"][last_update]["message"]["text"]
#     chat_id = updates["result"][last_update]["message"]["chat"]["id"]
#     return (text, chat_id)

def send_message(text, chat_id):
    # Sends message to chat_id using Bot API
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?chat_id={}&text={}".format(chat_id, text)
    get_url(url)

def send_news(text, link, chat_id):
    # Sends a new blog post with link using Markdown
    text = urllib.parse.quote(text)
    text = '[' + text + '](https://playoverwatch.com' + link + ')'
    url = URL + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(chat_id, text)
    get_url(url)

def new_article_check(latest_article):
    print("Checking for new article")
    check_source = urllib.request.urlopen('https://playoverwatch.com/en-us/blog/').read()
    check_soup = BeautifulSoup(check_source, 'html5lib')
    check_article = check_soup.find(class_='link-title')
    if latest_article != check_article:
        print("New Article Found")
        new_title = check_article['title']
        new_link = check_article['href']
        subscribers = db.get_items()
        for sub in subscribers:
            send_news(new_title, new_link, sub)
        latest_article = check_article
    else:
        print("No New Article")

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            text = text.partition(" ")[0]
            print(text)
            all_chats = db.get_items()
            if text == "/subscribe":
                if chat in all_chats:
                    send_message("You are already subscribed!", chat)
                else:
                    db.add_item(chat)
                    send_message("You are now subscribed to Overwatch News!", chat)
            elif text == "/unsubscribe":
                if chat in all_chats:
                    db.delete_item(chat)
                    send_message("You are now unsubscribed from Overwatch News!", chat)
                else:
                    send_message("You aren't subscribed, send /subscribe first!")
        except KeyError:
            pass

def main():
    db.setup()
    last_update_id = None
    new_article_check(latest_article)
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: new_article_check(latest_article), 'interval', seconds=3600)
    scheduler.start()
    while True:
        print ("Getting updates...")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
