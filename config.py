#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 8000 #3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", "c2ad16eb-c106-438c-b487-cfc569117efe")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "9798f35d114b4ddf820c1adbcb4a3b13")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    # myluisfly-authoring.cognitiveservices.azure.com
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "03bbdb7a-ebd4-4ca2-bed4-92dbcf64e331"
    )
