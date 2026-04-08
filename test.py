from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate    
from dotenv import load_dotenv  
from langchain.chains import LLMChain   
from langchain.callbacks.base import BaseCallbackHandler
from queue import Queue 
from threading import Thread

load_dotenv()  # Load environment variables from .env file
queue=Queue()
class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self,queue):
        self.queue=queue # Create a new queue for this streaming session
    def on_llm_new_token(self, token: str, **kwargs):
        self.queue.put(token)  # Add the token to the queue
    def on_llm_end(self, response, **kwargs):
        self.queue.put(None)  # Signal the end of the stream with None
    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)  # Signal the end of the stream with None in case of error
chat=ChatOpenAI(streaming=True)
prompt=ChatPromptTemplate.from_messages([
    ("human","{content}")
])
# chain=LLMChain(llm=chat,prompt=prompt)
# # message=prompt.format_messages(content="What is the capital of France?")  
# # for message in chat.stream(message):
# #     print(message)
# for output in chain.stream(input={"content": "Tell me a joke about programming. Make it short and funny."}):
#     print(output)
input={"content": "Tell me a joke about programming. Make it short and funny."}

class StreamableChain():
    def stream(self,input):
        queue=Queue()  # Create a new queue for this streaming session
        handler=StreamingCallbackHandler(queue)  # Create a new callback handler instance
        def task():
            self(input,callbacks=[handler])  # Call the chain to start the streaming process
        Thread(target=task).start()  # Start the streaming in a separate thread
        while True:
            token=queue.get()  # Get the next token from the queue
            if token is None:  # Check for the end of the stream
                break
            yield token  # Yield the token to the caller   
class StreamingChain(StreamableChain,LLMChain):
    pass
chain=StreamingChain(llm=chat,prompt=prompt)

for output in chain.stream(input=input):
    print(output)   