import sys
import os
import re
import datetime
from time import process_time_ns
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Get the absolut path of the current folder 
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create absolut path of the folders containning the other modules 
config_dir = os.path.join(current_dir, '../')
logger_dir = os.path.join(current_dir, '../utils/')

# Add the absolut path of each module to sys.path
sys.path.append(config_dir)
sys.path.append(logger_dir)

# Import modules
import config
from Logger import Logger
from DataStorage import DataStorage


class AmazonScraper:
    def __init__(self):
        # create a driver object using driver_path as a parameter
        self.driver = webdriver.Chrome(config.CHROME_DRIVER)
        

    def max_pages(self)->int:
        self.driver.get(config.AMAZON_URL)
        self.driver.implicitly_wait(5)
        # assign any keyword for searching
        keyword = "wireless charger"
        # create WebElement for a search box
        search_box = self.driver.find_element(By.ID, 'twotabsearchtextbox')
        # type the keyword in searchbox
        search_box.send_keys(keyword)
        # create WebElement for a search button
        search_button = self.driver.find_element(By.ID, 'nav-search-submit-button')
        # click search_button
        search_button.click()
        # wait for the page to download
        self.driver.implicitly_wait(5)
        items = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "s-pagination-item s-pagination-disabled")]')))
        return int(items[0].text)

    def scrape_page(self,data_storage):
            # create arrays to put product informations inside
            product_name = []
            product_asin = []
            product_price = []
            product_ratings = []
            product_ratings_num = []
            product_link = []
            items = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
            for item in items:
                # get product name 
                name = item.find_element(By.XPATH,'.//span[@class="a-size-medium a-color-base a-text-normal"]')
                product_name.append(name.text)
                # get ASIN number (used to identify the product on Amzon)
                data_asin = item.get_attribute("data-asin")
                product_asin.append(data_asin)
                # get product price 
                # find prices
                whole_price = item.find_elements(By.XPATH, './/span[@class="a-price-whole"]')
                fraction_price = item.find_elements(By.XPATH,'.//span[@class="a-price-fraction"]')
                if whole_price != [] and fraction_price != []:
                    price = '.'.join([whole_price[0].text, fraction_price[0].text])
                else:
                    price = 0
                product_price.append(price)
                # find a ratings box
                ratings_box = item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')
                if ratings_box != []:
                    ratings = ratings_box[0].get_attribute('aria-label')
                    ratings_num = ratings_box[1].get_attribute('aria-label')
                else:
                    ratings, ratings_num = 0, 0
                product_ratings.append(ratings)
                product_ratings_num.append(str(ratings_num))
                # get product link
                link = item.find_elements(By.XPATH, './/a')
                if link != []:
                    product_link.append(link[0].get_attribute('href'))
                else:
                    product_link.append('')
            data = [product_name,product_asin,product_price,product_link]
            transformed_data = [list(row) for row in zip(*data)]
            data_storage.add_data(transformed_data)
    def scrape_amazon(self,keyword,max_pages):

        # create a log file for the current execution 
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = os.path.join(current_dir, f"../logs/log_{timestamp}.log")
        log_manager = Logger(log_file_path)

        # create a dataframe to put data inside 
        data_storage = DataStorage()
        columns = ['Product name', 'ANSI', 'price','link']
        # Call the create_dataframe function with the provided data and columns
        data_storage.create_dataframe([], columns)

        page_number = 1
        next_page = ''

        # assign your website to scrape
        try:
            self.driver.get(config.AMAZON_URL)
            # assign any keyword for searching
            keyword = keyword
            # create WebElement for a search box
            search_box = self.driver.find_element(By.ID, 'twotabsearchtextbox')
            # type the keyword in searchbox
            search_box.send_keys(keyword)
            # create WebElement for a search button
            search_button = self.driver.find_element(By.ID, 'nav-search-submit-button')
            # click search_button
            search_button.click()
            # wait for the page to download
            self.driver.implicitly_wait(5)
            while page_number <= max_pages :
                try :
                    self.scrape_page(data_storage)
                    print(page_number)
                    page_number += 1
                    next_page = self.driver.find_element(By.XPATH,'//a[contains(@class, "s-pagination-next")]').get_attribute("href")
                    print(next_page)
                    self.driver.get(next_page)
                    self.driver.implicitly_wait(5)

                except Exception as e:
                    log_manager.log_error(str(e))
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    data_file_path = os.path.join(current_dir, f"../data/extraction_{timestamp}.csv")
                    data_storage.export_to_csv(data_file_path)

            # export data to csv file
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            data_file_path = os.path.join(current_dir, f"../data/extraction_{timestamp}.csv")
            data_storage.export_to_csv(data_file_path) 

        except Exception as e:
            log_manager.log_error(str(e))


    def close(self):
        self.driver.quit()


Amazon = AmazonScraper()
Amazon.scrape_amazon('python books',Amazon.max_pages())