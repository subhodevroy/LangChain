from pydantic import BaseModel
from app.web.api import(get_messages_by_conversation_id,add_message_to_conversation)
from langchain_core.chat_history import BaseChatMessageHistory
class SqlMessageHistory(BaseChatMessageHistory, BaseModel):
    conversation_id: str

    @property
    def messages(self):
        return get_messages_by_conversation_id(self.conversation_id)

    def add_message(self, message):

        return add_message_to_conversation(conversation_id=self.conversation_id, role=message.type, content=message.content)
    def clear(self):        # Implement logic to clear messages for the conversation_id
        pass