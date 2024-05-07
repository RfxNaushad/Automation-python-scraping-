from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import random
import csv

STATE_SHORT_CODES = [
    "ca", "ny", "al", "ak", "az", "ar", "co", "ct", "de", "fl", 
    "ga", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", 
    "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", 
    "nj", "nm", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", 
    "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"
]


QUERY_PARAMETERS = [
    "liquidation", "overstock", "discount", "auction", "liquidation stores", 
    "bin stores", "overstock stores", "discount shopping", "discount stores", 
    "pallet liquidation", "discount auction", "overstock auction"
]



def get_data_for_state(driver, state_code, query_param):
    companies = []
    for page_number in range(1, 4):  # Scraping the first 3 pages
        url = f"https://opencorporates.com/companies/us_{state_code}?action=search_companies&commit=Go&controller=searches&inactive=false&order=&q={query_param}&type=companies&utf8=%E2%9C%93&page={page_number}"
        driver.get(url)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "results"))
            )
            rows = driver.find_elements(By.CSS_SELECTOR, "li.company.active")
            for row in rows:
                try:
                    company_name = row.find_element(By.CLASS_NAME, "company_search_result").text
                    href_value = row.find_element(By.CLASS_NAME, "company_search_result").get_attribute("href")
                    companies.append((company_name, href_value))
                except NoSuchElementException:
                    print(f"Could not find required elements in row on page {page_number}")
                    continue
        except TimeoutException:
            print(f"Timeout occurred while waiting for search results on page {page_number}")
            break
        except WebDriverException as e:
            print(f"WebDriverException on page {page_number}: {e}")
            break
        
        time.sleep(random.uniform(5, 11))  # wait for a random time before the next request

    return companies

def scrape_additional_data(driver, companies):
    additional_data = []
    for company_name, href_value in companies:
        driver.get(href_value)
        time.sleep(random.uniform(5, 11))  # Wait for the page to load
        
        try:
            jurisdiction = driver.find_element(By.CLASS_NAME, "jurisdiction").text
            registered_address = driver.find_element(By.CLASS_NAME, "registered_address").text
            additional_data.append((company_name, href_value, jurisdiction, registered_address))
        except NoSuchElementException:
            print(f"Could not extract additional data for {company_name}")
            continue

    return additional_data

def main():
    options = Options()
    options.headless = True
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    all_companies = []
    for state_code in STATE_SHORT_CODES:
        for query_param in QUERY_PARAMETERS:
            companies = get_data_for_state(driver, state_code, query_param)
            additional_data = scrape_additional_data(driver, companies)
            all_companies.extend(additional_data)  # Extend with additional data directly
            
            time.sleep(5)
    driver.quit()

    # Save the results to a CSV file
    with open("scraped_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "opencorporates_url", "state", "address"])  # Write CSV header
        writer.writerows(all_companies)

    print("Scraping finished and data saved to scraped_data.csv")
    # print(all_companies)

if __name__ == "__main__":
    main()
