from flask import current_app
from queue import Queue 
from threading import Thread

from app.chat.callbacks.stream import StreamingCallbackHandler
class StreamableChain():
    def stream(self,input):
        queue=Queue()  # Create a new queue for this streaming session
        handler=StreamingCallbackHandler(queue)  # Create a new callback handler instance
        def task(app_context):
            app_context.push()  # Push the Flask application context to this thread
            self(input,callbacks=[handler])  # Call the chain to start the streaming process
        Thread(target=task,args=[current_app.app_context()]).start()  # Start the streaming in a separate thread
        while True:
            token=queue.get()  # Get the next token from the queue
            if token is None:  # Check for the end of the stream
                break
            yield token  # Yield the token to the caller   