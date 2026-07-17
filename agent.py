import email_fetcher
import re

message = email_fetcher.fetch_arxiv_email(24)
tot = ''
for email in message:
	tot += email

paper_block = re.compile(r'-{10,}')

print(f"LENGTH: {len(paper_block.split(tot))}")

for block in paper_block.split(tot)[5:-2]:
	if "replaced with revised version" not in block:
		print(block)
		print("---------------- BLOCK SEPARATOR ----------------")
	
