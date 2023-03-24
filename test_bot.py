#import sys
#import os
import json
import aiounittest
#import unittest
from booking_details import BookingDetails
from config import DefaultConfig
from dialogs import BookingDialog, MainDialog
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent
from botbuilder.dialogs.prompts import TextPrompt
from botbuilder.core import (
    TurnContext, 
    ConversationState, 
    MemoryStorage
)
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.core.adapters import TestAdapter

class TestBotLuis(aiounittest.AsyncTestCase):

    async def test_execute_luis_query(self):
        CONFIG = DefaultConfig()
        luis_recognizer = FlightBookingRecognizer(CONFIG)

        async def exec_test(turn_context: TurnContext):
            intent, result = await LuisHelper.execute_luis_query(
                luis_recognizer, turn_context
            )

            await turn_context.send_activity(
                json.dumps({"intent": intent,
                            "booking_details": None if not hasattr(result, "__dict__") else result.__dict__
                            })
            )

        adapter = TestAdapter(exec_test)
        
        await adapter.test(
            "Hy",
            json.dumps(
                {
                    "intent": Intent.BOOK_FLIGHT.value,
                    "booking_details": BookingDetails().__dict__,
                }
            ),
        )
        
        await adapter.test(
            "I want to fly to Paris",
            json.dumps(
                {
                    "intent": Intent.BOOK_FLIGHT.value,
                    "booking_details": BookingDetails(
                        destination="Paris"
                    ).__dict__,
                }
            ),
        )

        
        await adapter.test(
            "I would like to travel to Paris. I want to leave on 23 july 2023 and return back on 28 july 2023",
            json.dumps(
                {
                    "intent": Intent.BOOK_FLIGHT.value,
                    "booking_details": BookingDetails(
                        destination = "Paris",
                        start_date="2023-07-23",
                        end_date="2023-07-28"
                    ).__dict__,
                }
            ),
        )





class BotTest(aiounittest.AsyncTestCase):

    # Test une réservation étape par étape
    async def test_booking_step_by_step(self):
        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)


        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)

        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hy", "What can I help you with today?")
        await adapter.test("Book me a flight", "From what city will you be travelling?")
        await adapter.test("I am from Paris", "To what city would you like to travel?")
        await adapter.test("I want to go to London", "What date would you like to travel?")
        await adapter.test("25 march 2023", "What date would you like to return?")
        await adapter.test("28 march 2023", "What is your budget to travel from I am from Paris to I want to go to London?")
        await adapter.test(
            "I have just 300 euros",
            "Please confirm, your trip details: - To: I want to go to London - from: I am from Paris - departure date: 2023-03-25,  - returning date: 2023-03-28. - Your budget is: I have just 300 euros. Is this correct? (1) Yes or (2) No"
            )

    # Test une annulation de réservation
    async def test_booking_cancel(self):
        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)


        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)

        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hy", "What can I help you with today?")
        await adapter.test("I want to book a flight to Paris", "From what city will you be travelling?")
        await adapter.test("Cancel", "Cancelling")

    # Test une réservation en fournissant toutes les informations en une seule fois
    async def test_booking_one_shot(self):
        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)


        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)

        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hello", "What can I help you with today?")
        await adapter.test(
            "Book me to Chisinau from Paris. I have 500 euros and I want to leave on 25 march 2023 and return back on 28 march 2023. ",
            "Please confirm, your trip details: - To: Chisinau - from: Paris - departure date: 2023-03-25,  - returning date: 2023-03-28. - Your budget is: 500. Is this correct? (1) Yes or (2) No"
            )


'''
if __name__ == "__main__":
    unittest.main()  # pragma: no cover
'''