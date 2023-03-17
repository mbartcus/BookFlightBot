# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        start_date: str = None,
        end_date: str = None,
        budget: int = None,
        #travel_date: str = None,
        #unsupported_airports=None,
    ):
        #if unsupported_airports is None:
        #    unsupported_airports = []
        self.destination = destination
        self.origin = origin
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        #self.travel_date = travel_date
        #self.unsupported_airports = unsupported_airports
