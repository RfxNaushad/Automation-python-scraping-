from pymongo import MongoClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import csv
import os
 
# Load the environment variables
load_dotenv()
mongo_url = os.getenv("TEST_DB")
client = MongoClient(mongo_url)
db = client["us_liquidation_list_db"]  # Create/use the database named "us_liquidation_list_db"
collection = db["companies_data"]    # Create/use the collection named "companies_data"
 
# Constants
STATE_SHORT_CODES = [
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga",
    "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md",
    "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
    "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc",
    "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy",
    "dc", "pr"
]
 
QUERY_PARAMETERS = [
    "liquidation", "overstock", "discount", "auction", "liquidation+stores",
    "bin+stores", "overstock+stores", "discount+shopping", "discount+stores",
    "pallet+liquidation", "discount+auction", "overstock+auction"
]
 
API_KEY = os.getenv("ZENROWS_API_KEY")
PROXY = f"http://{API_KEY}:js_render=true&premium_proxy=true&proxy_country=us@proxy.zenrows.com:8001"
 
def fetch_data(state_code, query_param, page_number):
    url = f"https://opencorporates.com/companies/us_{state_code}?action=search_companies&commit=Go&controller=searches&inactive=false&order=&q={query_param}&type=companies&utf8=%E2%9C%93&page={page_number}"
    proxies = {"http": PROXY, "https": PROXY}
    response = requests.get(url, proxies=proxies, verify=False)
    return response.text
 
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = soup.find_all('li', class_='search-result')
    companies = []
    for result in results:
        company_name = result.find('a', class_='company_search_result').text
        link = result.find('a', class_='company_search_result').get('href')
        href_value = "https://opencorporates.com"+link
        companies.append((company_name, href_value))
    return companies
 
def scrape_additional_data(companies):
    proxies = {"http": PROXY, "https": PROXY}
    additional_data = []
    for company_name, href_value in companies:
        response = requests.get(href_value, proxies=proxies, verify=False)
 
        jurisdiction = "Not Available"
        address = "Not Available"
 
        soup = BeautifulSoup(response.text, 'html.parser')
 
        try:
            jurisdiction = soup.find(class_='jurisdiction_filter').text
        except AttributeError:
            print(f"Could not find jurisdiction for {company_name}")
 
        try:
            address = soup.find(class_='registered_address').text
        except AttributeError:
            print(f"Could not find registered address for {company_name}")
 
        additional_data.append((company_name, href_value, jurisdiction, address))
 
    return additional_data
 
def save_to_mongodb(companies):
    if not companies:
        print("No data to save to MongoDB")
        return
 
    documents = [{"name": company[0], "opencorporates_url": company[1], "state": company[2], "address": company[3]} for company in companies]
    try:
        collection.insert_many(documents)
        print(f"Successfully inserted {len(documents)} documents into MongoDB.")
    except Exception as e:
        print(f"Error inserting documents into MongoDB: {e}")
 
def main():
    all_companies = []
    for state_code in STATE_SHORT_CODES:
        for query_param in QUERY_PARAMETERS:
            for page_number in range(1, 2):  # First 3 pages
                html_content = fetch_data(state_code, query_param, page_number)
                companies = parse_html(html_content)
                additional_data = scrape_additional_data(companies)
                all_companies.extend(additional_data)
 
    # Save the results in the MongoDB       
    save_to_mongodb(all_companies)
 
    # Save the results to a CSV file
    with open("scraped_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "opencorporates_url", "state", "address"])  # Write CSV header
        writer.writerows(all_companies)
 
    print("Scraping finished and data saved to MongoDB and scraped_data.csv")
    # print(all_companies)
 
if __name__ == "__main__":
    main()