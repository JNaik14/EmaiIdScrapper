import re
import requests
from urllib.parse import urlsplit,urlparse
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd 
from tqdm import tqdm

# http_proxy  =  "http://192.168.43.164:8080"
# proxyDict = { 
              # "http"  : http_proxy, 
              # "https" : http_proxy, 
            # }


#Your CSV File which must have a column with Title 'Website' and having valid website urls
file = pd.read_csv("physio.csv")

def GetEmailId(url):
    
    unscraped = deque([url])  
    scraped = set()

    #Main Loop
    while len(unscraped):
        url = unscraped.popleft()  
        scraped.add(url)


        #Splitting the URL for further use
        parts = urlsplit(url)
        base_url = f"{parts.scheme}://{parts.netloc}"
        if '/' in parts.path:
            path = url[:url.rfind('/')+1]
        else:
            path = url

        print("Crawling URL %s" % url)

        #Getting the WebPages
        try:
            response = requests.get(url)
        except Exception as e:
            print(e)
            continue

        #Getting Email Ids From the HTML File

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z0-9\.\-+_]+", response.text, re.I))

        #Only Saves a single Email ID 
        if len(new_emails):
            return list(new_emails)[0]

        #Getting any URLs in the Website
        #Its rare that you will file the main email id in the index page, hence the script the crawn the whole website
        
        soup = BeautifulSoup(response.text, 'lxml')

        for anchor in soup.find_all("a"):
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            else:
                link = ''

            if link.startswith('/'):
                link = base_url + link
            
            elif not link.startswith('http'):
                link = path + link

            if not link in unscraped and not link in scraped:
                unscraped.append(link)

EmailIDs = []
for url in tqdm(file['Website']):
    # Remove Empty and Error prone URLs
    try:
        requests.get(url)
        email = GetEmailId(url)
        print(f'URL - {url} : Email - {email}')
        EmailIDs.append(email)
    except:
        print("Url Not found or Malformed")
        EmailIDs.append("None")
        
file["Email IDs"] = EmailIDs
file.to_csv('FinalListWithEmails.csv', index=False)
