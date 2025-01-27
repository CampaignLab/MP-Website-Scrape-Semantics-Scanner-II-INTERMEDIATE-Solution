#!/usr/bin/env python3


# DISCLAIMER: DISCLAIMER: The Application code scrpt and tool is intended to facilitate research, by authorised and approved parties, pursuant to the ideals of libertarian democracy in the UK, by Campaign Lab membership. Content subject-matter and results can be deemed sensitive and thus confidential. Therefore illicit and authorisation for any other use, outside these terms, is hereby not implied pursuant to requisite UK Data Protection legislation and the wider GDPR enactments within the EU.


# CODE REVISION: Ejimofor Nwoye, Newspeak House, London, England, @ 22/01/2025


import requests
from bs4 import BeautifulSoup
import re
import json
from elasticsearch import Elasticsearch
import os


os.system("clear")

# Function to scrape data from a URL
def scrape_mps(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch URL: {url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []

    if "theyworkforyou" in url:
        for link in soup.select(".mp .person a"):
            links.append(link['href'])
    elif "members.parliament.uk" in url:
        for link in soup.select(".card-title a"):
            links.append(link['href'])

    return links

# Function to extract policy interests, statements, and phrases
def extract_mp_data(mp_urls):
    mp_data = []

    for mp_url in mp_urls:
        try:
            response = requests.get(mp_url)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            # Regular expressions to extract relevant information
            policy_interests = re.findall(r"policy interest[s]?: (.*?)\\n", text, re.IGNORECASE)
            statements = re.findall(r"\"(.*?)\"", text)
            phrases = re.findall(r"\b(?:IPP|sentences|prison reform|justice system)\b", text, re.IGNORECASE)

            mp_data.append({
                "url": mp_url,
                "policy_interests": policy_interests,
                "statements": statements,
                "phrases": phrases
            })
        except Exception as e:
            print(f"Error processing {mp_url}: {e}")

    return mp_data

# Main execution
if __name__ == "__main__":
    # URLs to scrape
    urls = [
        "https://www.theyworkforyou.com/mps/",
        "https://members.parliament.uk/constituencies"
    ]

    all_mp_urls = []

    # Scrape MP URLs from both sources
    for url in urls:
        all_mp_urls.extend(scrape_mps(url))

    # Extract data for each MP
    mp_profiles = extract_mp_data(all_mp_urls)

    # Save data to JSON file
    with open("ukmpprofile.json", "w") as json_file:
        json.dump(mp_profiles, json_file, indent=4)

    print("Data saved to ukmpprofile.json")

    # Copy data to ELK stack
    es = Elasticsearch(["http://localhost:9200"])  # Adjust the host and port as needed

    for profile in mp_profiles:
        es.index(index="uk-mp-profiles", document=profile)

    print("Data uploaded to ELK stack.")
