from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as BrowserOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from time import sleep as wait
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

DEFAULT_STARTME_URL = None
LINK_POOL_FILENAME = "links.txt"
DELIMITER = "$#$"

with open("startme.link","r") as temp:
    DEFAULT_STARTME_URL = temp.read().strip()

# Settings Variables
HEADLESS = False # HEADLESS WON'T WORK FOR DIS

def wait_for_element(element,byshit,byvalue):
    found_element = None
    while not found_element:
        found_element = element.find_element(byshit,byvalue)
        if found_element:
            return found_element
        else:
            wait(1)

def scrape(u=DEFAULT_STARTME_URL):
    options = BrowserOptions()
    options.add_argument("log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # options.add_argument("--start-minimized")
    #HEADLESS DOES NOT WORK
    # if HEADLESS:
    #     options.add_argument("--headless=new")
    print("Starting webdriver...")
    driver = webdriver.Edge(options=options)
    print("Fetching webpage...")
    driver.get(u)
    # wait(10)
    print("Getting links...")
    links_titles = dict()
    a_tab = driver.find_elements(By.CLASS_NAME, 'bookmark-item__link')
    # delay = WebDriverWait(driver,10)
    # a_tab = delay.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bookmark-item__link')))
    print(a_tab)
    for a in a_tab:
        href = a.get_attribute("href")
        title = wait_for_element(a,By.CLASS_NAME,"bookmark-item__title").text
        links_titles[href] = title
        # print(href+title)

    print("Quitting driver...")
    driver.quit()

    print(f"Wiping {LINK_POOL_FILENAME}...")
    with open(LINK_POOL_FILENAME,"w") as outfile:
        outfile.write("")

    print("Saving links...")
    with open(LINK_POOL_FILENAME,"a") as outfile:
        for href in links_titles:
            title = links_titles[href]
            line = f"{title}$#${href}"
            outfile.write(line+"\n")
    print("Scrape successful.")
    return links_titles
	
if __name__ == "__main__":
    scrape(DEFAULT_STARTME_URL)