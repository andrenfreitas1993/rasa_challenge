from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta
import json

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
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            salon_name TEXT NOT NULL,
            address TEXT NOT NULL         
        )
        ''')
        conn.commit()
        print('Tabela "agendamentos" criada com sucesso!')
        conn.close()
    else:
        print(f'O banco de dados {database} já existe.')

# Função para adicionar um agendamento
def adicionar_agendamento(database, cpf,name, day, time,salon_name,address):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    # Inserir o agendamento na tabela
    cursor.execute('''
    INSERT INTO agendamentos (cpf,name,date,time,salon_name,address)
    VALUES (?, ?, ?, ?,?,?)
    ''' ,(cpf,name,  day, time,salon_name,address))
    
    conn.commit()
    print(f'Agendamento de {name} inserido com sucesso!')
    conn.close()

def ler_salons_json(filepath: str) -> Dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            salons = json.load(f)
            return salons
    except FileNotFoundError:
        print(f"Arquivo {filepath} não encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo {filepath}.")
        return {}
        


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
        date = tracker.get_slot('date')
        time = tracker.get_slot('time')
        option = tracker.get_slot('option_salon')
        salons = ler_salons_json("salons.json")
        choose_salon = salons[option]
        salon_name = choose_salon['name']
        address = choose_salon['address']
        # Adiciona o agendamento ao banco de dados
        adicionar_agendamento(database, cpf,name,  date, time,salon_name,address)

        # Retorna um feedback ao usuário
        dispatcher.utter_message(text=f"{name}'s appointment for the {date} at {time} confirmed.\n\nName:{salon_name}\naddress:{address}")

        return []
