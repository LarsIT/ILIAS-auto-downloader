# pip3 install requests beautifulsoup4
import os
import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

with open("package.json", "r") as log:
    payload = json.load(log)

log = []


def write_log(log):
    with open("logfile.txt", "w") as logfile:
        for entry in log:
            logfile.write(entry)
            logfile.write("\n")

# TODO:
#   file structure should be retained for download
#   fix function timeout on empy pages
def scrape_folder(driver, folder_url):
    div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ilContainerItemsContainer"))
    )

    links = div.find_elements(By.TAG_NAME, "a")

    for link in links:

        link_text = link.text.strip()
        link_url = link.get_attribute("href")

        if 'cmd=view&cmdClass=ilrepository' in link_url: # TODO optimize ability to distinguish between folder, file, test, forum
            log.append(f"Entering folder: {link_text}")
            log.append("___")

            driver.switch_to.new_window("window")
            driver.get(link_url)

            scrape_folder(driver, link_url)

            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

        elif 'download' in link_url:
            log.append(f"Found file: {link_text}")
            # link.click()


download_dir = os.path.join("~/Documents/University/WS_2425/Electives/WPFs", "Business English C1")
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", download_dir)
options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                       "application/pdf, application/zip, application/octet-stream")
options.set_preference("pdfjs.disabled", True)

# Initialize Selenium WebDriver with the profile
driver = webdriver.Firefox(options=options)

driver.get(
    "https://ilias.h-ka.de/ilias.php?ref_id=772135&cmdClass=ilrepositorygui&cmdNode=y0&baseClass=ilrepositorygui"
)

# login page
element_username = driver.find_element(By.XPATH, '//*[@id="username"]')
element_password = driver.find_element(By.XPATH, '//*[@id="password"]')
element_username.send_keys(payload["username"])
element_password.send_keys(payload["password"])
element_password.send_keys(Keys.RETURN)

# Course selection
# TODO adjust location method
# TODO implement query function with autocomplete,
#  eg. "Which course would you like to update?" -> "english" -> *completes to business english c1 and selects it as course*
course = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH,
                                    '/html/body/div[1]/main/div/div[1]/div/div/div/div[3]/div[3]/div/div/div/div[2]/div/div[12]/div/div/div/div/div[2]/div[1]/a'))
)
course.click()

# Content download
try:
    current_url = driver.current_url
    scrape_folder(driver, current_url)
finally:
    write_log(log)
    driver.quit()

# Close the driver
