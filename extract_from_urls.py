from openai import OpenAI
import os
import json
import re

# Initialize the client with the API key
api_key = os.environ.get("PERPLEXITY_API_KEY")
if not api_key:
    print("API key is not set.")
    exit(1)

client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

company_urls=["https://www.palletpalmarketplace.com/", "https://www.simplelots.com/", "https://www.olabid.com/"]
# "https://www.directliquidation.com", "https://bluelots.com/", 

# Dictionary to hold the company data
company_info = {}

def fetch_info(company, question, key):
    liquidation_description = """
    A liquidation company is a business that purchases inventory from companies that are overstocked, closing down, or bankrupt. 
    They then resell these goods at significantly reduced prices, often through an online storefront. These companies are involved in the liquidation of assets across various sectors, including electronics, furniture, and apparel.
    """
    messages = [
        {"role": "system", "content": f"{liquidation_description} Now that you know about liquidations websites, extract data fields from the website: email, phone number, address, state, site name. Be precise and concise"},
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
            return response.choices[0].message.content  # Return the full response content directly
        else:
            return 'Not available'
    except Exception as e:
        print(f"An error occurred while fetching data for {company}: {e}")
        return 'Not available'

# Collect and process information for each company
for company_url in company_urls:
    website = fetch_info(company_url, f"Get the website url of {company_url}.", 'link')
    name = fetch_info(company_url, f"Extract the name of the site from {company_url}", 'name')
    email = fetch_info(company_url, f"Get me the email from the url {company_url}", 'email')
    state = fetch_info(company_url, f"Identify the state of the company through this url {company_url}", 'state')
    phone = fetch_info(company_url, f"Get me the phone number of {company_url} from any part of the website", 'phone')
    address = fetch_info(company_url, f"Analyze the website of {company_url} and determine the physical address from the contact page", 'address')

    company_info[company_url] = {
        'link': website,
        'name': name,
        'email': email,
        'state': state,
        'phone': phone,
        'address': address
    }

# Print cleaned up data
try:
    print(json.dumps(company_info, indent=4))
except TypeError as e:
    print(f"Error serializing to JSON: {e}")

