# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from dateutil import parser
from booking_details import BookingDetails
from datetime import datetime

def get_timex(or_date):
    date = parser.parse(or_date)
    date_str = parser.parse(or_date).strftime("%Y-%m-%d")

    year, month, day = date_str.split('-')

    if day not in or_date:
        day = "XX"

    if date.strftime("%b").lower() not in or_date:
        month = "XX"

    if year not in or_date:
        year = "XXXX"

    final_date = f"{year}-{month}-{day}"

    return final_date

# Define the Intent enum class
class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    CANCEL = "Cancel"
    NONE_INTENT = "None"
    
# Define the key mapping for attributes and their corresponding types
MAP_KEY_ATTR = {'or_city': 'origin', 'dst_city':'destination', 'str_date': 'start_date', 'end_date': 'end_date', 'budget': 'budget'}
MAP_KEY_TYPE = {'or_city': 'geographyV2_city', 'dst_city':'geographyV2_city', 'str_date': 'datetime', 'end_date': 'datetime', 'budget': 'number'}



# Define a function to determine the top intent from a dictionary of intents
def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    # Initialize variables to store the top intent and its score
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    # Loop through all intents and their scores
    for intent, value in intents:
        # Create an IntentScore object from the score value
        intent_score = IntentScore(value)
        
        # Check if this intent has a higher score than the current top intent
        if intent_score.score > max_value:
            # If so, update the top intent and its score
            max_intent, max_value = intent, intent_score.score
    # Create a TopIntent object from the top intent and its score, and return it
    return TopIntent(max_intent, max_value)



