# webgpt is a command line interface tool that uses the GPT-3 API to generate summaries from the web and provides a link to the source

import re
import sys
import argparse
import openai
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import warnings
import os

# supress warnings
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Use GPT-3 with multi-shot prompting to generate summaries from the web.')
parser.add_argument('query', type=str, help='the query to generate text from')
parser.add_argument('-m', '--model', type=str, default='text-davinci-003', help='the GPT-3 model to use')
parser.add_argument('-t', '--temperature', type=float, default=0.8, help='the sampling temperature')
parser.add_argument('-max', '--max-tokens', type=int, default=800, help='the maximum number of tokens to generate')
parser.add_argument('-n', '--num-results', type=int, default=3, help='the number of results to return')

# Parse the arguments
args = parser.parse_args()

query = args.query

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
  key = os.getenv('SERPAPI_KEY')

  params = {
    "q": query,
    "hl": hl,
    "gl": gl,
    "api_key": key
  }

  search = GoogleSearch(params)
  results = search.get_dict()

  links = []
  print(results)
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
    r = openai.Completion.create(model=args.model, prompt=prompt, temperature=args.temperature, max_tokens=args.max_tokens)
    response = r.choices[0]['text']

    return response

with HiddenPrints():
    # This function combines the search, scrape and gpt functions
    def process(query):
    
        links = search(query)
        results = []

        for i in links[:args.num_results]:

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

    data = process(args.query)

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


output(args.query, data)