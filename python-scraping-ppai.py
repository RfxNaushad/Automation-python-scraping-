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

# companies = ["A&R Appliance and Liquidation, LLC", "AHM Liquidation Inc.", "AK Liquidation LLC", "Alabama Liquidation & Collection Agency, Inc.", "Alabama Liquidation, LLC", "Alex Liquidation Deals LLC", "At Home Estate Sales & Liquidation, LLC", "B & C Liquidation LLC", "B & Z Liquidation LLC", "AAW Liquidation Inc"]
companies=["Black River Estates and Liquidation Services LLC", "CEM Liquidation, Inc", "B & C Liquidation LLC", "B & Z Liquidation LLC", "AAW Liquidation Inc"]
# companies=["AAW Liquidation Inc"]

# Dictionary to hold the company data
company_info = {}

# def fetch_info(company, question):
#     messages = [
#         {"role": "system", "content": "Be precise and concise"},
#         {"role": "user", "content": question}
#     ]

#     try:
#         response = client.chat.completions.create(
#             model="sonar-medium-online",
#             messages=messages,
#             temperature=0.1,  # Lower temperature for more deterministic output
#             max_tokens=50     # Limit the number of tokens to keep answers concise
#         )
#         # Access the completion's content directly through the response object's methods or properties
#         if response.choices and response.choices[0].message:
#             answer = response.choices[0].message.content  # Access using property if available
#         else:
#             answer = None
#         return answer
#     except Exception as e:
#         print(f"An error occurred while fetching data for {company}: {e}")
#         return None

# # Assuming fetch_info and company_info setup are correct
# for company in companies:
#     website = fetch_info(company, f"Get the website of {company} searching in google. It may not be the same as the company name, so be precised. Make it very short answer.") or 'Not available'
#     site_name = fetch_info(company, f"Get the site name of the website of {company}. Make it very short answer.") or 'Not available'
#     email = fetch_info(company, f"Get the email of {company} from their contact page. Make it very short answer.") or 'Not available'
#     phone = fetch_info(company, f"Get the phone number of {company} from their contact page and footer. Make it very short answer.") or 'Not available'

#     company_info[company] = {
#         'link': website,
#         'site_name': site_name,
#         'email': email,
#         'phone': phone
#     }

# try:
#     print(json.dumps(company_info, indent=4))
# except TypeError as e:
#     print(f"Error serializing to JSON: {e}")




def parse_info(response, key):
    """
    Extracts the specific part of the response based on key.
    """
    if key == 'link' or key == 'site_name':
        match = re.search(r"(https?://\S+|www\.\S+)", response)
    elif key == 'email':
        match = re.search(r"(\S+@\S+\.\S+)", response)
    elif key == 'phone':
        match = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", response)
    return match.group(1) if match else 'Not available'

def fetch_info(company, question, key):
    messages = [
        {"role": "system", "content": "Be precise and concise"},
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

# Collect and process information for each company
for company in companies:
    website = fetch_info(company, f"Get the website of {company} searching in google.", 'link')
    site_name = fetch_info(company, f"Get the site name of the website of {company}", 'site_name')
    email = fetch_info(company, f"Get the email of {company} from their contact page", 'email')
    phone = fetch_info(company, f"Get the phone number of {company} from their contact page or footer or homepage.", 'phone')

    company_info[company] = {
        'link': website,
        'site_name': site_name,
        'email': email,
        'phone': phone
    }

# Print cleaned up data
try:
    print(json.dumps(company_info, indent=4))
except TypeError as e:
    print(f"Error serializing to JSON: {e}")
