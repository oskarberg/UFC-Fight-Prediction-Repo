from bs4 import BeautifulSoup
import requests
import csv

url = 'http://ufcstats.com/fight-details/23a604f460289271'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')



# METHOD, ROUND, TIME
Weight_class = soup.select_one('i.b-fight-details__fight-title').get_text(strip=True)
Method = soup.select_one('i.b-fight-details__text-item_first').get_text(strip=True).split('\n')[-1].strip()
Round = soup.select_one('i.b-fight-details__text-item:nth-child(2)').get_text(strip=True).split('\n')[-1].strip()
Time = soup.select_one('i.b-fight-details__text-item:nth-child(3)').get_text(strip=True).split('\n')[-1].strip()

fighters = soup.select('a.b-fight-details__person-link')
fighter_1_name = fighters[0].get_text(strip=True)
fighter_2_name = fighters[1].get_text(strip=True)

statuses = soup.select('i.b-fight-details__person-status')
fighter_1_result = statuses[0].get_text(strip=True)  # First status
fighter_2_result = statuses[1].get_text(strip=True)  # Second status


texts = [element.get_text(strip=True) for element in soup.select('p.b-fight-details__table-text')]


fighter_1_KD = texts[2]
fighter_1_SIG_STR = texts[4]
fighter_1_TD = texts[10]
fighter_1_SUB_ATT = texts[14]
fighter_1_REV = texts[16]
fighter_1_Ctrl = texts[18]
fighter_1_Distance = texts[72]
fighter_1_Clinch = texts[74]
fighter_1_Ground = texts[76]


fighter_2_KD = texts[3]
fighter_2_SIG_STR = texts[5]
fighter_2_TD = texts[11]
fighter_2_SUB_ATT = texts[15]
fighter_2_REV = texts[17]
fighter_2_Ctrl = texts[19]
fighter_2_Distance = texts[73]
fighter_2_Clinch = texts[75]
fighter_2_Ground = texts[77]



row = [
    Weight_class, Method, Round, Time, 
    fighter_1_name, fighter_1_result, fighter_1_KD, fighter_1_SIG_STR, 
    fighter_1_TD, fighter_1_SUB_ATT, fighter_1_REV, fighter_1_Ctrl, 
    fighter_1_Distance, fighter_1_Clinch, fighter_1_Ground,
    fighter_2_name, fighter_2_result, fighter_2_KD, fighter_2_SIG_STR, 
    fighter_2_TD, fighter_2_SUB_ATT, fighter_2_REV, fighter_2_Ctrl, 
    fighter_2_Distance, fighter_2_Clinch, fighter_2_Ground
]


# Headers for the CSV file
headers = [
    "Weight Class", "Method", "Round", "Time", 
    "Fighter 1 Name", "Fighter 1 Result", "Fighter 1 KD", "Fighter 1 SIG STR", 
    "Fighter 1 TD", "Fighter 1 SUB ATT", "Fighter 1 REV", "Fighter 1 Ctrl", 
    "Fighter 1 Distance", "Fighter 1 Clinch", "Fighter 1 Ground",
    "Fighter 2 Name", "Fighter 2 Result", "Fighter 2 KD", "Fighter 2 SIG STR", 
    "Fighter 2 TD", "Fighter 2 SUB ATT", "Fighter 2 REV", "Fighter 2 Ctrl", 
    "Fighter 2 Distance", "Fighter 2 Clinch", "Fighter 2 Ground"
]

# Writing data to a CSV file
with open('fight_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Writing headers
    writer.writerow(row)  # Writing data


