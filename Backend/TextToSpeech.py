import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-JennyNeural")  # Default voice

# Ensure the Data directory exists
data_dir = "Data"
os.makedirs(data_dir, exist_ok=True)

async def TextToAudioFile(text) -> None:
    """Convert text to speech and save it as an audio file."""
    file_path = os.path.join(data_dir, "speech.mp3")
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def run_async(coro):
    """Ensures async function is properly executed once per runtime."""
    try:
        asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
        loop.close()

def TTS(Text, func=lambda r=None: True):
    """Plays the generated speech audio file and ensures smooth execution."""
    try:
        run_async(TextToAudioFile(Text))

        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(data_dir, "speech.mp3"))
        pygame.mixer.music.play()

        start_time = pygame.time.get_ticks()  # Get start time in milliseconds
        timeout_ms = 10000  # 10 seconds timeout

        while pygame.mixer.music.get_busy():
            if func() == False or (pygame.time.get_ticks() - start_time) > timeout_ms:
                break
            pygame.time.Clock().tick(10)  # Smooth processing

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in cleanup: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    """Splits text intelligently and decides whether to print remaining text."""
    sentences = Text.split(".")  # Avoid redundant splits

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(sentences) > 4 and len(Text) >= 250:
        TTS(". ".join(sentences[:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))
