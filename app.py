import random
from databases.malayalam_database import responses as malayalam_responses
from databases.english_database import responses as english_responses
# Function to get a response
def get_response(user_input):
    user_input = user_input.lower().strip()

    # Check if the input is in English responses
    for key, replies in english_responses.items():
        if key in user_input:
            return random.choice(replies)
    
    # Check if the input is in Malayalam responses
    for key, replies in malayalam_responses.items():
        if key in user_input:
            return random.choice(replies)
    
    # Default response if no match is found
    return "Sorry, I didn't understand that. Can you try again?"

# Main chatbot loop
def chatbot():
    print("Welcome to the AI Chatbot!")
    print("You can chat with me in English or Malayalam. Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye! Have a great day!")
            break
        response = get_response(user_input)
        print(f"Chatbot: {response}")

# Run the chatbot
if __name__ == "__main__":
    chatbot()