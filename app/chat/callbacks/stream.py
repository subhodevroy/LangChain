from langchain.callbacks.base import BaseCallbackHandler


class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self,queue):
        self.queue=queue # Create a new queue for this streaming session
        self.streaming_run_ids=set()  # To track which runs are streaming       
    def on_chat_model_start(self, serialized, messages,run_id, **kwargs):
        if serialized["kwargs"]["streaming"]:
            self.streaming_run_ids.add(run_id)  # Add the run ID to the set of streaming runs
    def on_llm_new_token(self, token: str, **kwargs):
        self.queue.put(token)  # Add the token to the queue
    def on_llm_end(self, response,run_id, **kwargs):
        if run_id in self.streaming_run_ids:
            self.queue.put(None)  # Signal the end of the stream with None
            self.streaming_run_ids.remove(run_id)  # Remove the run ID from the set of streaming runs
    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)  # Signal the end of the stream with None in case of error
