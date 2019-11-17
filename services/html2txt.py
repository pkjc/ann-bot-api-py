import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup

def html2txt(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html,features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

import requests

url = 'http://0.0.0.0:5000/reply'
myobj = {
  "queryResult": {
    "queryText": "how many patients are between the ages 50 to 70",
    "parameters": {
      "color": ""
    },
    "allRequiredParamsPresent": True,
    "fulfillmentMessages": [
      {
        "text": {
          "text": [
            ""
          ]
        }
      }
    ],
    "intent": {
      "name": "projects/quotebot-18fe7/agent/intents/264c9988-9235-447a-a7dd-9d6085b6ea05",
      "displayName": "patient.data"
    },
    "intentDetectionConfidence": 1.0,
    "languageCode": "en"
  }
}

x = requests.post(url, json = myobj)

print(x.text)