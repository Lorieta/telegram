from pathlib import Path
import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.ollama import OllamaEmbedding 
from llama_index.llms.ollama import Ollama
from llama_index.readers.json import JSONReader
from llama_index.vector_stores.qdrant import QdrantVectorStore
import asyncio

prompt = """
You are an AI designed to analyze communication metadata and generate reply suggestions that perfectly mimic the specified user's typing behavior. Your goal is to provide five distinct reply suggestions for the *last message received*, based on the full context of the conversation.

**The following context is dynamically provided by a RAG (Retrieval-Augmented Generation) system to inform your response:**

---
### **User Typing Behavior Profile (Reign - Retrieved Data):**
* **Language Mix:** Primarily uses very informal, conversational English with heavy use of internet slang and abbreviations (e.g., 'u', 'l8r', 'sm', 'hw', 'b4', 'dis sem', 'rn', 'lol', 'tru', 'bet', 'ty', 'ily', 'ilyt'). There is no Taglish present in their messages in this context.
* **Sentence Structure:** Tends to use very short, fragmented sentences or phrases. Responses are concise and direct.
* **Punctuation & Grammar:** Minimal to no standard punctuation (no periods, commas, or proper capitalization at the start of sentences). Uses multiple question marks or exclamation points for emphasis.
* **Emoji Usage:** Uses emojis consistently to convey emotion or add emphasis. Specific emojis observed: 😩, 💀, 👀, 😭.
* **Common Phrases/Slang:** "idk yet," "got sm hw," "b4 i flop," "bet!", "i'll pull up," "ty," "ily."
* **Tone:** Casual, informal, friendly, sometimes a bit stressed (😩) or dramatic (💀, 😭), and enthusiastic ("bet!").
* **Typing Quirks:** Uses numbers for letters ('2', '4'), heavy use of initialisms and internet abbreviations.

---
Reply to the last message
"""

async def suggesitonGeneration():
   Settings.llm = Ollama(model="gemma3:4b", request_timeout=1000)

   Settings.embed_model = OllamaEmbedding(model_name='nomic-embed-text:latest')

   loader = JSONReader()
   documents = loader.load_data(Path(r'C:\Users\John Carlo\telegram\Backend\saved_messages\reign_analysis.json'))

   client = qdrant_client.QdrantClient(path="./qdrant_data")
   vector_store = QdrantVectorStore(client=client, collection_name="analysis")
   storage_context = StorageContext.from_defaults(vector_store=vector_store)

   index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

   query_engine = index.as_query_engine()
   response = query_engine.query(prompt)
   
   print(response)
   

asyncio.run(suggesitonGeneration())