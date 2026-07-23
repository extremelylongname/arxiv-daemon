print("LOADED", flush=True)

import email_fetcher
import re
import json
import pandas as pd
from config import CONFIG
import os
from openai import OpenAI

print("IMPORTED", flush=True)
api_key = CONFIG["apikey"]

client = OpenAI(
    base_url=CONFIG["apiprovider"],
    api_key=CONFIG["apikey"],
)

with open('prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

json_catcher = re.compile(r"\\[(.*?)\\]")
abstract_catcher = re.compile(r"\\\\(.*?)\\\\\s*\(", re.DOTALL)
message = email_fetcher.fetch_arxiv_email(24)
tot = ''

if len(message) > 0:
	for email in message:
		tot += email

	paper_block = re.compile(r'-{10,}')


	ct = 0
	iterations = CONFIG["iterations"]
	batch_size = CONFIG["batch_size"]
	thresh = CONFIG["threshold"]
	error_thresh = 2
	abstracts = paper_block.split(tot)[5:-2]
	overall_scores = []

	print("SETUP VARIABLES", flush=True)
	print("----------", flush=True)

	valid_blocks = [block for block in abstracts if ("replaced with revised version" not in block) and ("Authors" in block)]

	for it in range(iterations):

		print(f"ITERATION {it}", flush=True)
		jsons = []
		abs_raw_text = []

		for start in range(0, len(valid_blocks), batch_size):
			batch = valid_blocks[start:min(start+batch_size, len(valid_blocks))]
			abstract_batch = "\n".join(batch)
			abs_raw_text += [abstract_catcher.search(b).group(1).strip() for b in batch]
			expected = len(batch)
			
			while True:
				try:
					response = client.chat.completions.create(model=CONFIG["model"],
											messages=[{"role": "user", "content":f"{prompt} \n  {abstract_batch}"}])
					message = response.choices[0].message.content
					match = json_catcher.search(message)
					if message.startswith("```"):
						message = message.split("\n", 1)[1]
						message = message.rsplit("```", 1)[0]
					scores = json.loads(message)

					if len(scores) != expected:
						print("EXCEPTION CAUGHT")
						raise Exception("Model response does not match number of abstracts in input")
					break
				except:
					continue
		
			jsons += scores
		
		print((len(jsons), len(abs_raw_text)))
		# print(f"FIRST: {jsons[0]}, LAST: {jsons[-1]}")
		# print(f"FIRST: {abs_raw_text[0]}, LAST: {abs_raw_text[-1]}")
		for i in range(len(jsons)):
			jsons[i]["abstract"] = abs_raw_text[i]
		print(f"FETCHED FEEDBACK", flush=True)
		overall_scores.append(pd.DataFrame(jsons))



	combined = pd.concat(overall_scores, ignore_index=True)
	combined = (combined.groupby("id", as_index=False).agg({"score": "sum", "reason": "first", "abstract": "first"}))
	combined.to_csv("combined.csv")
	print(combined['score'].value_counts())
else:
	print("NO EMAIL FOUND.", flush=True)

