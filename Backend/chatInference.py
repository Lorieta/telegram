import re
from ollama import AsyncClient
import asyncio
import json
import sys
import os

# --- Constants ---
# System prompt for the emotional analysis AI
SYSTEM_PROMPT = """
You are an emotional analysis assistant, skilled at discerning the emotional undertones in any input provided to you. Your expertise lies in evaluating text based on 8 fundamental emotions: joy, acceptance, fear, surprise, sadness, disgust, anger, and anticipation.

Instructions: You will receive a statement or question as input.

Your task is to analyze the emotional content and assign scores to each of the 8 emotions.

Scores range from 1 (lowest intensity) to 10 (highest intensity), where a higher score indicates a stronger association with the corresponding emotion.

Provide a clear and concise reason for each score.

Always present your analysis as a valid Python list in the following format, do not forget anything:

[ {"analysis": , "dim": "joy", "score": }, {"analysis": , "dim": "acceptance", "score": }, {"analysis": , "dim": "fear", "score": }, {"analysis": , "dim": "surprise", "score": }, {"analysis": , "dim": "sadness", "score": }, {"analysis": , "dim": "disgust", "score": }, {"analysis": "This text indicates a positive outlook towards a future event.", "dim": "anticipation", "score": 7}, {"analysis": , "dim": "anger", "score": } ] Rules Use each of the 8 emotions only once in the response.

Ensure that the reasons provided for the scores are logical, concise, and intuitive. Make the analysis short, and summarized
"""

# Define the 8 fundamental emotions
EMOTIONS = ["joy", "acceptance", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"]
DEFAULT_MODEL = "gemma3:4b" # Changed to a more common model name, adjust if needed

# --- Utility Functions ---
def extract_json_list(text: str) -> str | None:
  
    # Regex to find a JSON list: starts with '[', ends with ']', contains at least one '{...}' object
    match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

# --- Core Logic ---
async def analyze_emotion(prompt: str, model: str = DEFAULT_MODEL) -> list[float] | None:

    print(f"Sending prompt to LLM: '{prompt[:70]}...'") # Log beginning of prompt for brevity

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': prompt}
    ]

    try:
        response = await AsyncClient().chat(model=model, messages=messages)
        content = response.message.content
        print("Raw LLM output:\n", content)

        json_str = extract_json_list(content)
        if not json_str:
            print("Error: No valid JSON list found in LLM output.")
            return None

        emotion_data = json.loads(json_str)
        print("Parsed emotion data:\n", json.dumps(emotion_data, indent=2)) # Pretty print JSON

        # Initialize embedding with default neutral scores
        emotion_embedding = [0.0] * len(EMOTIONS)
        found_emotions = set()

        for item in emotion_data:
            dim = item.get("dim")
            score = item.get("score")

            if dim and isinstance(dim, str) and dim in EMOTIONS:
                if dim in found_emotions:
                    print(f"Warning: Duplicate entry for emotion '{dim}' found in LLM output. Using the first one.")
                    continue
                try:
                    # Ensure score is a float and within 1-10 range
                    score_float = float(score)
                    if not (1 <= score_float <= 10):
                        print(f"Warning: Score for '{dim}' ({score_float}) is out of expected range (1-10).")
                        score_float = max(1.0, min(10.0, score_float)) # Clamp the score
                    emotion_embedding[EMOTIONS.index(dim)] = score_float
                    found_emotions.add(dim)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid score type for '{dim}'. Expected a number, got '{score}'.")
            else:
                print(f"Warning: Unrecognized or missing 'dim' for an item: {item}")

        # Check if all 8 emotions were included in the LLM's response
        if len(found_emotions) < len(EMOTIONS):
            missing_emotions = set(EMOTIONS) - found_emotions
            print(f"Warning: LLM response did not include all 8 emotions. Missing: {', '.join(missing_emotions)}")

        print("Final emotion embedding:", emotion_embedding)
        return emotion_embedding

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from LLM output: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during emotion analysis: {e}")
        return None

async def analyze_json_file(json_path: str) -> list[dict] | None:
  
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at '{json_path}'")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{json_path}': {e}")
        return None
    except Exception as e:
        print(f"Error reading file '{json_path}': {e}")
        return None

    texts = []
    # Smartly handle various JSON structures for messages
    if isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
        # Case: root dict with "messages" list-of-dicts
        texts = [m["text"] for m in data["messages"] if isinstance(m, dict) and "text" in m]
    elif isinstance(data, list):
        if all(isinstance(obj, dict) and "text" in obj for obj in data):
            # Case: root list of dicts with "text" key
            texts = [obj["text"] for obj in data]
        elif all(isinstance(obj, str) for obj in data):
            # Case: root list of strings
            texts = data
        else:
            print(f"Warning: JSON file '{json_path}' contains a list with unrecognized object types. "
                  "Expected list of strings or dicts with 'text' key.")
            return None
    else:
        print(f"Error: Unrecognized JSON structure in '{json_path}'. "
              "Expected a list of messages or a dictionary with a 'messages' array.")
        return None

    if not texts:
        print(f"No messages found to analyze in '{json_path}'.")
        return []

    results = []
    for i, msg in enumerate(texts):
        print(f"\n--- Analyzing Message {i+1}/{len(texts)} ---")
        print(f"Message: {msg}")
        embedding = await analyze_emotion(msg)
        results.append({'text': msg, 'embedding': embedding})
        # Optionally, add a small delay to avoid rate limiting if processing many messages
        # await asyncio.sleep(0.5)
    return results

# --- Main Execution ---
async def textExtraction():
 
    json_file_path = r"C:\Users\John Carlo\telegram\Backend\saved_messages\reign.json"
   

    print(f"Automatically analyzing JSON file: {json_file_path}")
    analysis_results = await analyze_json_file(json_file_path)

    if analysis_results:
        print("\n--- All Analysis Results ---")
        for res in analysis_results:
            print(f"Text: '{res['text']}'\nEmbedding: {res['embedding']}\n")
    else:
        print("No analysis results or an error occurred during file analysis.")

if __name__ == "__main__":
    asyncio.run(textExtraction())