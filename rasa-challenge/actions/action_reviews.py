# actions.py

import requests
import json
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionSummarizeReview(Action):
    def name(self) -> str:
        return "action_summarize_review"
    
    def summarize_review(self, review_text: str) -> str:
        # Prepare the prompt for summarizing the review
        url = "https://api.openai.com/v1/responses"
        api_key = 'your_api_key'  # Replace with your OpenAI API key
        prompt = f"""
        Summarize the following restaurant review in English, keeping it within 100 tokens:

        "{review_text}"
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'  # API key passed in the header
        }

        data = {
            'model': 'gpt-4o-mini',  # Change this if you need a different model
            'input': prompt,
            'max_output_tokens': 100,  # Limit the summary to 100 tokens
            'temperature': 0.5  # Moderate creativity for a concise summary
        }
        
        # Send the POST request to OpenAI API
        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract and return the summary from the response
            result = response.json()
       
            print(result['output'][0]['content'][0]['text'])  # Print the summary for debugging
            return result['output'][0]['content'][0]['text']
        else:
            # Handle any error that occurs
            return f"Error {response.status_code}: {response.text}"
    
    def run(self, dispatcher, tracker, domain) -> list:
        # Retrieve the review text from the user's message or slots
        with open('places.json', 'r') as file:
            review_text = json.load(file)

        place = tracker.get_slot("name_place")
        if place:
            review_text = review_text[place]['reviews']
            if review_text:
                # Get the summarized review
                summary = self.summarize_review(review_text)

                # Return the summary to the user
                dispatcher.utter_message(text=f"Here is the summarized review: {summary}")
            else:
                dispatcher.utter_message(text="Sorry, I couldn't find a review to summarize.")

            return []
        dispatcher.utter_message(text="Sorry, I couldn't find the place you mentioned.")
        return []
