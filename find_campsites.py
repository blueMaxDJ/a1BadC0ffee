from datetime import datetime
import logging
from typing import List

from camply.containers import AvailableCampsite, SearchWindow
from camply.search import SearchRecreationDotGov
import yaml
import telegram
import telegram_send
import time
logging.basicConfig(format="%(asctime)s [%(levelname)8s]: %(message)s",
                    level=logging.ERROR)

avoidCampList = ['Timber Creek', 'Fish Creek', 'Apgar']


def teleprint(str):
    global tele_message
    print(str)
    tele_message += f'{str}\n' 

def search_by_campgrounds(start_date, end_date, park_name, camp_id, camp_name):
    match_count = 0
    search_win = SearchWindow(start_date=start_date,
                                end_date=end_date)
    camping_finder = SearchRecreationDotGov(search_window=search_win,
                                            campgrounds=camp_id,
                                            weekends_only=False,
                                            nights=1)
    matches: List[AvailableCampsite] = camping_finder.get_matching_campsites(log=True, verbose=True,
                                                                            continuous=False)                                                                         
    for match in matches:
        match_count = match_count + 1
        teleprint(f'{match.facility_name}:{match.campsite_site_name} [{match.campsite_type}] available for {match.booking_date}')
    if (not match_count):
        print(f'No campsite available for dates {start_date} to {end_date} for {park_name}: {camp_name}')
    return match_count

def search_by_park_id(start_date, end_date, park_id, park_name):
    match_count=0
    search_win = SearchWindow(start_date=start_date,
                                end_date=end_date)
    camping_finder = SearchRecreationDotGov(search_window=search_win,
                                            recreation_area=park_id,
                                            weekends_only=False,
                                            nights=1)

    matches: List[AvailableCampsite] = camping_finder.get_matching_campsites(log=False, verbose=False,
                                                                            continuous=False)                                                                            
    for match in matches:
        avoid_camp_match = 0
        for avoidCamp in avoidCampList:
            if avoidCamp in match.facility_name:
                avoid_camp_match = 1
        if avoid_camp_match == 1:
            continue
        if 'GROUP' in match.campsite_type:
            continue        
        match_count = match_count + 1
        teleprint(f'{match.facility_name}:{match.campsite_site_name} [{match.campsite_type}] available for {match.booking_date}')
    if (not match_count):
        print(f'No campsite available for dates {start_date} to {end_date} for {park_name}')
    return match_count


bot = telegram.Bot("5385158546:AAE3dDq2wGz9cktstVlhm4E48uG1agYVUmk")
poll_cnt = 1
while(1):
    match_count = 0
    tele_message = ""
    format = '%Y-%m-%d'
    with open("config.yml", "r") as yml_file:
        configs = yaml.safe_load(yml_file)
        for park in configs['parks']:
            if (poll_cnt % int(park['poll']) == 0): 
                start_date = datetime.strptime(str(park['start_date']), format)
                end_date = datetime.strptime(str(park['end_date']), format)  
                match_count += search_by_park_id(start_date, end_date, park['id'], park['name'])
        
        for campground in configs['campgrounds']:
            if (poll_cnt % int(campground['poll']) == 0): 
                start_date = datetime.strptime(str(campground['start_date']), format)
                end_date = datetime.strptime(str(campground['end_date']), format)   
                park_name = campground['park_name']
                for camp_id in campground['camp_ids']:
                    match_count += search_by_campgrounds(start_date, end_date, park_name, camp_id['id'], camp_id['name'] )
    if match_count:

        print(f"Sending telegram message for poll_cnt {poll_cnt}")
        # telegram_send.send(messages=[f'{tele_message}'])
        bot.send_message(-1001539975375, text=f'{tele_message}')

    poll_cnt = poll_cnt + 1
    time.sleep(20)
