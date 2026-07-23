import json
from pathlib import Path
import re
import os
import inquirer

config = Path(__file__).parent / "config.json"
email_re = re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$")

def email_validation(_, email):
    if not email_re.match(email):
        raise inquirer.errors.ValidationError("", reason="Invalid email.")
    return True

def gpass_validation(_, gpass):
	if len(gpass.replace(" ", "").strip()) != 16:
		raise inquirer.errors.ValidationError("", reason="Invalid password.")
	return True

def setup():

	confirm = [inquirer.Confirm("continue", message="This will change all your current configs and create a new one. Continue?", default=False)]

	if inquirer.prompt(confirm)["continue"]:

		questions = [
		inquirer.Text("email", message="Please enter the email recieving the arXiv emails", validate=email_validation),
		inquirer.Password("gpass", message="Please visit https://myaccount.google.com/apppasswords for the account recieving the arXiv emails and create a new app. Paste the password here",
						validate=gpass_validation),
		inquirer.List(
		"apiprovider",
		message="Select an OpenAI API compatible model provider",
		choices=[("Anyscale Endpoints", "https://api.endpoints.anyscale.com/v1"),
				("Alibaba Qwen (DashScope)", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
				("Azure OpenAI", "https://{your-resource}.openai.azure.com"),
				("Cerebras", "https://api.cerebras.ai/v1"),
				("Cohere", "https://api.cohere.ai/compatibility/v1"),
				("DeepSeek", "https://api.deepseek.com/v1"),
				("Fireworks AI", "https://api.fireworks.ai/inference/v1"),
				("FreeInference", "https://freeinference.org/v1"),
				("Groq", "https://api.groq.com/openai/v1"),
				("LM Studio (local)", "http://localhost:1234/v1"),
				("MiniMax", "https://api.minimax.chat/v1"),
				("Mistral AI", "https://api.mistral.ai/v1"),
				("Moonshot AI (Kimi)", "https://api.moonshot.ai/v1"),
				("OpenRouter", "https://openrouter.ai/api/v1"),
				("Ollama (local)", "http://localhost:11434/v1"),
				("OpenAI", "https://api.openai.com/v1"),
				("Perplexity", "https://api.perplexity.ai"),
				("Reka", "https://api.reka.ai/v1"),
				("Together AI", "https://api.together.xyz/v1"),
				("vLLM (self-hosted)", "http://localhost:8000/v1"),
				("xAI (Grok)", "https://api.x.ai/v1"),
				("Z.ai (GLM)", "https://open.bigmodel.cn/api/paas/v4"),]),
		inquirer.Password("apikey", message="Please enter the api key for your model"),
		inquirer.Text("model", message="Please enter your model of choice exactly as in your API documentation (e.g. minimax-m2.7)"),
		inquirer.Text("iterations", message="How many times do you want to evaluate the daily papers (reccomended: 2-5)? More evaluations means more robust scores but higher time and API cost"),
		inquirer.Text("batch_size", message="How large should each batch of papers sent to the LLM be (reccomended: 10-30)? Larger batch sizes means less robust scores but lower time and API cost"),
		inquirer.Text("prompt", message="Please visit the repo and follow the directions to create your evaluation prompt. Enter the path"),
		inquirer.Text("threshold", message="Based on your prompt, please enter the threshhold score above which papers will be shown"),
		inquirer.Text("time", message="Please enter (in hours after midnight local time) when the fetch should run, fetching any emails in the previous 24 hours"),
		inquirer.Text("pypath", message="Please enter your Python path")
		]


		answers = inquirer.prompt(questions)

		answers["threshold"] = float(answers["threshold"])
		answers["iterations"] = int(answers["iterations"])
		answers["batch_size"] = int(answers["batch_size"])
		answers["time"] = float(answers["time"])

		print(answers)

		with open("config.json", "w") as f:
			json.dump(answers, f, indent=4)

		launch_script = f"""
		<?xml version="1.0" encoding="UTF-8"?>
		<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
		<plist version="1.0">
		<dict>

			<key>Label</key>
			<string>com.arxivfetch.daemon.plist</string>

			<key>RunAtLoad</key>
			<true/>

			<key>StartCalendarInterval</key>
			<dict>
			<key>Hour</key>
				<integer>{int(answers["time"])}</integer>
			<key>Minute</key>
				<integer>{int((answers["time"] - int(answers["time"]))*60)}</integer>
			</dict>

			<key>StandardErrorPath</key>
			<string>{os.path.join(Path(__file__).resolve().parent, "stderr.log")}</string>

			<key>StandardOutPath</key>
			<string>{os.path.join(Path(__file__).resolve().parent, "stdout.log")}</string>

			<key>EnvironmentVariables</key>
			<dict>
			<key>PATH</key>
			<string><![CDATA[/usr/local/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin]]></string>
			</dict>

			<key>WorkingDirectory</key>
			<string>{os.path.join(Path(__file__).resolve().parent)}</string>

			<key>ProgramArguments</key>
			<array>
			<string>{answers["pypath"]}</string>
			<string>agent.py</string>
			</array>

		</dict>
		</plist>
		"""

	with open(os.path.join(Path.home(), "/Library/LaunchAgents/com.arxivfetch.daemon.plist "), "w") as f:
		f.write(launch_script)

if __name__ == "__main__":
	setup()




	


