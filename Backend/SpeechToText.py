from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")

InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to English if not set

HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;
            }};

            recognition.onend = function() {{
                recognition.start();
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            recognition.stop();
        }}
    </script>
</body>
</html>'''

# Ensure the directory exists before writing the file
data_dir = os.path.join(os.getcwd(), "Data")
os.makedirs(data_dir, exist_ok=True)
html_path = os.path.join(data_dir, "Voice.html")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

temp_dir = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(temp_dir, exist_ok=True)

def SetAssistantStatus(Status):
    status_file = os.path.join(temp_dir, "Status.data")
    with open(status_file, "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "which", "why", "can you", "whom", "whose", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip(".?!") + "?"
    else:
        new_query = new_query.rstrip(".?!") + "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    translated_text = mt.translate(Text, "en", "auto")
    return translated_text.capitalize()

def SpeechRecognition():
    driver.get("file:///" + html_path)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            text_element = driver.find_element(By.ID, "output")
            if text_element.text:
                recognized_text = text_element.text
                driver.find_element(By.ID, "end").click()

                if "en" in InputLanguage.lower():
                    return QueryModifier(recognized_text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(recognized_text))
        except Exception:
            continue  # Prevent crash due to element not found

if __name__ == "__main__":
    while True:
        text = SpeechRecognition()
        print(text)
