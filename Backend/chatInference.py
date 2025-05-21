import re
from ollama import AsyncClient
import asyncio
import json

system_prompt = """
You are an emotional analysis assistant, skilled at discerning the emotional undertones in any input provided to you. Your expertise lies in evaluating text based on 8 fundamental emotions: joy, acceptance, fear, surprise, sadness, disgust, anger, and anticipation.

Instructions:
You will receive a statement or question as input.

Your task is to analyze the emotional content and assign scores to each of the 8 emotions.

Scores range from 1 (lowest intensity) to 10 (highest intensity), where a higher score indicates a stronger association with the corresponding emotion.

Provide a clear and concise reason for each score.

Always present your analysis as a valid Python list in the following format, do not forget anything:

[
    {"analysis": <REASON>, "dim": "joy", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "acceptance", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "fear", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "surprise", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "sadness", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "disgust", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "anger", "score": <SCORE>},
    {"analysis": <REASON>, "dim": "anticipation", "score": <SCORE>}
]
Rules
Use each of the 8 emotions only once in the response.

Ensure that the reasons provided for the scores are logical, concise, and intuitive.

"""

def extract_json_list(text):
    """
    Extracts the first JSON list from a string.
    Returns the JSON string or None if not found.
    """
    match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

async def analyze_emotion(prompt: str, model: str = "llama3.2:1b"):
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': prompt}
    ]
    response = await AsyncClient().chat(model=model, messages=messages)
    content = response.message.content
    print("Raw LLM output:\n", content)
    try:
        json_str = extract_json_list(content)
        if not json_str:
            print("No JSON list found in LLM output.")
            return None
        emotion_list = json.loads(json_str)
        print("Parsed emotion list:\n", emotion_list)
        # Optionally, extract just the scores:
        emotions = ["joy", "acceptance", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"]
        emotion_embedding = [1.0] * 8  # Default as float
        for item in emotion_list:
            if item["dim"] in emotions:
      
                emotion_embedding[emotions.index(item["dim"])] = float(item["score"])
        print("Emotion embedding:", emotion_embedding)
        return emotion_embedding
    except Exception as e:
        print("Failed to parse LLM output:", e)
        return None

if __name__ == "__main__":
    asyncio.run(analyze_emotion("sana wag na si maam magtanong technical HAHAHAHAHHA"))



