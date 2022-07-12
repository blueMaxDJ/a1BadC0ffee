import os
import time
import selenium.common.exceptions
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import sys
import re
import telegram

class GNPLodgeScanner(object):

    def __init__(self):
        self.tele_message = ""

    def teleprint(self, str):
        print(str)
        self.tele_message += f'{str}\n' 

    def link_gen(self):
        link = "https://secure.glaciernationalparklodges.com/booking/lodging-search?destination=ALL&adults=3&children=1&rateCode=INTERNET&rateType=promo&dateFrom=07-28-2022&nights=1"
        return link

    def check(self, page_source):
        found = 0
        html_soup = BeautifulSoup(page_source, 'html.parser')
        hotel_containers = html_soup.find_all('div', class_ = 'product-card__title mb-16')
        room_avail = html_soup.find_all('div', class_ = 'availability-message') 

        for hotel, room in zip(hotel_containers, room_avail): 
            res = re.search('<span>(.*)</span>',str(hotel.contents[0]))
            res_hotel = res.group(1).strip()
            if "Swiftcurrent Motor" in hotel or "Many Glacier" in hotel:
                if ("ROOM LEFT" in room.contents[0]):
                    self.teleprint(f'{res_hotel} {room.contents[0]}')
                    found = 1
            else:
                print(res_hotel, room.contents[0])
        return found

    def run(self):
        # Create search link
        search_link = self.link_gen()
        # Begin Scanning
        check_url = 1
        bot = telegram.Bot("5385158546:AAE3dDq2wGz9cktstVlhm4E48uG1agYVUmk")
        while check_url:
            try:
                # check_url = 0
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                print(timestamp)
                driver_path = os.getcwd() + "\\chromedriver.exe"
                browser = webdriver.Chrome(executable_path=driver_path)
                browser.set_page_load_timeout(60)
                browser.get(search_link)
                time.sleep(15)
                found = self.check(browser.page_source)
                if found:
                    bot.send_message(-1001539975375, text=f'{self.tele_message}')
                    self.tele_message = ""
                time.sleep(15)
            except selenium.common.exceptions.TimeoutException:
                print("Time out loading web page.")
            except:
                print("Something goes wrong: ")
            finally:
                browser.quit()

gnp = GNPLodgeScanner()
gnp.run()