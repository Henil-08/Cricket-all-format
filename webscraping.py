import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to get the player metadata from their individual page
def get_player_metadata(player_url):
    player_response = requests.get(player_url)
    player_soup = BeautifulSoup(player_response.content, 'html.parser')
    
    player_data = {}
    info_sections = player_soup.find('div', class_='ds-grid lg:ds-grid-cols-3 ds-grid-cols-2 ds-gap-4 ds-mb-8')
    for section in info_sections:
        key_element = section.find('p', class_='ds-text-tight-m ds-font-regular ds-uppercase ds-text-typo-mid3')
        value_element = section.find('span', class_='ds-text-title-s ds-font-bold ds-text-typo')
        if key_element and value_element:
            key = key_element.text.strip().replace(":", "")
            value = value_element.text.strip()
            player_data[key] = value
    return player_data

# Function to scrape the main page and player data
# Function to scrape the main page and player data
def scrape_cricket_data(classs, page, type):
    url = f"https://stats.espncricinfo.com/ci/engine/stats/index.html?class={classs};page={page};template=results;type={type}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Error fetching page {page}: Status code {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    players_data = []

    # Find the table
    tables = soup.find_all('table', class_='engineTable')

    if not tables:
        raise ValueError("Could not find the data table on the page")

    for table in tables:
        if table.find("caption"):
            final = table

    rows = final.find_all('tr')

    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) > 0:
            player_name = cols[0].text.strip()
            player_link = cols[0].find('a')['href']
            player_url = f"https://www.espncricinfo.com{player_link}"

            player_data = {
                'Player Name': player_name,
                'Player URL': player_url,
                'Span': cols[1].text.strip(),
                'Matches': cols[2].text.strip(),
                'Innings': cols[3].text.strip(),
                'Balls': cols[4].text.strip(),
                'Runs': cols[5].text.strip(),
                'Wickets': cols[6].text.strip(),
                'BBI': str(cols[7].text.strip()),
                'BBM': str(cols[8].text.strip()),
                'Ave': cols[9].text.strip(),
                'Econ': cols[10].text.strip(),
                'SR': cols[11].text.strip(),
                '5': cols[12].text.strip(),
                '10': cols[13].text.strip(),
                '4s': cols[13].text.strip(),
                '6s': cols[14].text.strip()
            }

            # player_data.update(get_player_metadata(player_url))
            players_data.append(player_data)

    return players_data

# Function to scrape data from multiple pages
def scrape_all_pages(classs, total_pages, type):
    all_players_data = []
    for page_number in range(1, total_pages + 1):
        print(f"Scraping page {page_number} of {type} data...")
        page_data = scrape_cricket_data(classs, page_number, type)
        all_players_data.extend(page_data)
    return all_players_data


# # Scrape Test Batting data
# batting_data = scrape_all_pages(64, "batting")
# batting_df = pd.DataFrame(batting_data)
# batting_df.to_csv('Data/Test_Batting.csv', index=False)

# Scrape Test Bowling data
bowling_data = scrape_all_pages(1, 64, "bowling")
bowling_df = pd.DataFrame(bowling_data)
bowling_df.to_csv('Data/Test_Bowling.csv', index=False)

# Scrape Test Bowling data
bowling_data = scrape_all_pages(2, 60, "bowling")
bowling_df = pd.DataFrame(bowling_data)
bowling_df.to_csv('Data/ODI_Bowling.csv', index=False)

# Scrape Test Bowling data
bowling_data = scrape_all_pages(3, 80, "bowling")
bowling_df = pd.DataFrame(bowling_data)
bowling_df.to_csv('Data/T20_Bowling.csv', index=False)
