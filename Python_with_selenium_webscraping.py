import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException
)

class Redbus:
    def __init__(self, Xpath):
        self.Xpath = Xpath
        self.Bus = {}  
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome()

        # Open the Redbus page
        self.driver.get('https://www.redbus.in/')
        time.sleep(5)

        # Scroll horizontally to bring the element into view
        target_element = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, self.Xpath)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
        time.sleep(2)

        # Click on the state bus link
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.Xpath))).click()
        time.sleep(10)

        Bus_Route_link = []
        Bus_Route_name = []

        # Loop to gather bus routes and their links from all pages until no more pages are available
        page = 1
        while True:
            try:
                current_page_links = [i.get_attribute('href') for i in self.driver.find_elements(By.XPATH, "//div[@class='route_details']//a")]
                current_page_names = [i.text for i in self.driver.find_elements(By.XPATH, "//a[@class='route']")]

                # Only add unique links and names to the main list
                for link, name in zip(current_page_links, current_page_names):
                    if link not in Bus_Route_link:
                        Bus_Route_link.append(link)
                        Bus_Route_name.append(name)
                # Print the bus routes and links to verify they are being collected
                print(f"Page {page} - Bus Routes and Links:")
                for name, link in zip(Bus_Route_name, Bus_Route_link):
                    print(f"Route Name: {name}, Route Link: {link}")
                print("\n")

                # Try to navigate to the next page
                next_page_xpath = f"//div[12]/div[{page + 1}]"

                if not self.driver.find_elements(By.XPATH, next_page_xpath):
                    print(f"Page {page + 1} does not exist. Exiting loop.")
                    break

                # Wait for the element to be present and visible
                element = WebDriverWait(self.driver, 25).until(EC.visibility_of_element_located((By.XPATH, next_page_xpath)))

                # Scroll the element into view before clicking
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)  

                # Attempt to click the element
                element.click()
                time.sleep(5)

                page += 1

            except ElementNotInteractableException as e:
                print(f"Error navigating to page {page + 1}: {e}")
                break
            except ElementClickInterceptedException as e:
                print(f"Click intercepted when trying to navigate to page {page + 1}: {e}")
                break
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error loading page {page + 1}: {e}")
                break

        def smooth_scroll():
            """Function to scroll to the bottom of the page to ensure all elements are loaded."""
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to the bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait for new content to load
                time.sleep(2)
                # Calculate new scroll height and compare with last height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        # Start scraping bus details from each link
        for name, link in zip(Bus_Route_name, Bus_Route_link):
            self.driver.get(link)
            time.sleep(10)
            self.Bus[name] = {"Private": {}, "Government": {}}

            # Wait for elements to load and fetch private bus details
            time.sleep(10) 
            try:
                # Smooth scroll before scraping private bus details
                smooth_scroll()

                # Scrape private bus details
                Bus_travel_Name, Bus_Confort_Type, Bus_start_time, Bus_end_time, Total_travel_time, Rating, Seat_availability, Price, Reach_date = WebDriverWait(self.driver, 25).until(
                    lambda driver: (
                        driver.find_elements(By.XPATH, "//div[@class='travels lh-24 f-bold d-color']"),
                        driver.find_elements(By.XPATH, "//div[@class='bus-type f-12 m-top-16 l-color evBus']"),
                        driver.find_elements(By.XPATH, "//div[@class='dp-time f-19 d-color f-bold']"),
                        driver.find_elements(By.XPATH, "//div[@class='bp-time f-19 d-color disp-Inline']"),
                        driver.find_elements(By.XPATH, "//div[@class='dur l-color lh-24']"),
                        driver.find_elements(By.XPATH, "//div[@class='rating-sec lh-24']//span"),
                        driver.find_elements(By.XPATH, "//div[@class='seat-left m-top-30']"),
                        driver.find_elements(By.XPATH, "//div[@class='fare d-block']"),
                        driver.find_elements(By.XPATH, "//div[@class='next-day-dp-lbl m-top-16']")
                    )
                )

                # Print the bus details to verify they are being scraped
                print(f"Scraped data for route: {name}")
                print("Bus travel Name:", [elem.text.strip() for elem in Bus_travel_Name if elem.text != ''])
                print("Bus Comfort Type:", [elem.text.strip() for elem in Bus_Confort_Type if elem.text != ''])
                print("Bus Start Time:", [elem.text.strip() for elem in Bus_start_time if elem.text != ''])
                print("Bus End Time:", [elem.text.strip() for elem in Bus_end_time if elem.text != ''])
                print("Total Travel Time:", [elem.text.strip() for elem in Total_travel_time if elem.text != ''])
                print("Rating:", [float(elem.text.strip()) for elem in Rating if elem.text != ''])
                print("Seat Availability:", [int(i.text.split()[0]) for i in Seat_availability if i.text != ''])
                print("Price:", [i.text[3:].strip() for i in Price if i.text[3:] != ''])
                print("Reach Date:", [elem.text.strip() for elem in Reach_date if elem.text != ''])
                print("\n")

                # Store scraped data for private buses
                self.Bus[name]["Private"]["Bus_Name"] = [elem.text.strip() for elem in Bus_travel_Name if elem.text != '']
                self.Bus[name]["Private"]["Bus_Type"] = [elem.text.strip() for elem in Bus_Confort_Type if elem.text != '']
                self.Bus[name]["Private"]["Departing_Time"] = [elem.text.strip() for elem in Bus_start_time if elem.text != '']
                self.Bus[name]["Private"]["Reaching_Time"] = [elem.text.strip() for elem in Bus_end_time if elem.text != '']
                self.Bus[name]["Private"]["Duration"] = [elem.text.strip() for elem in Total_travel_time if elem.text != '']
                self.Bus[name]["Private"]["Star_Rating"] = [float(elem.text.strip()) for elem in Rating if elem.text != '']
                self.Bus[name]["Private"]["Seat_availability"] = [int(i.text.split()[0]) for i in Seat_availability if i.text != '']
                self.Bus[name]["Private"]["Price"] = [i.text[3:].strip() for i in Price if i.text[3:] != '']
                self.Bus[name]["Private"]["Reach_date"] = [elem.text.strip() for elem in Reach_date if elem.text != '']

                # Click to switch to government buses
                try:
                    button = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='button']")))

                    # Scroll the button into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)  
                    self.driver.execute_script("arguments[0].click();", button)

                except ElementClickInterceptedException as e:
                    print(f"Error clicking the button to switch to government buses: {e}")

                # Smooth scroll before scraping government bus details
                smooth_scroll()

                # Scrape government bus details
                Bus_travel_Name, Bus_Confort_Type, Bus_start_time, Bus_end_time, Total_travel_time, Rating, Seat_availability, Price, Reach_date = WebDriverWait(self.driver, 25).until(
                    lambda driver: (
                        driver.find_elements(By.XPATH, "//div[@class='travels lh-24 f-bold d-color']"),
                        driver.find_elements(By.XPATH, "//div[@class='bus-type f-12 m-top-16 l-color evBus']"),
                        driver.find_elements(By.XPATH, "//div[@class='dp-time f-19 d-color f-bold']"),
                        driver.find_elements(By.XPATH, "//div[@class='bp-time f-19 d-color disp-Inline']"),
                        driver.find_elements(By.XPATH, "//div[@class='dur l-color lh-24']"),
                        driver.find_elements(By.XPATH, "//div[@class='rating-sec lh-24']//span"),
                        driver.find_elements(By.XPATH, "//div[@class='seat-left m-top-30']"),
                        driver.find_elements(By.XPATH, "//div[@class='fare d-block']"),
                        driver.find_elements(By.XPATH, "//div[@class='next-day-dp-lbl m-top-16']")
                    )
                )

                # Print the bus details to verify they are being scraped
                print(f"Scraped data for government buses on route: {name}")
                print("Bus travel Name:", [elem.text.strip() for elem in Bus_travel_Name if elem.text != ''])
                print("Bus Comfort Type:", [elem.text.strip() for elem in Bus_Confort_Type if elem.text != ''])
                print("Bus Start Time:", [elem.text.strip() for elem in Bus_start_time if elem.text != ''])
                print("Bus End Time:", [elem.text.strip() for elem in Bus_end_time if elem.text != ''])
                print("Total Travel Time:", [elem.text.strip() for elem in Total_travel_time if elem.text != ''])
                print("Rating:", [float(elem.text.strip()) for elem in Rating if elem.text != ''])
                print("Seat Availability:", [int(i.text.split()[0]) for i in Seat_availability if i.text != ''])
                print("Price:", [i.text[3:].strip() for i in Price if i.text[3:] != ''])
                print("Reach Date:", [elem.text.strip() for elem in Reach_date if elem.text != ''])
                print("\n")

                # Store scraped data for government buses
                self.Bus[name]["Government"]["Bus_Name"] = [elem.text.strip() for elem in Bus_travel_Name if elem.text != '']
                self.Bus[name]["Government"]["Bus_Type"] = [elem.text.strip() for elem in Bus_Confort_Type if elem.text != '']
                self.Bus[name]["Government"]["Departing_Time"] = [elem.text.strip() for elem in Bus_start_time if elem.text != '']
                self.Bus[name]["Government"]["Reaching_Time"] = [elem.text.strip() for elem in Bus_end_time if elem.text != '']
                self.Bus[name]["Government"]["Duration"] = [elem.text.strip() for elem in Total_travel_time if elem.text != '']
                self.Bus[name]["Government"]["Star_Rating"] = [float(elem.text.strip()) for elem in Rating if elem.text != '']
                self.Bus[name]["Government"]["Seat_availability"] = [int(i.text.split()[0]) for i in Seat_availability if i.text != '']
                self.Bus[name]["Government"]["Price"] = [i.text[3:].strip() for i in Price if i.text[3:] != '']
                self.Bus[name]["Government"]["Reach_date"] = [elem.text.strip() for elem in Reach_date if elem.text != '']

            except TimeoutException as e:
                print(f"Error fetching bus details for {name}: {e}")
        
        # Close the WebDriver
        self.driver.quit()

    def get_bus_data(self):
        """Return the scraped bus data."""
        return self.Bus

# Creating an object of Redbus
Buses = Redbus("//div[@class='rtcNameMain']/div[@class='rtcName' and text()='WBSTC']")

Value = Buses.get_bus_data()
