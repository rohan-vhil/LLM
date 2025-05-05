import json
from openai import OpenAI
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup Open-Meteo client with retry and caching
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define the tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_info",
            "description": "Get current temperature using latitude and longitude.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "string",
                        "description": "Latitude of the location"
                    },
                    "longitude": {
                        "type": "string",
                        "description": "Longitude of the location"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        }
    }
]

# Actual function to get temperature using Open-Meteo
def get_info(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m"
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        current = response.Current()
        temperature = current.Variables(0).Value()
        timestamp = current.Time()

        return f"Current temperature at ({latitude}, {longitude}) is {temperature}°C as of timestamp {timestamp}."
    except Exception as e:
        return f"Failed to retrieve temperature: {str(e)}"

# Run the conversation with OpenAI function call
def run_conversation(prompt, tools):
    client = OpenAI()

    messages = [
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = getattr(response_message, "tool_calls", None)

    if tool_calls:
        messages.append(response_message)

        available_tools = {
            "get_info": get_info
        }

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_to_call = available_tools[function_name]

            function_response = function_to_call(
                latitude=function_args.get("latitude"),
                longitude=function_args.get("longitude")
            )

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })

        second_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        final_message = second_response.choices[0].message
        print("\n Final Response:\n", final_message.content)
    else:
        print("\n Model Response:\n", response_message.content)

# Example prompt
run_conversation("What's the temperature in Mumbai?", tools)
