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

        # Get the bus route links and names
        Bus_Route_link = [i.get_attribute('href') for i in self.driver.find_elements(By.XPATH, "//div[@class='route_details']//a")]
        Bus_Route_name = [i.text for i in self.driver.find_elements(By.XPATH, "//a[@class='route']")]

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

        for i in range(1, 6):
            if i > 1:
                # Refresh bus route links and names for subsequent pages
                Bus_Route_link = [i.get_attribute('href') for i in self.driver.find_elements(By.XPATH, "//div[@class='route_details']//a")]
                Bus_Route_name = [i.text for i in self.driver.find_elements(By.XPATH, "//a[@class='route']")]

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

            # Navigate back and handle pagination
            try:
                time.sleep(7)
                self.driver.get('https://www.redbus.in/')
                time.sleep(5)
                
                # Scroll horizontally to bring the element into view
                target_element = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, self.Xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
                time.sleep(2)
                
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.Xpath))).click()
                time.sleep(10)

                xpath = f"//div[12]/div[{i + 1}]"

                # Check if the element exists
                if not self.driver.find_elements(By.XPATH, xpath):
                    print(f"Page {i + 1} does not exist. Exiting loop.")
                    break

                # Wait for the element to be present and visible
                element = WebDriverWait(self.driver, 25).until(EC.visibility_of_element_located((By.XPATH, xpath)))

                # Scroll the element into view before clicking
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)  

                # Attempt to click the element
                element.click()

            except ElementNotInteractableException as e:
                print(f"Error navigating to page {i + 1}: {e}")
            except ElementClickInterceptedException as e:
                print(f"Click intercepted when trying to navigate to page {i + 1}: {e}")
            except TimeoutException or NoSuchElementException as e:
                print(f"Page is over {i + 1}: {e}")

        # Close the WebDriver
        self.driver.quit()

    def get_bus_data(self):
        """Return the scraped bus data."""
        return self.Bus

# Creating an instance of Redbus
Buses = Redbus("//div[@class='rtcNameMain']/div[@class='rtcName' and text()='JKSRTC']")

# Accessing the values inside the instance
Value = Buses.get_bus_data()
