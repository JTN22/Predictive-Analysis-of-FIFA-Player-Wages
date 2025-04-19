import random
import time

import cloudscraper
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

players = pd.read_csv("players.csv")
print(players.head())

# Turn incorrect format into correct format
# https://www.fifaindex.com/players//player/239085/erling-haaland/ -> https://www.fifaindex.com/player/239085/erling-haaland/

# players["url"] = players["url"].str.replace("players//player/", "player/")
# players.to_csv("players.csv", index=False)

# print(players.head())
print(players.iloc[0, 1])


# Bypass Cloudflare's anti-bot protection
def get_scraper():
    """Create a cloudscraper instance"""
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}, delay=10
    )


# HAHAHAHAHAHAHA FU CLOUDFLARE
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.fifaindex.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


def get_page(url, scraper, retry_count=3):
    """Get a page with retries"""
    for attempt in range(retry_count):
        try:
            response = scraper.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retry_count - 1:
                raise
            time.sleep(random.uniform(1, 3))


def count_star(star_element):
    """FIFA presents some ratings with stars (maximum 5)/ This function counts the number of stars"""

    stars = star_element.find_all("i", {"class": "fas fa-star fa-lg"})
    count = len(stars)

    return count


def get_overall_stats(page, debug=True):
    try:
        cards = page.find_all("div", {"class": "col-sm-6"})
        main_card = cards[1]
        ostat_card = main_card.find("h5", {"class": "card-header"})

        ostat = ostat_card.find_all("span")

        assert len(ostat) >= 2

        overall_score = ostat[1].text
        position_score = ostat[2].text
        if debug:
            print(f"Overall score: {overall_score}")
            print(f"Position score: {position_score}")

    except Exception as e:
        print(f"Error: {e}")
        return {"overall_score": None, "position_score": None}

    return {"overall_score": overall_score, "position_score": position_score}


def get_main_card(page, debug=True):
    try:
        cards = page.find_all("div", {"class": "col-sm-6"})
        main_card = cards[1]

        stats = main_card.find_all("p", {"class": ""})

        height = stats[0].find("span", {"class": "data-units data-units-metric"}).text

        weight = stats[1].find("span", {"class": "data-units data-units-metric"}).text

        pref_foot = stats[2].find("span").text
        birthdate = stats[3].find("span").text
        age = stats[4].find("span").text
        pref_pos = stats[5].find("span").text
        work_rate = stats[6].find("span").text
        weak_foot = count_star(stats[7])
        skill_moves = count_star(stats[8])
        value_wage = main_card.find_all(
            "p", {"class": "data-currency data-currency-dollar"}
        )
        value = value_wage[0].find("span").text
        wage = value_wage[1].find("span").text

        if debug:
            print(f"Number of stats: {len(stats)}")
            print(f"Height: {height}")
            print(f"Weight: {weight}")
            print(f"Preferred foot: {pref_foot}")
            print(f"Age: {age}")
            print(f"Preferred position: {pref_pos}")
            print(f"Work rate: {work_rate}")
            print(f"Weak foot: {weak_foot}")
            print(f"Skill moves: {skill_moves}")
            print(f"Value: {value}")
            print(f"Wage: {wage}")
    except Exception as e:
        print(f"Error: {e}")
        return {
            "height": None,
            "weight": None,
            "pref_foot": None,
            "birthdate": None,
            "age": None,
            "pref_pos": None,
            "work_rate": None,
            "weak_foot": None,
            "skill_moves": None,
            "value": None,
            "wage": None,
        }

    return {
        "height": height,
        "weight": weight,
        "pref_foot": pref_foot,
        "birthdate": birthdate,
        "age": age,
        "pref_pos": pref_pos,
        "work_rate": work_rate,
        "weak_foot": weak_foot,
        "skill_moves": skill_moves,
        "value": value,
        "wage": wage,
    }


def get_team_data(page, debug=True):
    try:
        cards = page.find_all("div", {"class": "team"})
        print(f"Number of team: {len(cards)}")

        main_elems = cards[0].find("div", {"class": "card-body"}).find_all("p")
        print(f"Number of main_elem: {len(main_elems)}")

        joined_club = main_elems[2].find("span").text
        contract_expires = main_elems[3].find("span").text
    except Exception as e:
        print(f"Error: {e}")
        return {"joined_club": None, "contract_expires": None}

    if debug:
        print(f"Joined club: {joined_club}")
        print(f"Contract expires: {contract_expires}")

    return {"joined_club": joined_club, "contract_expires": contract_expires}


