import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL of the website to scrape
base_url = "https://www.howstat.com/Cricket/Statistics/Players/PlayerList.asp?Group="

# List to hold player data
players_data = []

# Loop through each alphabet group A to Z
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    # Form the complete URL for each alphabet group
    url = base_url + char
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing player data
        table = soup.find('table', {'class': 'TableLined'})
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip the header row
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 6:
                    player = {
                        'Name': cols[0].text.strip(),
                        'Born': cols[1].text.strip(),
                        'Country (Current)': cols[2].text.strip(),
                        'Tests': cols[3].text.strip(),
                        'ODIs': cols[4].text.strip(),
                        'T20s': cols[5].text.strip()
                    }
                    players_data.append(player)

# Create a DataFrame from the list of player data
df = pd.DataFrame(players_data)

# Save the DataFrame to a CSV file
df.to_csv('cricket_players.csv', index=False)

print("Data scraped and saved to cricket_players.csv")