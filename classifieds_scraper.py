import csv
import os

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class CraiglistScraper(object):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    def __init__(self, location, car, make, minAutoYear, maxAutoYear, radius):
        self.location = location
        self.car = car
        self.make = make
        self.minAutoYear = minAutoYear
        self.maxAutoYear = maxAutoYear
        self.radius = radius

        self.url = f"https://{location}.craigslist.org/search/sss?query={car}&auto_make_model={make}+" \
                   f"{car}&min_auto_year={minAutoYear}&max_auto_year={maxAutoYear}"
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.chrome_options)
        self.delay = 3

    def load_craigslist_url(self):
        self.driver.get(self.url)
        try:
            wait = WebDriverWait(self.driver, self.delay)
            wait.until(EC.presence_of_element_located((By.ID, "searchform")))
            print(f"Parsing: {self.url}")
            self.page_html = self.driver.page_source
        except TimeoutException:
            print("Loading took too much time")

    def extract_post_information(self):
        all_posts = self.driver.find_elements_by_class_name("result-row")

        dates = []
        titles = []
        prices = []

        for post in all_posts:
            title = post.text.split("$")

            if title[0] == '':
                title = title[1]
            else:
                title = title[0]

            title = title.split("\n")
            price = title[0]
            title = title[-1]

            title = title.split(" ")

            month = title[0]
            day = title[1]
            title = ' '.join(title[2:])
            date = month + " " + day

            titles.append(title)
            prices.append(price)
            dates.append(date)

        return titles, prices, dates

    def extract_post_urls(self):
        url_list = []

        soup = BeautifulSoup(self.driver.page_source, "lxml")
        for link in soup.findAll("a", {"class": "result-title hdrlnk"}):
            print(link["href"])
            url_list.append(link["href"])
        return url_list

    def write_to_csv(self):
        today = datetime.now().strftime('%d-%m')
        user_desktop = os.path.expanduser("~/Desktop")
        output_file = os.path.join(user_desktop, f'{location}_{car}_{make}_classifieds_output{today}.csv')

        with open(output_file, mode='w', encoding="utf-8") as csv1:
            title = ''
            price = ''
            date = ''
            url = ''
            fields = OrderedDict({'title': title, 'price': price, 'date': date, 'url': url})
            writer = csv.DictWriter(csv1, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            titles, prices, dates = scraper.extract_post_information()
            urls = scraper.extract_post_urls()

            for title, price, date, url in (zip(titles, prices, dates, urls)):
                writer.writerow(
                    {'title': title, 'price': price, 'date': date, 'url': url})

            print(f'Finished, output file is: {output_file}')

    def quit(self):
        self.driver.close()
        self.driver.quit()


location = input('Please input a market to search (e.g "sfbay")\n')
car = input('Please input a car model to search (e.g "Corolla")\n')
make = input('Please input a car make to search (e.g "Toyota")\n')
minAutoYear = input('Please select minimum model year (e.g "2003")\n')
minAutoYear = 'min_auto_year=' + minAutoYear
maxAutoYear = input('Please select maximum model year (e.g "2008")\n')
maxAutoYear = 'max_auto_year=' + maxAutoYear
radius = 5000

scraper = CraiglistScraper(location, car, make, minAutoYear, maxAutoYear, radius)
scraper.load_craigslist_url()
titles, prices, dates = scraper.extract_post_information()
urls = scraper.extract_post_urls()

scraper.write_to_csv()
scraper.quit()
