import imaplib
from config import CONFIG
from datetime import datetime, timedelta
import email
import os

today = datetime.now()
imap_host = "imap.gmail.com"
imap_port = 993
user = CONFIG["email"]
password = CONFIG["gpass"]

def fetch_arxiv_email(lookback):
	"""
	fetches all arxiv messages within a given lookback time (hours)
	for example, if arxiv sends out notices at ~10 PM EST and this should be ready by 9 AM in the morning, set a lookback time anywhere within 11-35 hours
	"""
	conn = imaplib.IMAP4_SSL(imap_host, imap_port)
	conn.login(user, password)
	conn.select("INBOX")
	
	lookback_time = today - timedelta(hours=lookback)
	date_format = lookback_time.strftime("%d-%b-%Y")
	status, data = conn.search(None, f"(FROM arxiv.org SINCE {date_format})")
	ids = data[0].split()
	
	messages = []
	for msg_id in ids:
		status, msg_data = conn.fetch(msg_id, "(RFC822)")
		raw_email = msg_data[0][1]
		msg = email.message_from_bytes(raw_email)
		body = get_plain_text_body(msg)
		if ("Your email address has been added" not in body) and ("To get a list of the valid subject classes"): #filter subscription emails
			messages.append(body)

	conn.logout()
	return messages

def get_plain_text_body(msg):
	if msg.is_multipart():
		for part in msg.walk():
			if part.get_content_type() == "text/plain":
				return part.get_payload(decode=True).decode(errors="replace")
	else:
		return msg.get_payload(decode=True).decode(errors="replace")
	return ""

	
