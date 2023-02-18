# webgpt is a command line interface tool that uses the GPT-3 API to generate summaries from the web and provides a link to the source

import re
import sys

import openai
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import warnings
import os

# supress warnings
warnings.filterwarnings("ignore")

query = sys.argv[1]

# Using this class to supress the output of the search function
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# This function searches google for the query and returns the top 3 links
def search(query):

  hl =  "en"
  gl = "us"
  key = ""

  params = {
    "q": query,
    "hl": hl,
    "gl": gl,
    "api_key": key
  }

  search = GoogleSearch(params)
  results = search.get_dict()

  links = []
  for i in results["organic_results"]:
      links.append(i['link'])
  
  return links

# This function scrapes the text from the link
def scrape(url):

    # url = "https://en.wikipedia.org/wiki/Coffee"

    r1 = requests.get(url)
    r1.status_code
    coverpage = r1.content
    soup = BeautifulSoup(coverpage, "lxml")
    content = soup.find("body").find_all('p')

    x = ''
    for i in content:
        x = x + i.getText().replace('\n', '')

    x = re.sub(r'==.*?==+', '', x)
    
    return x

# This function uses the GPT-3 API to generate a summary
def gpt(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    r = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0.2, max_tokens=500)
    response = r.choices[0]['text']

    return response

with HiddenPrints():
    # This function combines the search, scrape and gpt functions
    def process(query):
    
        links = search(query)
        results = []

        for i in links[:2]:

            txt = scrape(i)[:1000]
            if len(txt) < 500:
                continue

            prompt = """Given the following question:'"""+query+"""'

            Extract the text from the following content relevant to the question and summarize in detail:

            '"""+txt+"""'

            Extracted summarized content:"""

            a = {
                'query': query,
                'link': i,
                'text': txt,
                'summary': gpt(prompt).strip()
            }
            
            results.append(a)
        return results

    data = process(query)

# This function prints the results in a nice format
def output(query, data):
    print('')
    print('\033[1m' + 'Query:' + '\033[0m', "\x1B[3m" + query + "\x1B[0m")
    print('\033[1m' + 'Results: ' + '\033[0m')

    for i in data:
        print('')
        print('')
        # print('\033[1m' + '' + '\033[0m',)
        print(" - '"+i['summary'].strip()+"'")
        print('['+ '\033[1m' + 'source:' + '\033[0m', '\033[34m' + "\x1B[3m" + i['link'] + "\x1B[0m" + '\033[00m' +']')
        print('')


output(query, data)