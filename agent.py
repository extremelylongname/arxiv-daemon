import email_fetcher
import re
import json
import time
import subprocess
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.environ["ARXIV_API_KEY"]

client = OpenAI(
    base_url="https://freeinference.org/v1",
    api_key=api_key,
)

with open('prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

json_catcher = re.compile(r"\\[(.*?)\\]")
message = email_fetcher.fetch_arxiv_email(24)
tot = ''
for email in message:
	tot += email

paper_block = re.compile(r'-{10,}')

print(f"LENGTH: {len(paper_block.split(tot))}")

ct = 0
batch_size = 10
thresh = 8
abstract_batch = ''
abstracts = paper_block.split(tot)[5:-2]

jsons = []

for block in abstracts:
	if ("replaced with revised version" not in block) and ("Authors" in block):
		ct += 1
		abstract_batch += '\n' + block
	if (ct == batch_size) or (block == abstracts[-3]): 
		response = client.chat.completions.create(model="deepseek-v4-flash",
								messages=[{"role": "user", "content":f"{prompt} \n  {abstract_batch}"}])
		message = response.choices[0].message.content
		match = json_catcher.search(message)
		if message.startswith("```"):
			message = message.split("\n", 1)[1]
			message = message.rsplit("```", 1)[0]

		scores = json.loads(message)
		jsons += scores
		abstract_batch = ''
		ct = 0

scores = pd.DataFrame(jsons)
print(scores['score'].value_counts())
scores.sort_values(by="score", inplace=True, ascending=False)
best_articles = scores[scores['score'] > thresh]
print(len(best_articles))
urls = ["https:///arxiv.org/abs/" + id for id in best_articles["id"]]

subprocess.Popen(
    ["open", "-na", "Brave Browser", "--args", "--new-window"] + urls)

