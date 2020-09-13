import csv
import time
from datetime import timedelta

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

st = time.perf_counter()


def ms_to_hms(millis: int) -> str:
    if millis > 0:
        return str(timedelta(milliseconds=millis)).split('.')[0]
    else:
        return "--:--:--"


print("Welcome \n\nInput url to continue")
html = input(">>> ")
# html = "http://results.xacte.com/?kw=riteaid"
# html = "http://live.xacte.com/templates/philadelphiamarathon.com/for-runners/race-results/"
url = "http://results.xacte.com/json/search"

print("\nGetting data please wait ...\n")

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
browser = webdriver.Chrome("./chromedriver", options=options)
browser.get(html)
time.sleep(5)

print("\nCompleted\n")
event = Select(browser.find_element_by_id("xact_results_event"))

print("\nPlease select an event from the list below\n")

for i, v in enumerate(event.options):
    print(i, v.text)
while True:
    try:
        selected_event = int(input(">>> "))
        event.select_by_index(selected_event)
        break
    except (ValueError, NoSuchElementException):
        print("please enter one of the numbers above")

time.sleep(2)

race = Select(browser.find_element_by_id("xact_results_search_race"))

print("\nPlease select a race from the list below\n")

for i, v in enumerate(race.options):
    print(i, v.text)
while True:
    try:
        selected_race = int(input(">>> "))
        race.select_by_index(selected_race)
        break
    except (ValueError, NoSuchElementException):
        print("please enter one of the numbers above")

time.sleep(2)

print("\nProcessing please wait ...\n ")
se = event.first_selected_option
sr = race.first_selected_option

eventId = se.get_attribute("value")
subeventId = sr.get_attribute("value")
total_size = requests.get(url, {"eventId": eventId, "subeventId": subeventId, }).json()["iTotalRecords"]

print("total records", total_size)
print("selected event:", se.text,
      "\nselected event Id:", eventId,
      "\nselected race:", sr.text,
      "\nselected race Id:", subeventId)

params = {"eventId": eventId,
          "subeventId": subeventId,
          "iColumns": "",
          "iDisplayStart": "0",
          "iDisplayLength": total_size}

print("\nCollecting records please wait ...\n")

response = requests.get(url, params=params).json()["aaData"]

with open('results.csv', 'w+', newline='') as csvfile:
    fieldnames = ["bib", "name", "City/State", "Age", "Gender", "Net time", "Clock time"]
    writer = csv.writer(csvfile)

    writer.writerow(fieldnames)

    for entry in response:
        bib = entry.get("bib", "")
        name = f'{entry.get("firstname")} {entry.get("lastname")}'
        age = entry.get('age')
        gender = entry.get('sex')
        city_sate = f'{entry.get("city")} {entry.get("state")}'
        net_time = int(entry.get("chiptime")) if entry.get("chiptime") else 0
        clock_time = int(entry.get("clocktime")) if entry.get("clocktime") else 0

        writer.writerow([bib, name, city_sate, age, gender, ms_to_hms(net_time), ms_to_hms(clock_time)])

print("\nProcess completed successfully")
et = time.perf_counter()

print("time: ", et - st)
