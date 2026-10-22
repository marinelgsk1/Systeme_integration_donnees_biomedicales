import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


conversation_memory = []

def init_conversation(symptoms, diseases, meds, treatments):


    """
    Initializes the conversation with context based on the user's input and database results.
    This sets up the system prompt and the first assistant message.
    """


    global conversation_memory
    conversation_memory = []


    # Create the system message with instructions and context
    conversation_memory.append({
    "role": "system",
    "content": (
        "You are a medically trained assistant helping the user interpret symptom-based search results from a database.\n\n"

        "Your task is to analyze the symptoms and database results (diseases, medication causes, and treatments) to identify the most probable explanation.\n"
        "To do this, ask one clear medical question at a time to help confirm or exclude potential hypotheses. Use real diagnostic reasoning like a physician would.\n"
        "You may ask about:\n"
        "- Age or gender\n"
        "- Timing and evolution of symptoms\n"
        "- Medication history\n"
        "- Prior conditions or exposures\n\n"

        "⚠️ RULES:\n"
        "- Only use diseases, medications, and treatments provided in the database below.\n"
        "- Never invent a new disease or treatment.\n"
        "- Do not give generic advice (hydration, rest, consult a doctor).\n"
        "- When you give a diagnosis and treatment, include a short description of each.\n"
        "- Always clarify that your answer is based on the results below, because the user sees your response above them.\n\n"
        "- Do not use any Markdown formatting (no **bold**, no ## titles, no symbols). Write in plain, natural language only."
        "- Alaways say at the end that the diagnostic is based on the results below.\n"
        "-Don't ask for other symptoms and always give a result even if you are not sure "
        
        f"Symptoms (don't consider them as deasease, just analyse the symptoms): {', '.join(symptoms)}\n"

        f"📌 Provided Results: your diagnostic has to be something fund in this data !!! \n"
        f"Possible Diseases (from DB): {', '.join(diseases)}\n"
        f"Possible Medication Causes (from DB): {', '.join(meds)}\n"
        f"Possible Treatments (from DB): {', '.join(treatments)}"
    )
})

    conversation_memory.append({
        "role": "assistant",
        "content": (
            "Would you like me to analyze the results below? If so, I will need to ask you a few additional questions to refine the analysis."
        )
    })

def ask_openai(message):


    """
    Sends a message to OpenAI and returns the assistant's reply.
    Keeps track of conversation history in memory.
    """

    global conversation_memory

   
    if not message.strip():
        for msg in reversed(conversation_memory):
            if msg["role"] == "assistant":
                return msg["content"]
        return "AI is ready."  

    # Add the user's message to the conversation memory
    conversation_memory.append({"role": "user", "content": message})

    # Call OpenAI API to get the assistant's reply
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_memory
        )
        reply = response.choices[0].message.content.strip()
        conversation_memory.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"An error occurred: {str(e)}"