#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 15:49:00 2024

@author: nick
"""

import requests
import json
import csv
import time
import pandas as pd
from plotnine import ggplot, aes, geom_bar, labs, theme_minimal, theme, element_text

def filter_card(scryfall_card):
    card = {
        "name": scryfall_card["name"],
        "type_line": scryfall_card["type_line"],
        # "color_identity": scryfall_card["color_identity"],
    }

    if "mana_cost" in scryfall_card:
        card["mana_cost"] = scryfall_card["mana_cost"]
    # else:
    #    card["mana_cost"] = None

    if "oracle_text" in scryfall_card:
        card["oracle_text"] = scryfall_card["oracle_text"]
    # else:
    #    card["oracle_text"] = None

    return card


def save_json(cards, filename):
    with open(filename, "w") as file:
        json.dump(cards, file, indent=2)


def save_csv(cards_json):
    headers = ["name", "type_line", "mana_cost", "oracle_text"]

    with open("output.csv", "w", newline="\n") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for card in cards_json:
            writer.writerow(card)


def download_all_standard_cards():
    standard_cards = []
    url = "https://api.scryfall.com/cards/search"
    params = {
        "q": "(game:paper) legal:standard",
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:

        data = response.json()
        has_more = data['has_more']
        cards = data['data']
        standard_cards.extend(cards)
        time.sleep(0.1)

        while has_more:
            print(data['next_page'])
            next_response = requests.get(data['next_page'])
            if next_response.status_code == 200:
                data = next_response.json()
                has_more = data['has_more']
                cards = data['data']
                standard_cards.extend(cards)
            else:
                print("Error paging")
                has_more = False
            time.sleep(0.1)

    else:
        print("Request failed with status code:", response.status_code)
    return standard_cards


def search_cards(query):
    returned_cards = []
    url = "https://api.scryfall.com/cards/search"
    params = {
        "q": query,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:

        data = response.json()
        has_more = data['has_more']
        cards = data['data']
        returned_cards.extend(cards)
        time.sleep(0.1)

        while has_more:
            print(data['next_page'])
            next_response = requests.get(data['next_page'])
            if next_response.status_code == 200:
                data = next_response.json()
                has_more = data['has_more']
                cards = data['data']
                returned_cards.extend(cards)
            else:
                print("Error paging")
                has_more = False
            time.sleep(0.1)

    else:
        print("Request failed with status code:", response.status_code)
    return returned_cards


def filter_cards(cards):
    filtered_cards = []
    for card in cards:
        filtered_cards.append(filter_card(card))
    return filtered_cards


def get_first_half(arr):
    mid = len(arr) // 2
    return arr[:mid]


# electronic counter

def find_cards_standard_counter_oracle():
    return search_cards("oracle:counter (game:paper) legal:standard")

def find_cards_modern_counter_oracle():
    return search_cards("oracle:counter (game:paper) legal:modern")

def find_preceding_words(text):
    words = text.split()
    preceding_words = []

    for i in range(1, len(words)):
        if "counter" in words[i].lower():
            preceding_word = words[i - 1]
            preceding_words.append(preceding_word)
            print("match: " + words[i].lower())
            print("previous: " + preceding_word)

    return preceding_words


def extract_counters(cards):
    counter_types = []
    for card in cards:
        if "oracle_text" in card:
            print(card["oracle_text"])
            counter_types.extend(find_preceding_words(card["oracle_text"]))
            print('\n')

    return counter_types


def filter_counters(arr):
    filtered_strings = [x for x in arr if not (
            x.endswith('.') or x.endswith(')') or x.endswith(',') or x.endswith(':') or x.endswith(
        '—') or x.endswith('each') or x.endswith('Then') or x.endswith('a') or x.endswith('of') or x.endswith(
        'another') or x.endswith('additional') or x.endswith('•') or x.endswith('be') or x.endswith('is')
            or x.endswith('more') or x.endswith('and') or x.endswith('its') or x.endswith('three')
    or x.endswith('those') or x.endswith('had') or x.endswith('with') or x.endswith('five') or x.endswith('X'))]
    return filtered_strings

def plot_with_plotnine(counters):
    # Create a DataFrame from the array
    df = pd.DataFrame(counters, columns=['Counter'])

    # Create the bar plot using plotnine
    plot = (
            ggplot(df, aes(x='Counter')) +
            geom_bar() +
            labs(
                title='Standard Format Counter Frequency',
                x='Counter',
                y='Occurrences'
            )+ theme(axis_text_x=element_text(angle=-45, hjust=0))
    )

    # Show the plot
    plot.show()

def get_collapsed_dataframe(counters):
    df = pd.DataFrame(counters, columns=['Counter'])

    # Count occurrences of each counter and sort by occurrences in descending order
    df_counts = df['Counter'].value_counts().reset_index()
    df_counts.columns = ['Counter', 'Occurrences']
    df_counts = df_counts.sort_values(by='Occurrences', ascending=False)
    df_counts['Counter'] = pd.Categorical(df_counts['Counter'], categories=df_counts['Counter'], ordered=True)

    return df_counts


def plot_with_plotnine_sorted(counters, title):
    # Create a DataFrame from the array
    df = pd.DataFrame(counters, columns=['Counter'])

    # Count occurrences of each counter and sort by occurrences in descending order
    df_counts = df['Counter'].value_counts().reset_index()
    df_counts.columns = ['Counter', 'Occurrences']
    df_counts = df_counts.sort_values(by='Occurrences', ascending=False)
    df_counts['Counter'] = pd.Categorical(df_counts['Counter'], categories=df_counts['Counter'], ordered=True)

    # Create the bar plot using plotnine
    plot = (
        ggplot(df_counts, aes(x='Counter', y='Occurrences')) +
        geom_bar(stat='identity') +
        labs(
            title=title,
            x='Counter Type',
            y='Number of References'
        ) +
        theme(axis_text_x=element_text(angle=-45, hjust=0))
    )

    # Show the plot
    plot.show()
    plot.save(filename='counters.svg', format='svg', width=12, height=8, units='in')

