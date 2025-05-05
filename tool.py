import json
from openai import OpenAI


prompt="How Much is the temperature Mumbai city"

tools= [
    {
        "type":"function",
        "function":{
            "name":"get_info",
            "description":"Use the longitude and latitude and give the temp",
            "parameters":{
                "type":"object",
                "properties":{
                    "latitude":{"type":"string","description":"This is the Latitude of the place"},
                    "longitude":{"type":"string","description":"This is the longitude of the place"}
                },
            },
            "required":["latitude","longitude"],
        },
    }
]

def get_info(longitude,latitude/location):


    return result

def run_conversation(prompt,tools):
    client = OpenAI()
    message = [
        {
            "role":"User",
            "content":prompt
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=message,
        tools=tools,
        tool_choice="auto"
    )
    response_message=response.choices[0].message
    print("\nResponse_message",response_message)
    tool_calls=response_message.tool_calls
    print("\nTool Requeired",tool_calls)

    if tool_calls:
        available_tool={
            "get_info":get_info
        }
        message.append(response_message)
        for tool_call in tool_calls:
            function_name=tool_call.function.name
            function_to_call=available_tool[function_name]
            function_args = json.load(tool_call.function.arguments)
            function_response=function_to_call(
                latitude=function_args.get("latitude"),
                longitude=function_args.get("longitude")
            )
            message.append(
                {
                    "tool_call_id":tool_call.id,
                    "role":"tool",
                    "name":function_name,
                    "content":function_response
                }
            )

        second_response=client.chat.completions.create(
            model="gpt-4",
            messages=message
        )
        response_message=second_response.choices[0].message
