from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as BrowserOptions
import logging
from time import sleep as wait
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

LINK_POOL_FILENAME = "links.txt"
DELIMITER = "$#$"
WEBDRIVER_START_RETRIES = 2
PAGE_LOADED_RETRIES = 10
DEFAULT_STARTME_URL = None

logger = logging.getLogger(__name__)
logging.basicConfig(filename='scraper.log', encoding='utf-8', level=logging.INFO)

try:
    with open("startme.link","r") as temp:
        DEFAULT_STARTME_URL = temp.read().strip()
except:
    logger.critical("Failed to open startme.link file, either bad perms or does not exist. Exiting...")
    exit()

def wait_for_element(element,byshit,byvalue):
    '''
    Unused
    '''
    found_element = None
    while not found_element:
        found_element = element.find_element(byshit,byvalue)
        if found_element:
            return found_element
        else:
            wait(1)

def scrape(u=DEFAULT_STARTME_URL):
    logger.info("Beginning scrape.")
    logger.info("Starting webdriver...")
    options = BrowserOptions()
    options.add_argument("log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = None
    while not driver:
        retries = 0
        try:
            driver = webdriver.Edge(options=options)
        except:
            logger.error("Webdriver failed to start, retrying...")
            retries+=1
            wait(5)
        if retries == WEBDRIVER_START_RETRIES:
            logger.critical(f"Webdriver failed to start after {str(retries+1)} attempts. Exiting early...")
            return -1
    
    logger.info("Webdriver started.")
    logger.info("Fetching webpage...")

    try:
        driver.get(u)
        wait(3)
    except:
        logger.critical("Webdriver get request failed.")

    test_element = None
    while not test_element:
        retries = 0
        test_element = driver.find_element(By.CLASS_NAME, 'bookmark-item__link')
        if test_element:
            break
        else:
            logger.warning("Webpage not yet loaded. Waiting...")
            wait(5)
            retries+=1
        if retries == PAGE_LOADED_RETRIES:
            logger.critical("Webdriver could not load webpage. Exiting early...")
            driver.quit()
            return -1

    links_titles = dict()
    a_tab = driver.find_elements(By.CLASS_NAME, 'bookmark-item__link')

    if len(a_tab) == 0:
        logger.critical("Webdriver failed to extract bookmark link elements from webpage.")

    for a in a_tab:
        href = a.get_attribute("href")
        title = a.find_element(By.CLASS_NAME,"bookmark-item__title").text
        links_titles[href] = title

    logger.info("Stopping webdriver...")
    try:
        driver.quit()
    except:
        logger.error("Webdriver exited ungracefully.")

    if len(links_titles) == 0:
        logger.critical("Failed to extract links and titles from webpage. Exiting early...")
        return -1

    try:
        with open(LINK_POOL_FILENAME,"w") as outfile:
            outfile.write("")
    except:
        logger.critical("Failed to initialize link pool file, possibly bad perms")
        return -1
    
    with open(LINK_POOL_FILENAME,"a") as outfile:
        for href in links_titles:
            title = links_titles[href]
            line = f"{title}$#${href}"
            outfile.write(line+"\n")
    logger.info("Scrape successful.")
    return links_titles
	
if __name__ == "__main__":
    logger.info("Scraper run manually.")
    scrape(DEFAULT_STARTME_URL)