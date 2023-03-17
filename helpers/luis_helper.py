# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails

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

                    if entity is not None:
                        setattr(booking_details, MAP_KEY_ATTR[key], entity)
                
            return Intent.BOOK_FLIGHT.value, booking_details
                    
        except Exception as exception:
            print(f"Error in execute_luis_query: {exception}")

        return Intent.NONE_INTENT.value, None

    # Return the right entity in the Json
    @staticmethod
    def _get_entity(recognizer_result, key, type_):
        if (recognizer_result.entities.get("$instance") is None
            or recognizer_result.entities.get(key) is None
            or len(recognizer_result.entities.get(key)) == 0) :
            return None

        # finds the entity with the highest score in the list of entities for the given key
        selected_entity = max(recognizer_result.entities.get("$instance").get(key), key=lambda x: x["score"])
        print(f'key: {key}, type: {type_}, selected_entity: {selected_entity}')
        
        # Get a list of entities of the specified type
        entities = recognizer_result.entities.get("$instance").get(type_)
        if entities:
            # Update the index with the minimum score based on the distance between the start and end indices of the entities
            index, _ = min(
                enumerate(entities),
                key=lambda e: abs(e[1]['startIndex'] - selected_entity['startIndex']) + abs(e[1]['endIndex'] - selected_entity['endIndex'])
            )
        else:
            return None
        

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