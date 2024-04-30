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

company_urls=["https://www.palletpalmarketplace.com/", "https://www.directliquidation.com", "https://bluelots.com/"]
# "https://www.simplelots.com/", "https://www.olabid.com/" 

# Dictionary to hold the company data
company_info = {}

def parse_info(response, key):
    """
    Extracts the specific part of the response based on key.
    """
    match = None
    if key == 'link':
        match = re.search(r"(https?://\S+|www\.\S+)", response)
    elif key == 'name':
        pattern = r"(?<=is\s)(?:\"([^\"]+)\"|([A-Z][\w\s-]*))"
        match = re.search(pattern, response)
    elif key == 'email':
        match = re.search(r"(\S+@\S+\.\S+)", response)
    elif key == 'state':
        pattern = r"""\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|Northern California|Southern California|Central California|Upstate New York|Western New York)\b"""
        match = re.search(pattern, response)
    elif key == 'phone':
        match = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", response)
    elif key == 'address':
        pattern = r"(?<=is\s)(\d+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s[A-Z][a-z]+(?:\s[A-Z]{2})?,\s\d{5})"
        # pattern = r"(?:is\s+)?(\d+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\s(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)),\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s[A-Z][a-z]+(?:\s[A-Z]{2})?,\s\d{5})"
        match = re.search(pattern, response)
    return match.group(1) if match else 'Not available'

def fetch_info(company, question, key):
    liquidation_description = """
    A liquidation company is a business that purchases inventory from companies that are overstocked, closing down, or bankrupt. 
    They then resell these goods at significantly reduced prices, often through an online storefront. These companies are involved in the liquidation of assets across various sectors, including electronics, furniture, and apparel.
    """
    messages = [
        {"role": "system", "content": f"{liquidation_description} Now that you know about liquidation websites, extract data fields from the website: email, phone number, address, state, site name. Be precise and concise"},
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat.completions.create(
            model="sonar-medium-online",
            messages=messages,
            temperature=0.1,
            max_tokens=200  # Adjusted to allow for more detailed responses
        )
        if response.choices and response.choices[0].message:
            response_text = response.choices[0].message.content
            # Directly parse the information here using parse_info
            return parse_info(response_text, key)
        else:
            return 'Not available'
    except Exception as e:
        print(f"An error occurred while fetching data for {company}: {e}")
        return 'Not available'

# def fetch_info(company, question, key):
#     liquidation_description = """
#     A liquidation company is a business that purchases inventory from companies that are overstocked, closing down, or bankrupt. 
#     They then resell these goods at significantly reduced prices, often through an online storefront. These companies are involved in the liquidation of assets across various sectors, including electronics, furniture, and apparel.
#     """
#     messages = [
#         {"role": "system", "content": f"{liquidation_description} Now that you know about liquidations websites, extract data fields from the website: email, phone number, address, state, site name. Be precise and concise"},
#         {"role": "user", "content": question}
#     ]

#     try:
#         response = client.chat.completions.create(
#             model="sonar-medium-online",
#             messages=messages,
#             temperature=0.1,
#             max_tokens=50
#         )
#         if response.choices and response.choices[0].message:
#             return response.choices[0].message.content  # Return the full response content directly
#         else:
#             return 'Not available'
#     except Exception as e:
#         print(f"An error occurred while fetching data for {company}: {e}")
#         return 'Not available'

# Collect and process information for each company
for company_url in company_urls:
    website = fetch_info(company_url, f"Get the website url of {company_url}.", 'link')
    name = fetch_info(company_url, f"Extract the name of the site from the title or footnotes of the website - {company_url}", 'name')
    email = fetch_info(company_url, f"Get me the email through this url {company_url}. Find the email address from homepage, footer or contact page", 'email')
    state = fetch_info(company_url, f"In which state does this company belongs in USA through this url {company_url}", 'state')
    phone = fetch_info(company_url, f"Get me the phone number from this url {company_url}. Open it and find me.", 'phone')
    address = fetch_info(company_url, f"Analyze the website of {company_url} and determine the physical address from the contact page", 'address')

    # website = re.search(r'https?://[^\s]+', website).group()
    # email = re.search(r"(\S+@\S+\.\S+)", email).group()
    # phone = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", phone).group()

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

