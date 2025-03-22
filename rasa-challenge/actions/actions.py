from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta


import sqlite3
import os

def criar_banco_de_dados(database):
    if not os.path.exists(database):
        conn = sqlite3.connect(database)
        print(f'Banco de dados {database} criado com sucesso!')
        
        # Criação da tabela de agendamentos
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT NOT NULL,
            name TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL
        )
        ''')
        conn.commit()
        print('Tabela "agendamentos" criada com sucesso!')
        conn.close()
    else:
        print(f'O banco de dados {database} já existe.')

# Função para adicionar um agendamento
def adicionar_agendamento(database, cpf,name, day, time):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    # Inserir o agendamento na tabela
    cursor.execute('''
    INSERT INTO agendamentos (cpf,name,day,time)
    VALUES (?, ?, ?, ?)
    ''' ,(cpf,name,  day, time))
    
    conn.commit()
    print(f'Agendamento de {name} inserido com sucesso!')
    conn.close()

class ActionTime(Action):
    def name(self) -> Text:
        return "action_scheduling"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        database = 'agendamentos.db'

        # Verifica e cria o banco de dados, caso não exista
        criar_banco_de_dados(database)

        # Pega os slots que foram definidos no diálogo
        cpf = tracker.get_slot('cpf')
        name = tracker.get_slot('name')
        day = tracker.get_slot('day')
        time = tracker.get_slot('time')

        # Adiciona o agendamento ao banco de dados
        adicionar_agendamento(database, cpf,name,  day, time)

        # Retorna um feedback ao usuário
        dispatcher.utter_message(text=f"Agendamento de {name} para o dia {day} às {time} foi confirmado.")

        return []
    
