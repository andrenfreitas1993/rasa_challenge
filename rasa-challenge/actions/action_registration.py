
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionRegisterUser(Action):

    def name(self) -> str:
        return "action_registration"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the slots with the user's data
        affirmation = ['yes']
        negation = ['no','not']
        r = tracker.latest_message.get
        if r in affirmation:
            return [SlotSet("registration", True)]
        
        return [SlotSet("registration", False)]