# Define a helper class for LUIS functionality
class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)
            intent = recognizer_result.get_top_scoring_intent().intent

            if intent == Intent.BOOK_FLIGHT.value:
                booking_details = BookingDetails()

                for (key, type_) in MAP_KEY_TYPE.items():
                    entity = LuisHelper._get_entity(recognizer_result, key, type_)
                    #print(f'----------> key: {key}, type: {type_}, entity: {entity}')
                    if entity is not None:
                        #print(f'key: {key}, type: {type_}, entity: {entity}')
                        setattr(booking_details, MAP_KEY_ATTR[key], entity)
                
            return Intent.BOOK_FLIGHT.value, booking_details
                    
        except Exception as exception:
            print(f"Error in execute_luis_query: {exception}")

        return Intent.NONE_INTENT.value, None

    
    # Return the right entity in the Json
    def _get_entity(recognizer_result, key_, type_):
        '''
        recognizer_result: LuisRecognizerResult object
        key_ is the name of the entity in the LUIS model
        type_ is the type of the entity in the LUIS model
        '''
        if (recognizer_result.entities.get("$instance") is None
            or recognizer_result.entities.get(key_) is None
            or len(recognizer_result.entities.get(key_)) == 0) :
            return None

        selected_entity = max(recognizer_result.entities.get("$instance").get(key_), key=lambda x: x["score"])

        index, min_entity = min(
            enumerate(recognizer_result.entities.get("$instance").get(type_)),
            key=lambda x: abs(x[1]['startIndex'] - selected_entity['startIndex']) + abs(x[1]['endIndex'] - selected_entity['endIndex'])
        )


        if (index is None
            or recognizer_result.entities.get(type_) is None
            or len(recognizer_result.entities.get(type_)) <= index):
            return None
        
        return (
            recognizer_result.entities.get(type_)[index].capitalize()
            if type_ == 'geographyV2_city'
            else recognizer_result.entities.get(type_)[index]["timex"][0]
            if type_ == 'datetime'
            else recognizer_result.entities.get(type_)[index]
            if type_ == 'number'
            else None
        )
        
    
    # Return the right entity in the Json
    def _get_entity_v2(recognizer_result, key_, type_):
        '''
        recognizer_result: LuisRecognizerResult object
        key_ is the name of the entity in the LUIS model
        type_ is the type of the entity in the LUIS model
        '''
        #print(f'1{recognizer_result.entities.get("$instance") is None}')
        #print(f'2{recognizer_result.entities.get(key_) is None}')
        #print(f'3{len(recognizer_result.entities.get(key_)) == 0}')
        
        if ((key_ == 'str_date') | (key_ == 'end_date')):
            verif_key = 'datetime'
        else:
            verif_key = key_
          
        if (recognizer_result.entities.get("$instance") is None
            or recognizer_result.entities.get(verif_key) is None
            or len(recognizer_result.entities.get(verif_key)) == 0) :
            return None

        
        #print(f'recognizer_result: {recognizer_result}')
        #print(f'..........key_: {key_}, type: {type_}')
        
        # finds the entity with the highest score in the list of entities for the given key
        selected_entity = max(recognizer_result.entities.get("$instance").get(verif_key), key=lambda x: x["score"])
        print(f'key_: {key_}, type: {type_}, selected_entity: {selected_entity}')
        
        
        list_keys = list(recognizer_result.entities.keys())
        print(f'............list_keys: {list_keys}')
        print(f"---->{    ('datetime' in list_keys) & ((key_ == 'str_date') | (key_ == 'end_date'))      }" )
        
        if (type_ == 'geographyV2_city') & (key_ == 'or_city'):
            or_city = selected_entity['text'].capitalize()
            print(f'1.or_city: {or_city}')
            return or_city
        elif ('or_city' in list_keys) & (key_ == 'or_city'):
            or_city = recognizer_result.entities.get('or_city')[0].capitalize()
            print(f'2.or_city: {or_city}')
            return or_city
        
        if (type_ == 'geographyV2_city') & (key_ == 'dst_city'):
            dst_city = selected_entity['text'].capitalize()
            print(f'3.dst_city: {dst_city}')
            return dst_city
        elif ('dst_city' in list_keys) & (key_ == 'dst_city'):
            dst_city = recognizer_result.entities.get('dst_city')[0].capitalize()
            print(f'4.dst_city: {dst_city}')
            return dst_city
        
        if (type_ == 'datetime') & (key_ == 'str_date'):
            str_date = selected_entity[0]['text']
            return str_date
        elif (type_ == 'datetime') & (key_ == 'end_date'):
            end_date = selected_entity[0]['text']
            return end_date
        elif ('datetime' in list_keys) & ((key_ == 'str_date') | (key_ == 'end_date')):
            print('HERE 1')
            if len(recognizer_result.entities.get('datetime')) == 2:
                print('HERE 2')
                date_1 = recognizer_result.entities.get('datetime')[0]['timex'][0]
                date_2 = recognizer_result.entities.get('datetime')[1]['timex'][0]
                
                datetime_date_1 = datetime.strptime(date_1, '%Y-%d-%m').date()
                datetime_date_2 = datetime.strptime(date_2, '%Y-%d-%m').date()
                
                if (datetime_date_2>datetime_date_1):
                    str_date = date_1
                    end_date = date_2
                elif (datetime_date_2==datetime_date_1):
                    str_date = date_1
                    end_date = date_2
                else:
                    str_date = date_2
                    end_date = date_1
                    
                if (key_ == 'str_date'):
                    return str_date
                elif (key_ == 'end_date'):
                    return end_date
            elif (len(recognizer_result.entities.get('datetime')) == 1) & (key_ == 'str_date'):
                date_1 = recognizer_result.entities.get('datetime')[0]['timex'][0]
                str_date = date_1
                return str_date
            elif (len(recognizer_result.entities.get('datetime')) == 1) & (key_ == 'end_date'):
                date_1 = recognizer_result.entities.get('datetime')[0]['timex'][0]
                end_date = date_1
                return end_date
        
        if (type_ == 'number') & (key_ == 'budget'):
            budget = selected_entity['text']
            return budget        
        elif ('budget' in list_keys) & (key_ == 'budget'):
            budget = recognizer_result.entities.get('budget')[0]
            return budget
        
        '''
        return (
            selected_entity['text'].capitalize()
            if (type_ == 'geographyV2_city') & (key_ == 'or_city')
            
            
            else selected_entity['text'].capitalize()
            if (type_ == 'geographyV2_city') & (key_ == 'dst_city')
            
            
            else selected_entity['text']
            if (type_ == 'datetime') & (key_ == 'str_date')
            
            
            else selected_entity['text']
            if (type_ == 'datetime') & (key_ == 'end_date')
            
            else selected_entity['text']
            if (type_ == 'number') & (key_ == 'budget')
            
            else None
        )
        '''     
        
        '''
        # Get a list of entities of the specified type
        top_score = 0
        top_index = None
        
        
        print(f'????????????{recognizer_result.entities.get("$instance").get(type_)}')
        for index, entity in enumerate(recognizer_result.entities.get("$instance").get(type_)):
            print(f'index: {index}, entity: {entity}')
            print(entity["endIndex"], selected_entity["endIndex"])
        
        for index, entity in enumerate(
            recognizer_result.entities.get("$instance").get(type_)
        ):
            score = min(entity["endIndex"], selected_entity["endIndex"]) - max(
                entity["startIndex"], selected_entity["startIndex"]
            )

            if score > top_score:
                top_index = index
                top_score = score

        if (
            top_index is None
            or recognizer_result.entities.get(type_) is None
            or len(recognizer_result.entities.get(type_)) < top_index
        ):
            return None
        
        return (
            recognizer_result.entities.get(type_)[index].capitalize()
            if type_ == 'geographyV2_city'
            else recognizer_result.entities.get(type_)[index]["timex"][0]
            if type_ == 'datetime'
            else recognizer_result.entities.get(type_)[index]
            if type_ == 'number'
            else None
        )
        '''