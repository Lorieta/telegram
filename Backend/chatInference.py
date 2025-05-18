from ollama import AsyncClient
import asyncio

async def Chat(prompt:str):
    message = [{'role':'user','content': f"{prompt}"}]
    response = await AsyncClient().chat(model="hf.co/unsloth/gemma-3-4b-it-GGUF:IQ3_XXS",messages=message)
        
    print(response.message.content)
    
    
asyncio.run(Chat("Hello"))