def get_misc_ratings(page, debug=True):
    rating_categories = {
        "Ball Skills": ["Ball Control", "Dribbling"],
        "Defence": ["Marking", "Slide Tackle", "Stand Tackle"],
        "Mental": [
            "Aggression",
            "Reactions",
            "Att. Position",
            "Interceptions",
            "Vision",
            "Composure",
        ],
        "Passing": ["Crossing", "Short Pass", "Long Pass"],
        "Physical": [
            "Acceleration",
            "Stamina",
            "Strength",
            "Balance",
            "Sprint Speed",
            "Agility",
            "Jumping",
        ],
        "Shooting": [
            "Heading",
            "Shot Power",
            "Finishing",
            "Long Shots",
            "Curve",
            "FK Acc.",
            "Penalties",
            "Volleys",
        ],
        "Goalkeeper": [
            "GK Positioning",
            "GK Diving",
            "GK Handling",
            "GK Kicking",
            "GK Reflexes",
        ],
    }

    try:
        cards = page.find_all("div", {"class": "item"})

        # Get Ball Skills
        ball_skills = cards[0]
        assert ball_skills.find("h5").text == "Ball Skills", "Ball Skills not found"
        ball_control = ball_skills.find_all("p")[0].find("span").text
        dribbling = ball_skills.find_all("p")[1].find("span").text
        try:  # Some players have no dribbling
            ball_skill_avg = np.average([int(ball_control), int(dribbling)])
        except:
            ball_skill_avg = None

        # Get Defence
        defence = cards[1]
        assert defence.find("h5").text == "Defence", "Defence not found"
        marking = defence.find_all("p")[0].find("span").text
        slide_tackle = defence.find_all("p")[1].find("span").text
        stand_tackle = defence.find_all("p")[2].find("span").text
        try:
            defence_avg = np.average(
                [int(marking), int(slide_tackle), int(stand_tackle)]
            )
        except:
            defence_avg = None

        # Get Mental
        mental = cards[2]
        assert mental.find("h5").text == "Mental", "Mental not found"
        aggression = mental.find_all("p")[0].find("span").text
        reactions = mental.find_all("p")[1].find("span").text
        att_position = mental.find_all("p")[2].find("span").text
        interceptions = mental.find_all("p")[3].find("span").text
        vision = mental.find_all("p")[4].find("span").text
        composure = mental.find_all("p")[5].find("span").text
        try:
            mental_avg = np.average(
                [
                    int(aggression),
                    int(reactions),
                    int(att_position),
                    int(interceptions),
                    int(vision),
                    int(composure),
                ]
            )
        except:
            mental_avg = None

        # Get Passing
        passing = cards[3]
        assert passing.find("h5").text == "Passing", "Passing not found"
        crossing = passing.find_all("p")[0].find("span").text
        short_pass = passing.find_all("p")[1].find("span").text
        long_pass = passing.find_all("p")[2].find("span").text
        try:
            passing_avg = np.average([int(crossing), int(short_pass), int(long_pass)])
        except:
            passing_avg = None

        # Get Physical
        physical = cards[4]
        assert physical.find("h5").text == "Physical", "Physical not found"
        acceleration = physical.find_all("p")[0].find("span").text
        stamina = physical.find_all("p")[1].find("span").text
        strength = physical.find_all("p")[2].find("span").text
        balance = physical.find_all("p")[3].find("span").text
        sprint_speed = physical.find_all("p")[4].find("span").text
        agility = physical.find_all("p")[5].find("span").text
        jumping = physical.find_all("p")[6].find("span").text
        try:
            physical_avg = np.average(
                [
                    int(acceleration),
                    int(stamina),
                    int(strength),
                    int(balance),
                    int(sprint_speed),
                    int(agility),
                    int(jumping),
                ]
            )
        except:
            physical_avg = None

        # Get Shooting
        shooting = cards[5]
        assert shooting.find("h5").text == "Shooting", "Shooting not found"
        heading = shooting.find_all("p")[0].find("span").text
        shot_power = shooting.find_all("p")[1].find("span").text
        finishing = shooting.find_all("p")[2].find("span").text
        long_shots = shooting.find_all("p")[3].find("span").text
        curve = shooting.find_all("p")[4].find("span").text
        fk_acc = shooting.find_all("p")[5].find("span").text
        penalties = shooting.find_all("p")[6].find("span").text
        volleys = shooting.find_all("p")[7].find("span").text
        try:
            shooting_avg = np.average(
                [
                    int(heading),
                    int(shot_power),
                    int(finishing),
                    int(long_shots),
                    int(curve),
                    int(fk_acc),
                    int(penalties),
                    int(volleys),
                ]
            )
        except:
            shooting_avg = None

        # Get Goalkeeper
        goalkeeper = cards[6]
        assert goalkeeper.find("h5").text == "Goalkeeper", "Goalkeeper not found"
        gk_positioning = goalkeeper.find_all("p")[0].find("span").text
        gk_diving = goalkeeper.find_all("p")[1].find("span").text
        gk_handling = goalkeeper.find_all("p")[2].find("span").text
        gk_kicking = goalkeeper.find_all("p")[3].find("span").text
        gk_reflexes = goalkeeper.find_all("p")[4].find("span").text
        try:
            goalkeeper_avg = np.average(
                [
                    int(gk_positioning),
                    int(gk_diving),
                    int(gk_handling),
                    int(gk_kicking),
                    int(gk_reflexes),
                ]
            )
        except:
            goalkeeper_avg = None

        # Last card is traits. Purely textual so we skip it.
        if debug:
            print(f"Number of cards: {len(cards)}")
            print(f"Ball Control: {ball_control}")
            print(f"Dribbling: {dribbling}")
            print(f"Marking: {marking}")
            print(f"Slide Tackle: {slide_tackle}")
            print(f"Stand Tackle: {stand_tackle}")

    except Exception as e:
        print(f"Error: {e}")
        return {
            "Ball Control": None,
            "Dribbling": None,
            "Marking": None,
            "Slide Tackle": None,
            "Stand Tackle": None,
            "Aggression": None,
            "Reactions": None,
            "Att. Position": None,
            "Interceptions": None,
            "Vision": None,
            "Composure": None,
            "Crossing": None,
            "Short Pass": None,
            "Long Pass": None,
            "Acceleration": None,
            "Stamina": None,
            "Strength": None,
            "Balance": None,
            "Sprint Speed": None,
            "Agility": None,
            "Jumping": None,
            "Heading": None,
            "Shot Power": None,
            "Finishing": None,
            "Long Shots": None,
            "Curve": None,
            "FK Acc.": None,
            "Penalties": None,
            "Volleys": None,
            "GK Positioning": None,
            "GK Diving": None,
            "GK Handling": None,
            "GK Kicking": None,
            "GK Reflexes": None,
            "ball_skill_avg": None,
            "defence_avg": None,
            "mental_avg": None,
            "passing_avg": None,
            "physical_avg": None,
            "shooting_avg": None,
            "goalkeeper_avg": None,
        }

    return {
        # Get Ball Skills
        "Ball Control": ball_control,
        "Dribbling": dribbling,
        # Get Defence
        "Marking": marking,
        "Slide Tackle": slide_tackle,
        "Stand Tackle": stand_tackle,
        # Get Mental
        "Aggression": aggression,
        "Reactions": reactions,
        "Att. Position": att_position,
        "Interceptions": interceptions,
        "Vision": vision,
        "Composure": composure,
        # Get Passing
        "Crossing": crossing,
        "Short Pass": short_pass,
        "Long Pass": long_pass,
        # Get Physical
        "Acceleration": acceleration,
        "Stamina": stamina,
        "Strength": strength,
        "Balance": balance,
        "Sprint Speed": sprint_speed,
        "Agility": agility,
        "Jumping": jumping,
        # Get Shooting
        "Heading": heading,
        "Shot Power": shot_power,
        "Finishing": finishing,
        "Long Shots": long_shots,
        "Curve": curve,
        "FK Acc.": fk_acc,
        "Penalties": penalties,
        "Volleys": volleys,
        # Get Goalkeeper
        "GK Positioning": gk_positioning,
        "GK Diving": gk_diving,
        "GK Handling": gk_handling,
        "GK Kicking": gk_kicking,
        "GK Reflexes": gk_reflexes,
        # Get Averages
        "ball_skill_avg": ball_skill_avg,
        "defence_avg": defence_avg,
        "mental_avg": mental_avg,
        "passing_avg": passing_avg,
        "physical_avg": physical_avg,
        "shooting_avg": shooting_avg,
        "goalkeeper_avg": goalkeeper_avg,
    }


scraper = get_scraper()
player_stats = []

for player_idx in tqdm(range(0, players.shape[0])):
    player_stat = {}

    player = players.iloc[player_idx]
    player_stat["name"] = player["name"]

    url = player["url"]
    print("Scraping player: ", player["name"])
    print("URL: ", url)

    soup = get_page(url, scraper)
    player_stat.update(get_overall_stats(soup, debug=False))
    player_stat.update(get_main_card(soup, debug=False))
    player_stat.update(get_team_data(soup, debug=False))
    player_stat.update(get_misc_ratings(soup, debug=True))

    print(f"Player stats: {player_stat}")
    player_stats.append(player_stat)
    # break

df = pd.DataFrame(player_stats)
df.to_csv("player_stats.csv", index=False)
