from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta


class ActionTime(Action):
    def name(self) -> Text:
        return "action_suggested_salon"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lista = [["Feeh Nails Decorated","Rua Nóbrega de Sousa Coutinho, 160 - Jardim Peri, São Paulo - SP, 02651-010, Brazil","Rating: 4.4"],["Espaço Carolina","Rua odassi nazzali, 63 - Jardim Santa Cruz, São Paulo - SP, 02672-010, Brazil","Rating: Não disponível"]]
        dispatcher.utter_message("Here are some suggestions for Beauty Salon::")
        for l in lista:
            dispatcher.utter_message(f"Nome:{l[0]}")
            dispatcher.utter_message(f"Endereço:{l[1]}")
            dispatcher.utter_message(f"Rating:{l[2]}")
            dispatcher.utter_message("###################")
        return []