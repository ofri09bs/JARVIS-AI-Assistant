import chromadb
import time
import uuid

# Global variables to hold the database client and collection
_memory_client = None
_memory_collection = None

def initialize_memory(db_path="./db_memory", collection_name="long_term_memory"):
    """
    Initializes the ChromaDB persistent client and retrieves or creates the collection.
    This ensures the database is ready for read/write operations.
    """
    global _memory_client, _memory_collection
    
    # Create a persistent client that saves data to the local disk
    _memory_client = chromadb.PersistentClient(path=db_path)
    
    # Get the collection or create it if it doesn't exist
    _memory_collection = _memory_client.get_or_create_collection(name=collection_name)

def save_interaction(user_query, system_response):
    """
    Saves a single interaction (user query and system response) into the vector database.
    Generates a unique ID and saves metadata for future filtering.
    """
    if _memory_collection is None:
        initialize_memory()
        
    # Combine the query and response into a single context block
    interaction_text = f"User: {user_query}\nJarvis: {system_response}"
    
    # Generate a unique ID for this specific memory entry
    entry_id = str(uuid.uuid4())
    
    # Store the current timestamp as metadata
    current_time = str(time.time())
    
    # Add the document to ChromaDB. 
    # By default, ChromaDB will automatically generate the mathematical embedding for this text.
    _memory_collection.add(
        documents=[interaction_text],
        metadatas=[{"timestamp": current_time, "type": "conversation"}],
        ids=[entry_id]
    )

def retrieve_relevant_context(current_query, num_results=3, distance_threshold=1.2):
    """
    Searches the vector database for past interactions that are semantically 
    similar to the current query.
    Filters out results that are too far mathematically (above distance_threshold).
    Returns a formatted string containing the relevant context.
    """
    if _memory_collection is None:
        initialize_memory()
        
    # Query the database for the most similar documents
    # ChromaDB automatically returns 'distances' along with 'documents'
    results = _memory_collection.query(
        query_texts=[current_query],
        n_results=num_results
    )
    
    retrieved_documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    
    if not retrieved_documents:
        return "No relevant past context found."
        
    context_string = "Relevant past interactions:\n"
    valid_results_found = False
    
    # Iterate through documents and their corresponding distances
    for i, (doc, dist) in enumerate(zip(retrieved_documents, distances)):
        # print(f"[DEBUG MEMORY] Distance for memory {i+1}: {dist}") # Uncomment to calibrate
        
        # Only include the document if it's close enough (distance is below the threshold)
        if dist <= distance_threshold:
            context_string += f"--- Memory {i+1} ---\n{doc}\n\n"
            valid_results_found = True
            
    # If all retrieved documents were above the threshold
    if not valid_results_found:
        return "No relevant past context found."
        
    return context_string