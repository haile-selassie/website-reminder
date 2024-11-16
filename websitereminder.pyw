# Reminds you to visit websites you haven't been to in a while
import win10toast_click
import os
import re
import time
import startme_scraper
from datetime import datetime
import logging

LINK_HISTORY_FILENAME = "history.txt"
NOTIFY_HOUR = "17"
SLEEP_INTERVAL = 60*60

logger = logging.getLogger(__name__)
logging.basicConfig(filename='reminder.log', encoding='utf-8', level=logging.INFO)

def domain_from_url(url):
    '''
    Unused
    '''
    domain = re.search(r"([\d\w]{2,}\.)+[\d\w]{2,}",url).group()
    domain = domain.replace("www.","")
    return domain

def update_link(link,title,newday):
    '''
    Updates a particular link in the history file so that its date field matches today
    '''
    contents = None
    with open(LINK_HISTORY_FILENAME,"r") as file:
        contents = file.read()
    origString = title+startme_scraper.DELIMITER+link+startme_scraper.DELIMITER+newday
    newString = title+startme_scraper.DELIMITER+link+startme_scraper.DELIMITER+datetime.now().strftime('%d-%m-%Y')
    contents = contents.replace(origString,newString)
    with open(LINK_HISTORY_FILENAME,"w") as file:
        file.write(contents)

def openlink(url):
    '''
    Opens up a page in default browser
    '''
    os.system(f"start {url}")

def notify(url,title):
    '''
    Uses toast to deliver a Windows Toast notification to the user at specified hour
    '''
    notifier = win10toast_click.ToastNotifier()
    notifier.show_toast(
        "Website Reminder",
        f"You haven't visited {title} in a while. Click to open.",
        duration = 60,
        threaded=True,
        callback_on_click=lambda: openlink(url)
    )

def get_oldest_link():
    '''
    Finds the oldest, or the first of many oldest links, and returns the link, title, and last day it was chosen
    '''
    oldest_title = None
    oldest_link = None
    oldest_day = None
    biggest_diff = None
    with open(LINK_HISTORY_FILENAME,"r") as infile:
        # Unpack each line
        for line in infile:
            line = line.strip()
            line = line.split(startme_scraper.DELIMITER)
            title = line[0]
            link = line[1]
            # -1 means never served before, so it gets priority
            if line[2] == "-1": return link,title,line[2]
            dt = datetime.strptime(line[2], '%d-%m-%Y')
            diff = (datetime.now() - dt).days
            # Initialize the beginning variable, or set them if it found a link that's older
            if not oldest_link or diff > biggest_diff:
                oldest_title = title
                oldest_link = link
                oldest_day = dt.strftime('%d-%m-%Y')
                biggest_diff = diff
                continue
    return oldest_link,oldest_title,oldest_day

def is_correct_hour():
    """
    Checks if the current hour matches the hour set as the notification hour
    """
    # zfill so that times are represented as 00-24
    current_hour = datetime.now().time().hour
    current_hour = str(current_hour).zfill(2)
    if current_hour == NOTIFY_HOUR.zfill(2):
        print("Is correct hour")
        return True
    else:
        print("Is not correct hour")
        return False

def served_today():
    """
    Checks if a link has been served today
    """
    # Initialize a variable
    result = None
    # Simply checks if the current date is anywhere within the history file
    with open(LINK_HISTORY_FILENAME,"r") as file:
        if datetime.now().strftime('%d-%m-%Y') in file.read():
            result = True
        else:
            result = False
    return result

def update_history():
    """
    Migrates the scraped links pool file over to the history file
    """
    # Get a set of all of the links that are already mentioned in the history file to compare against prospective links
    links_recorded = set()
    with open(LINK_HISTORY_FILENAME,"r") as history_infile:
        for line in history_infile:
            line = line.strip()
            line = line.split(startme_scraper.DELIMITER)
            link = line[1].strip()
            links_recorded.add(link)

    # Get a dictionary of all the links that need to be added
    links_titles_to_add = dict()
    with open(startme_scraper.LINK_POOL_FILENAME,"r") as link_pool_infile:
        for line in link_pool_infile:
            line = line.strip()
            title,link = line.split(startme_scraper.DELIMITER)
            link = link.strip()
            # Exclude links that already exist
            if link in links_recorded:
                continue
            else:
                # Add to dictionary
                links_titles_to_add[link] = title

    # If there were no new links to add, just skip entirely
    if len(links_titles_to_add) > 0:
        # Append the new links to the history file, -1 is used as a flag in place of a date to show that it has never been served to the user
        with open(LINK_HISTORY_FILENAME,"a") as history_outfile:
            for link in links_titles_to_add:
                title = links_titles_to_add[link]
                history_outfile.write(title+startme_scraper.DELIMITER+link+startme_scraper.DELIMITER+"-1"+'\n')
    else:
        logger.warning("No new links found when updating history file.")

def main():
    if served_today(): return
    if not is_correct_hour(): return
    logger.info("It's time to serve a link. Updating history...")
    update_history()
    logger.info("Selecting link to serve...")
    link_to_serve,title,old_day = get_oldest_link()
    update_link(link_to_serve,title,old_day)
    logger.info("Delivering notification.")
    notify(link_to_serve,title)

if __name__ == "__main__":
    logger.info("Initializing website reminder server...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        with open(LINK_HISTORY_FILENAME,"r") as tempfile:
            pass
    except:
        logger.warning("History file not found, initializing...")
        with open(LINK_HISTORY_FILENAME,"w") as tempfile:
            tempfile.write("")

    try:
        with open(startme_scraper.LINK_POOL_FILENAME,"r") as tempfile:
            pass
    except:
        logger.warning("Link pool file not found, running scraper...")
        with open(startme_scraper.LINK_POOL_FILENAME,"w") as tempfile:
            startme_scraper.scrape()

    logger.info("Website reminder server running.")
    while True:
        logger.info("Running reminder process...")
        main()
        logger.info("Reminder attempt finished, waiting for next interval...")
        time.sleep(SLEEP_INTERVAL)