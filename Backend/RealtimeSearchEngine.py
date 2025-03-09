from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))  
    Answer = f"The search result for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    data = "Use This Real-time Information if needed:\n" 
    current_date_time = datetime.datetime.now()
    data += f"Day: {current_date_time.strftime('%A')}\n"
    data += f"Date: {current_date_time.strftime('%d')}\n"
    data += f"Month: {current_date_time.strftime('%B')}\n"
    data += f"Year: {current_date_time.strftime('%Y')}\n" 
    data += f"Time: {current_date_time.strftime('%H')} hours, {current_date_time.strftime('%M')} minutes, {current_date_time.strftime('%S')} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    
    messages.append({"role": "user", "content": f"{prompt}"})
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )   
 
    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s", "")  
    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\ChatLog.json", "w") as f:  
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)  

if __name__ == "__main__":  
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))
