from app.chat.models import ChatArgs
from app.chat.vector_stores.pinecone import build_retriever
from langchain.chains import ConversationalRetrievalChain
from app.chat.llms.chatopenai import build_llm  
from app.chat.memories.sql_memory import build_memory   
from langchain_openai import ChatOpenAI
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain
from app.chat.vector_stores import retrievar_map
from app.web.api import (set_conversation_components, get_conversation_components)
from app.chat.llms import llm_map
from app.chat.memories import memory_map    
import random
from app.chat.score import random_component_by_score
def build_chat(chat_args: ChatArgs):
    """
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: A chain

    Example Usage:

        chain = build_chat(chat_args)
    """

    # retriever = build_retriever(chat_args)
    # return ConversationalRetrievalChain.from_llm(
    #     llm=llm,
    #     retriever=retriever,
    #     memory=memory)
    retriever_name,retriever=select_components("retriever",retrievar_map,chat_args)  
    llm_name,llm=select_components("llm",llm_map,chat_args)
    memory_name,memory=select_components("memory",memory_map,chat_args)
     # Store the selected component in the conversation components for later retrieval
    set_conversation_components(
        chat_args.conversation_id,
        llm_name,
        retriever_name,
        memory_name

    )
    condense_question_llm=ChatOpenAI(streaming=False)  # You can use a non-streaming LLM for condensing questions
    return StreamingConversationalRetrievalChain.from_llm(
        llm=llm,
        condense_question_llm=condense_question_llm,
        retriever=retriever,
        memory=memory)
def select_components(component_type,component_map,chat_args):
    """
    Selects a component from the component_map based on the chat_args.

    :param component_type: A string indicating the type of component (e.g., "retriever").
    :param component_map: A dictionary mapping component names to their builder functions.
    :param chat_args: ChatArgs object containing conversation_id, pdf_id, metadata, and streaming flag.

    :return: The name and instance of the selected component.
    """
    components=get_conversation_components(chat_args.conversation_id) 
    previous_component=components[component_type]
    if previous_component:
        selected_component_name = previous_component
    else:
        # For first time, we randomly select a component.
        selected_component_name = random_component_by_score(component_type, component_map)
    
    selected_component_builder = component_map[selected_component_name]
    selected_component_instance = selected_component_builder(chat_args)
    
   
    
    return selected_component_name, selected_component_instance