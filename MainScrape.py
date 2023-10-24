from bs4 import BeautifulSoup
import requests
import csv
import time

# Step 1: Extract Fight Cards
def get_fight_card_urls(main_url):
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract and return fight card URLs and dates from soup
    fight_card_data = []

    # Extracting URLs from <a> tags with class 'b-link b-link_style_black'
    for a_tag in soup.find_all('a', class_='b-link b-link_style_black'):
        fight_card_url = a_tag['href']
        fight_card_name_date = a_tag.get_text(strip=True)
        
        # Extracting the date from the <span> tag with class 'b-statistics__date'
        date_tag = a_tag.find_next_sibling('span', class_='b-statistics__date')
        if date_tag:
            date = date_tag.get_text(strip=True)
        else:
            date = "Unknown Date"
        
        # Appending the data as a tuple to the list
        fight_card_data.append((fight_card_url, fight_card_name_date, date))
    
    return fight_card_data

# Step 2: Extract Fights from Each Card
def get_fight_urls(fight_card_url):
    response = requests.get(fight_card_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract and return fight URLs from soup
    fight_urls = []
    
    # Extracting URLs from <a> tags with class 'b-flag b-flag_style_green'
    for a_tag in soup.find_all('a', class_='b-flag b-flag_style_green'):
        fight_url = a_tag['href']
        fight_urls.append(fight_url)
    
    return fight_urls

# Step 3: Extract Data from Each Fight

def get_fight_data(fight_url):
    
    response = requests.get(fight_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # METHOD, ROUND, TIME
    Weight_class = soup.select_one('i.b-fight-details__fight-title').get_text(strip=True)
    Method = soup.select_one('i.b-fight-details__text-item_first').get_text(strip=True).split('\n')[-1].strip()
    Round = soup.select_one('i.b-fight-details__text-item:nth-child(2)').get_text(strip=True).split('\n')[-1].strip()
    Time = soup.select_one('i.b-fight-details__text-item:nth-child(3)').get_text(strip=True).split('\n')[-1].strip()

    statuses = soup.select('i.b-fight-details__person-status')
    fighter_1_result = statuses[0].get_text(strip=True)  # First status
    fighter_2_result = statuses[1].get_text(strip=True)  # Second status

    
    # Directly select the Totals section using the CSS selector
    totals_section = soup.select_one('body > section > div > div > section:nth-child(4)')
    totals_data = extract_table_data(totals_section.find('table'))
    
    # Directly select the Significant Strikes table using the CSS selector
    sig_strikes_table = soup.select_one('body > section > div > div > section:nth-child(6) + table')
    sig_strikes_data = extract_table_data(sig_strikes_table)
    
    fighter_1_name = totals_data[0][0]
    fighter_1_KD = totals_data[1][0]
    fighter_1_SIG_STR = totals_data[2][0]
    fighter_1_TD = totals_data[5][0]
    fighter_1_SUB_ATT = totals_data[7][0]
    fighter_1_REV = totals_data[8][0]
    fighter_1_Ctrl = totals_data[9][0]
    fighter_1_Distance = sig_strikes_data[6][0]
    fighter_1_Clinch = sig_strikes_data[7][0]
    fighter_1_Ground = sig_strikes_data[8][0]

    fighter_2_name = totals_data[0][1]
    fighter_2_KD = totals_data[1][1]
    fighter_2_SIG_STR = totals_data[2][1]
    fighter_2_TD = totals_data[5][1]
    fighter_2_SUB_ATT = totals_data[7][1]
    fighter_2_REV = totals_data[8][1]
    fighter_2_Ctrl = totals_data[9][1]
    fighter_2_Distance = sig_strikes_data[6][1]
    fighter_2_Clinch = sig_strikes_data[7][1]
    fighter_2_Ground = sig_strikes_data[8][1]

    row = [
        Weight_class, Method, Round, Time, 
        fighter_1_name, fighter_1_result, fighter_1_KD, fighter_1_SIG_STR, 
        fighter_1_TD, fighter_1_SUB_ATT, fighter_1_REV, fighter_1_Ctrl, 
        fighter_1_Distance, fighter_1_Clinch, fighter_1_Ground,
        fighter_2_name, fighter_2_result, fighter_2_KD, fighter_2_SIG_STR, 
        fighter_2_TD, fighter_2_SUB_ATT, fighter_2_REV, fighter_2_Ctrl, 
        fighter_2_Distance, fighter_2_Clinch, fighter_2_Ground
    ]
    
    
    return row

def extract_table_data(table):
    data = []
    rows = table.find('tbody').find_all('tr')
    for row in rows:  #Only 1 row
        cols = row.find_all(['td', 'th'])
        # Splitting the text content for two fighters and appending them separately
        cols = [[text.strip() for text in ele.text.split('\n') if text.strip()] for ele in cols]
        data.append(cols)
    return cols

# Main URL that lists all fight cards
#main_url = 'http://ufcstats.com/statistics/events/completed'
main_url = 'http://ufcstats.com/statistics/events/completed?page=all'

# CSV Headers
headers = [
    "Date", "Weight Class", "Method", "Round", "Time", 
    "Fighter 1 Name", "Fighter 1 Result", "Fighter 1 KD", "Fighter 1 SIG STR", 
    "Fighter 1 TD", "Fighter 1 SUB ATT", "Fighter 1 REV", "Fighter 1 Ctrl", 
    "Fighter 1 Distance", "Fighter 1 Clinch", "Fighter 1 Ground",
    "Fighter 2 Name", "Fighter 2 Result", "Fighter 2 KD", "Fighter 2 SIG STR", 
    "Fighter 2 TD", "Fighter 2 SUB ATT", "Fighter 2 REV", "Fighter 2 Ctrl", 
    "Fighter 2 Distance", "Fighter 2 Clinch", "Fighter 2 Ground"
]

# Open CSV file
with open('fight_data_all.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Writing headers

    # Step 1: Iterate through all fight cards
    for fight_card_url, fight_card_name, date in get_fight_card_urls(main_url):
        
        print(f"{fight_card_name} scraping begins...")  
        #time.sleep(3)
        # Step 2: Iterate through all fights in a card
        for fight_url in get_fight_urls(fight_card_url):
            
            # Introduce delay between fetching data for individual fights
            #time.sleep(1)  # sleep for 1 second, adjust as needed
            
            row = get_fight_data(fight_url)
            if row is not None:
                writer.writerow([date] + row)  # Writing data
            else:
                print(f"Failed to extract data for fight: {fight_url}")
            # Step 3: Extract and write fight data
           
