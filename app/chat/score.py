import random

from app.chat.redis import client

def score_conversation(
    conversation_id: str, score: float, llm: str, retriever: str, memory: str
) -> None:
    """
    This function interfaces with langfuse to assign a score to a conversation, specified by its ID.
    It creates a new langfuse score utilizing the provided llm, retriever, and memory components.
    The details are encapsulated in JSON format and submitted along with the conversation_id and the score.

    :param conversation_id: The unique identifier for the conversation to be scored.
    :param score: The score assigned to the conversation.
    :param llm: The Language Model component information.
    :param retriever: The Retriever component information.
    :param memory: The Memory component information.
    """
    score=min(max(score, 0), 1)  # Ensure score is between 0 and 1
    client.hincrby("llm_score_values", llm, score)
    client.hincrby("llm_score_total", llm, 1)

    client.hincrby("retriever_score_values", retriever, score)
    client.hincrby("retriever_score_total", retriever, 1)

    client.hincrby("memory_score_values", memory, score)
    client.hincrby("memory_score_total", memory, 1)


def get_scores():
    """
    Retrieves and organizes scores from the langfuse client for different component types and names.
    The scores are categorized and aggregated in a nested dictionary format where the outer key represents
    the component type and the inner key represents the component name, with each score listed in an array.

    The function accesses the langfuse client's score endpoint to obtain scores.
    If the score name cannot be parsed into JSON, it is skipped.

    :return: A dictionary organized by component type and name, containing arrays of scores.

    """
    aggregated_scores = {"llm": {}, "retriever": {}, "memory": {}}
    for component_type in aggregated_scores.keys():
        scores = client.hgetall(f"{component_type}_score_values")
        counts = client.hgetall(f"{component_type}_score_total")
        names=scores.keys()
        for name in names:
            score=int(scores.get(name, 1))
            count=int(counts.get(name, 1))
            average_score = score / count 
            aggregated_scores[component_type][name] = [average_score]
    return aggregated_scores

def random_component_by_score(component_type, component_map):
    """
    Selects a component from the component_map based on the average score of each component.

    :param component_type: A string indicating the type of component (e.g., "retriever").
    :param component_map: A dictionary mapping component names to their builder functions.
  
    :return: The name of the selected component.
    """
    if component_type not in ["llm", "retriever", "memory"]:
        raise ValueError("Invalid component type. Must be 'llm', 'retriever', or 'memory'.")
    # From Redis, get the hash containing the total sum scores for given component
    total_scores = client.hgetall(f"{component_type}_score_values")
    # From Redis, get the hash containing the number of times each component was scored
    score_counts = client.hgetall(f"{component_type}_score_total")
    # Get all the valid component names from the component_map
    component_names = [name for name in component_map.keys() if name in total_scores]
    # For each valid component, calculate the average score by dividing the total sum score by the number of times it was scored
    print(total_scores, score_counts)
    avg_scores = {} 
    for name in component_names:
        score=int(total_scores.get(name,1))
        count=int(score_counts.get(name,1))
        average_score = score / count if count > 0 else 0
        avg_scores[name] = max(average_score, 0.01)  # Ensure a minimum average score to avoid zero probability
    #Do a weighted random selection based on the average scores
    total_avg_score = sum(avg_scores.values())
    random_score = random.uniform(0, total_avg_score)
    cumulative_score = 0.0
    for name, avg_score in avg_scores.items():
        cumulative_score += avg_score
        if random_score <= cumulative_score:
            return name 