import os
import json
import re
from openai import OpenAI

# Initialize the client with the API key
def initialize_client():
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("API key is not set.")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

def parse_info(response, key):
    if key == 'link':
        match = re.search(r"(https?://\S+|www\.\S+)", response)
    elif key == 'site_name':
        pattern = r"(?<=is\s)(?:\"([^\"]+)\"|([A-Z][\w\s-]*))"
        match = re.search(pattern, response)
    elif key == 'email':
        match = re.search(r"(\S+@\S+\.\S+)", response)
    elif key == 'phone':
        match = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", response)
    return match.group(1) if match else 'Not available'

def fetch_info(client, company, question, key):
    liquidation_description = """
    A liquidation company is a business that purchases inventory from companies that are overstocked, closing down, or bankrupt.
    They then resell these goods at significantly reduced prices, often through an online storefront. These companies are involved in the liquidation of assets across various sectors, including electronics, furniture, and apparel.
    """
    messages = [
        {"role": "system", "content": f"{liquidation_description} Now that you know about liquidation websites, extract data fields from the website: link, website name, email, phone number. Be precise and concise"},
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat.completions.create(
            model="sonar-medium-online",
            messages=messages,
            temperature=0.1,
            max_tokens=50
        )
        if response.choices and response.choices[0].message:
            return parse_info(response.choices[0].message.content, key)
        else:
            return 'Not available'
    except Exception as e:
        print(f"An error occurred while fetching data for {company}: {e}")
        return 'Not available'

def collect_company_info(client):
    # companies = ["A&R Appliance and Liquidation, LLC", "AHM Liquidation Inc.", "AK Liquidation LLC", "Alabama Liquidation & Collection Agency, Inc.", "Alabama Liquidation, LLC", "Alex Liquidation Deals LLC", "At Home Estate Sales & Liquidation, LLC", "B & C Liquidation LLC", "B & Z Liquidation LLC", "AAW Liquidation Inc"]
    companies=["Black River Estates and Liquidation Services LLC", "CEM Liquidation, Inc", "B & C Liquidation LLC", "B & Z Liquidation LLC", "AAW Liquidation Inc"]
    # companies=["AAW Liquidation Inc"]
    company_info = {}
    
    for company in companies:
        website = fetch_info(client, company, f"Get the website of {company} searching in google.", 'link')
        site_name = fetch_info(client, company, f"Get the site name of the website of {company}", 'site_name')
        email = fetch_info(client, company, f"Get the email of {company} from their contact page", 'email')
        phone = fetch_info(client, company, f"Get the phone number of {company} from their contact page or footer or homepage.", 'phone')

        company_info[company] = {
            'link': website,
            'site_name': site_name,
            'email': email,
            'phone': phone
        }
    return company_info

if __name__ == "__main__":
    client = initialize_client()
    company_info = collect_company_info(client)
    try:
        print(json.dumps(company_info, indent=4))
    except TypeError as e:
        print(f"Error serializing to JSON: {e}")
