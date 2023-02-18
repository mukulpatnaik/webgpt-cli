# standard GPT-3 API call

import openai
import sys
import os

prompt = sys.argv[1]
openai.api_key = os.getenv("OPENAI_API_KEY")
r = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0.8, max_tokens=800)
response = r.choices[0]['text']

print('\n'+response.strip("\n")+'\n')