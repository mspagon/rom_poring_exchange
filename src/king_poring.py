from card_rates import *

from datetime import datetime

import json
import os
import requests

cached_prices = 'cache/card_prices.txt'


def get_card_prices():
    """
    Run once a day.
    """
    cards = {}

    # Cards are type 21 through 27
    card_range = [x for x in range(21, 28)]

    for card_num in card_range:
        url = "https://www.romexchange.com/api?type={}".format(card_num)

        page = 1
        while True:
            print('making request:', url + '&page=' + str(page))
            r = requests.get(url + '&page=' + str(page))

            results = r.json()

            if not results:
                break

            for card in results:
                card_data = dict(card)
                name = card_data['name']
                price = card_data['global']['latest']
                cards[name] = price

            page += 1

    with open(cached_prices, 'w+') as fp:
        fp.write(json.dumps(cards, indent=2))


def find_avg(prices):
    prices = [x[1] for x in prices]
    return sum(prices) / len(prices)


def analyze():
    # Load Price Data
    with open(cached_prices, 'r') as fp:
        data = fp.read()

    prices = json.loads(data)

    gray_prices = []
    green_prices = []
    blue_prices = []

    for card in gray:
        gray_prices.append((card, prices[card]))

    for card in green:
        green_prices.append((card, prices[card]))

    for card in blue:
        blue_prices.append((card, prices[card]))

    gray_prices.sort(key=lambda x: x[1])
    green_prices.sort(key=lambda x: x[1])
    blue_prices.sort(key=lambda x: x[1])

    gray_lowest = gray_prices[0][1]
    green_lowest = green_prices[0][1]
    blue_lowest = blue_prices[0][1]

    gray_avg = find_avg(gray_prices)
    green_avg = find_avg(green_prices)
    blue_avg = find_avg(blue_prices)

    for row in king_poring_rates:
        cost = 0

        # Calculate Cost
        for letter in list(row['Input Colors']):
            if letter == 'W':
                cost += gray_lowest
            elif letter == 'G':
                cost += green_lowest
            elif letter == 'B':
                cost += blue_lowest

        row['Cost'] = cost

        # Calculate Expected
        expected_value = (
                (row['White Chance'] * gray_avg) +
                (row['Green Chance'] * green_avg) +
                (row['Blue Chance'] * blue_avg)
        )

        row['Expected Value'] = expected_value

        row['Profit'] = expected_value - cost

    def write_output():
        date = str(datetime.now().date())

        output = os.path.join('output/', date + '.txt')

        with open(output, 'w+') as fp:
            # columns
            fp.write(
                '{code:<8} {input_colors:<14} {white_chance:<15} '
                '{green_chance:<15} {blue_chance:<15} {cost:<16} '
                '{ev:<16} {profit:<16}\n'.format(
                    code='Code',
                    input_colors='Input Colors',
                    white_chance='White Chance',
                    green_chance='Green Chance',
                    blue_chance='Blue Chance',
                    cost='Cost',
                    ev='Expected Value',
                    profit='Profit'))

            # rows
            for r in king_poring_rates:
                fp.write(
                    '{code:<8} {input_colors:<14} {white_chance:<15.1%} '
                    '{green_chance:<15.1%} {blue_chance:<15.1%} {cost:<16,.2f} '
                    '{ev:<16,.2f} {profit:<16,.2f}\n'.format(
                        code=r['Code'],
                        input_colors=r['Input Colors'],
                        white_chance=r['White Chance'],
                        green_chance=r['Green Chance'],
                        blue_chance=r['Blue Chance'],
                        cost=r['Cost'],
                        ev=r['Expected Value'],
                        profit=r['Profit']
                    ))

            # Cheapest Cards
            fp.write('\n')
            fp.write('Gray Lowest: {} = ${:,}\n'.format(gray_prices[0][0], gray_prices[0][1]))
            fp.write('Green Lowest: {} = ${:,}\n'.format(green_prices[0][0], green_prices[0][1]))
            fp.write('Blue Lowest: {} = ${:,}\n'.format(blue_prices[0][0], blue_prices[0][1]))

            # All Cards
            fp.write('\n')
            fp.write('GRAY CARDS\n')
            fp.write('-' * 20 + '\n')
            for card in gray_prices:
                fp.write('{:} {:<15,.2f}\n'.format(card[0], card[1]))

            fp.write('\n')
            fp.write('GREEN CARDS\n')
            fp.write('-' * 20 + '\n')
            for card in green_prices:
                fp.write('{:} {:<15,.2f}\n'.format(card[0], card[1]))

            fp.write('\n')
            fp.write('BLUE CARDS\n')
            fp.write('-' * 20 + '\n')
            for card in blue_prices:
                fp.write('{:} {:<15,.2f}\n'.format(card[0], card[1]))

            fp.write('\n')

    write_output()


get_card_prices()
analyze()
