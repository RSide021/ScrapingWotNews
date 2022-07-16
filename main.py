import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

url_source = "https://wotexpress.info/news/world-of-tanks/"


def load_all_news_from_page():
    soup = get_soup()
    all_cards_news = soup.find_all("a", class_="news-block-row")

    news_dict = {}
    for card in all_cards_news:
        key_for_dict = get_key_for_dict(card)
        news_dict[key_for_dict] = create_new_element_news_dict(card)

    write_news_dict_to_file(news_dict)


def check_news_update():
    with open("news_dict.json", encoding="utf-8") as file:
        news_dict = json.load(file)

    soup = get_soup()

    all_cards_news = soup.find_all("a", class_="news-block-row")

    fresh_news_dict = {}
    for card in all_cards_news:
        key_for_dict = get_key_for_dict(card)

        if key_for_dict in news_dict:
            continue
        else:
            news_dict[key_for_dict] = create_new_element_news_dict(card)
            fresh_news_dict[key_for_dict] = create_new_element_news_dict(card)

    write_news_dict_to_file(news_dict)

    return fresh_news_dict


def get_soup(url=url_source):
    response = requests.get(url=url, headers=get_headers())
    return BeautifulSoup(response.text, "lxml")


def get_headers():
    ua = UserAgent()
    return {
        "user-agent": ua.random
    }


def get_key_for_dict(card):
    card_href = card.get("href")
    sub_card_href = card_href[:-1]
    return sub_card_href.split("/")[-1]


def create_new_element_news_dict(card):
    card_href = card.get("href")
    card_title = card.find("div", class_="news-block-text").find_next().text
    card_desc = card.find("div", class_="news_anons").find_next().text
    card_date = card.find("div", class_="news_date").text
    return {
        "card_title": card_title,
        "card_desc": card_desc,
        "card_date": card_date,
        "card_href": card_href
    }


def write_news_dict_to_file(news_dict):
    with open("news_dict.json", "w", encoding="utf-8") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

