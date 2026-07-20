import json
from pathlib import Path

config = Path(__file__).parent / "config.json"

def setup():
	config = {
		"Email": input("Please enter the email recieving the arXiv emails: "),
		"GPass": input("Please visit https://myaccount.google.com/apppasswords for the account recieving the arXiv emails and create a new app. Paste the password here: ).replace(" ", ""),
		"Browser": input("Please enter the exact application name (with capitalization and spaces) of the browser you want the abstracts to open in: "),
		"
