from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime, timedelta
import requests
import json
import os

def get_reviews(api_key,placeId):
    url = f"https://places.googleapis.com/v1/places/{placeId}"
    params = {
        "key": api_key
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-FieldMask": "displayName.text,rating,formattedAddress,reviews"
    }
    response = requests.get(url,params=params,headers=headers)
    
    if response.status_code == 200:
        response = response.json()
        return response
    else:
        print(f"Erro ao obter avaliações: {response.status_code}")
        return None
        
def get_current_location(api_key):
    """
    Obtém a localização atual usando a API de Geolocalização do Google Maps.

    :param api_key: Sua chave de API do Google Maps.
    :return: Um dicionário com latitude e longitude.
    """
    url = "https://www.googleapis.com/geolocation/v1/geolocate"
    params = {
        "key": api_key
    }
    response = requests.post(url, json={}, params=params)
    if response.status_code == 200:
        location = response.json().get("location", {})
        return location
    else:
        print(f"Erro ao obter localização: {response.status_code}")
        return None

def search_places(api_key,location=None, radius=None,place=None):
    """
    Consome a API Places do Google Maps para buscar lugares com base em uma consulta.

    :param api_key: Sua chave de API do Google Maps.
    :param query: Termo de busca (ex: "restaurantes").
    :param location: Coordenadas de localização (ex: "37.7749,-122.4194").
    :param radius: Raio de busca em metros (ex: 1000).
    :return: Lista de resultados da API.
    """
    base_url = "https://places.googleapis.com/v1/places:searchNearby"
    params = {"key": api_key,}
    
    payload = json.dumps({"includedTypes": [place],
                "maxResultCount": 10,
                "locationRestriction": {
                    "circle": {
                    "center": {
                        "latitude": location['lat'],
                        "longitude": location['lng']},
                    "radius": radius
                    
    }
  }
})

    headers = {"Content-Type": "application/json","X-Goog-FieldMask": "places.displayName.text,places.formattedAddress,places.id"}
     
    # Removendo o cabeçalho desnecessário
    response = requests.post(base_url, params=params,data=payload,headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na requisição: {response.status_code}, Detalhes: {response.text}")
        return None


class ActionPlaceApi(Action):
    def name(self) -> Text:
        return "action_places_api"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        places = {}
        place = tracker.get_slot("places")

        API_KEY = "AIzaSyBpYUMc0pluQ2LS5glW4pO2loWofG2ySPI"
        if API_KEY:
            lista = []
            # Obtendo a localização atual
            location = get_current_location(API_KEY)
          
            if location:
                RADIUS = 20000.0  
                results = search_places(API_KEY, location, RADIUS,place)
                if results and results != {}:
                    for place in results['places']:
                        if 'id' in place:
                            idplace = place['id']
                            reviews = get_reviews(API_KEY,idplace)
                            print(reviews)
                            if reviews:
                                if 'displayName' in reviews:
                                    displayname = reviews['displayName']['text']
                                else:
                                    displayname = "name unavailable" 
                                if 'formattedAddress' in reviews:
                                    formattedAddress = reviews['formattedAddress']
                                else:
                                    formattedAddress = "address unavailable"
                                if 'rating' in reviews:
                                    rating = reviews['rating']           
                                else:
                                    rating = "rating unavailable"
                                lista.append([displayname,formattedAddress,rating])
                else:
                    dispatcher.utter_message("I couldn't find any places nearby.\n\nTip:\nAdjusting the distance increases the likelihood of finding places closer to you.")
                    return []
            dispatcher.utter_message(f"Here are some suggestions for you:")
            for i,l in enumerate(lista):
                dispatcher.utter_message(f"OPTION: {i}\nNome:{l[0]}\nEndereço:{l[1]}\nRating:{l[2]}")
                places[str(i)] = {
                    "name": l[0],
                    "address": l[1],
                    "rating": l[2]
                }
            with open("places.json", "w",encoding="utf-8") as f:
                json.dump(places, f, indent=4)
            return []
        else:
            with open("places.json", "r",encoding="utf-8") as f:
                places = json.load(f)
            dispatcher.utter_message(f"Here are some suggestions for {place}:")
            for i,l in enumerate(places):
                dispatcher.utter_message(f"OPTION: {i}\nNome:{places[l]['name']}\nEndereço:{places[l]['address']}\nRating:{places[l]['rating']}")
            return []