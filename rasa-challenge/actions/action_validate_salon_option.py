from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta
import json
class ActionValidateSalonOption(Action):
    def name(self) -> Text:
        return "validate_option_salon"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        option = tracker.latest_message['text']
        with open("salons.json", "r") as file:
            salon_options = json.load(file)
        salon_options = list(salon_options.keys())
        if option not in salon_options:
            dispatcher.utter_message(text="Please select a valid salon option.")
            return [SlotSet("option_salon", None)]
        # Check if the salon option is available for the 
        return [SlotSet("option_salon", option)]