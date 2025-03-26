from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta
import json

class ActionTime(Action):
    def name(self) -> Text:
        return "action_suggested_salon"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        salons = {}
        lista = [["Feeh Nails Decorated","Rua Nóbrega de Sousa Coutinho, 160 - Jardim Peri, São Paulo - SP, 02651-010, Brazil","Rating: 4.4"],["Espaço Carolina","Rua odassi nazzali, 63 - Jardim Santa Cruz, São Paulo - SP, 02672-010, Brazil","Rating: Não disponível"]]
        dispatcher.utter_message("Here are some suggestions for Beauty Salon:")
        for i,l in enumerate(lista):
            dispatcher.utter_message(f"OPTION: {i}\nNome:{l[0]}\nEndereço:{l[1]}\n{l[2]}")
            salons[str(i)] = {
                "name": l[0],
                "address": l[1],
                "rating": l[2]
            }
        with open("salons.json", "w",encoding="utf-8") as f:
            json.dump(salons, f, indent=4)
        return []

        