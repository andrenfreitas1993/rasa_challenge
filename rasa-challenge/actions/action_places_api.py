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
    
    base_url = "https://places.googleapis.com/v1/places:searchNearby"
    params = {"key": api_key,}
    
    payload = json.dumps({"includedTypes": [place],
                "maxResultCount": 5,
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
        listSlots = []
        
        place = tracker.get_slot("places")
        if place == 'beauty salon':
            place = 'beauty_salon'
        elif place == 'barber shop':
            place = 'barber_shop'
        
        API_KEY = " your api key here "
        if API_KEY:
            lista = []
            
            # Getting the current location
            location = get_current_location(API_KEY)
          
            if location:
                RADIUS = 20000.0  
                results = search_places(API_KEY, location, RADIUS,place)
                
                if results and results != {}:
                    for place in results['places']:
                        if 'id' in place:
                            idplace = place['id']
                            reviews = get_reviews(API_KEY,idplace)
                            if reviews:
                                review_string = ''
                                reviews_list = []
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
                                if 'reviews' in reviews:
                                    for review in reviews['reviews']:
                                        review_string += review['text']['text'] + "\n"
                                    reviews_list.append(review_string)
                                else:
                                    reviews_list.append("No reviews available")
                                
                                lista.append([displayname,formattedAddress,rating,reviews_list])
                else:
                    dispatcher.utter_message("I couldn't find any places nearby.\n\nTip:\nAdjusting the distance increases the likelihood of finding places closer to you.")
                    return []
            dispatcher.utter_message(f"Here are some suggestions for you:")
            for i,l in enumerate(lista):
                dispatcher.utter_message(f"OPTION: {i}\nName:{l[0]}\nAdress:{l[1]}\nRating:{l[2]}")
                places[str(l[0])] = {
                    "name": l[0],
                    "address": l[1],
                    "rating": l[2],
                    "reviews": l[3]
                }
                listSlots.append(l[0])
            with open("places.json", "w",encoding="utf-8") as f:
                json.dump(places, f, indent=4)
            return [SlotSet("place_validation", listSlots)]
        else:
            with open("places.json", "r",encoding="utf-8") as f:
                places = json.load(f)
            dispatcher.utter_message(f"Here are some suggestions for {place}:")
            for i,l in enumerate(places):
                dispatcher.utter_message(f"OPTION: {i}\nNome:{places[l]['name']}\nEndereço:{places[l]['address']}\nRating:{places[l]['rating']}")
                listSlots.append(places[l]['name'])
            return [SlotSet("place_validation", listSlots)]