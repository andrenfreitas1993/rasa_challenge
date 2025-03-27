from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta
import json
import sqlite3
import os

class ActionReadAppointment(Action):
    def name(self) -> Text:
        return "action_read_appointment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Caminho para o banco de dados
        database = "agendamentos.db"

        # Obtém o CPF do slot
        cpf = tracker.get_slot("cpf")
        # Verifica se o banco de dados existe
        if not os.path.exists(database):
            dispatcher.utter_message(text="Não foi possível validar seus agendamentos")
            return []

        try:
            # Conecta ao banco de dados
            conn = sqlite3.connect(database)
            cursor = conn.cursor()

            # Consulta os agendamentos pelo CPF
            cursor.execute("SELECT name, date, time,salon_name,address FROM agendamentos WHERE cpf = ?", (cpf,))
            rows = cursor.fetchall()

            if rows:
                # Monta a mensagem com os agendamentos encontrados
                appointments = "\n".join(
                    [f"Name: {row[0]}, Date: {row[1]}, Hour: {row[2]},Salon Name:{row[3]},Address:{row[4]}" for row in rows]
                )
                dispatcher.utter_message(text=f"Appointments found:\n{appointments}")
            else:
                dispatcher.utter_message(text="No appointments were found for the CPF provided.")

            conn.close()
        except sqlite3.Error as e:
            dispatcher.utter_message(text=f"We were unable to validate your bookings.")
            return []

        return []