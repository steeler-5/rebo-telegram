from config import client
from memory import extract_fact, save_facts, build_memory_string, load_facts
from coin_info import get_coin_info, get_coin_info_cmc
from code_runner import run_code_snippet
from brave_search_tool import brave_search_tool
from web_search import perform_duckduckgo_search, should_search_web
from datetime import datetime, timezone, timedelta
import json

bot_facts = load_facts()

SYSTEM_IDENTITY = """
You are Beau’s AI partner, co-developer, and assistant. Your name is Rebo.
You speak naturally and helpfully — like ChatGPT — not like a robot.
You are intelligent, curious, and think before acting.
You can run Python code, fetch crypto prices, and search the web.
Only use tools when necessary. If you're unsure what the user meant, ask them to clarify.
Do not overuse web search. Only search when a real answer requires fresh or external info.
Summarize web results conversationally. If no good sources are found, say so honestly.
Assume timezone is America/New_York (Eastern Time) when giving date and time.
"""

def get_datetime_info():
    est_offset = timedelta(hours=-4)
    est_time = datetime.now(timezone.utc) + est_offset
    return est_time.strftime("It is currently %A, %B %d, %Y at %I:%M %p Eastern Time.")

def summarize_search_results(raw_results, topic):
    lines = raw_results.strip().split('\n')
    snippets = [line for line in lines if '-' in line and 'http' not in line]
    if not snippets:
        return "I checked the web, but couldn’t find anything useful or current."

    joined_snippets = "\n".join(snippets[:5])
    summary_prompt = [
        {"role": "system", "content": f"You are a smart summarizer. Your job is to read 3–5 news snippets about {topic} and summarize them into a single short update."},
        {"role": "user", "content": f"Snippets:\n{joined_snippets}\n\nWrite a short summary of what’s going on with {topic}."}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=summary_prompt
    )
    return response.choices[0].message.content.strip()

def chat_with_bot(message, history=None):
    global bot_facts

    facts_string = build_memory_string(bot_facts)

    messages = [{"role": "system", "content": SYSTEM_IDENTITY + "\nKnown facts:\n" + facts_string}]
    if history:
        for user, bot in history:
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": bot})
    messages.append({"role": "user", "content": message})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_coin_info",
                "description": "Fetch the live price and market data for a cryptocurrency using CoinGecko.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Name or symbol of the cryptocurrency."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_coin_info_cmc",
                "description": "Fetch live market data from CoinMarketCap for a cryptocurrency (fallback or alternative source).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Name or symbol of the coin."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "brave_search_tool",
                "description": "Use Brave Search API to fetch high-quality web results for current news or topics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What the user wants to search for."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "perform_duckduckgo_search",
                "description": "Perform a real-time DuckDuckGo web search for user queries. Only use this if the user is clearly asking for current news or something that requires up-to-date information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term or question."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_code_snippet",
                "description": "Execute a Python code snippet and return the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Python code prefixed with 'run code:'."}
                    },
                    "required": ["message"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_datetime_info",
                "description": "Get the current system date and time in human-readable format.",
                "parameters": {"type": "object", "properties": {}}
            }
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    choice = response.choices[0]
    reply = choice.message.content or ""

    key, value = extract_fact(message)
    if key and value:
        bot_facts[key] = value
        save_facts(bot_facts)
        write_fact(key, value)
        if "remember" in message.lower():
            memory_confirmation = f"Got it — I’ll remember that {key.replace('_', ' ')} is {value}.\n\n"
            return memory_confirmation + reply

    if choice.finish_reason == "tool_calls":
        tool_call = choice.message.tool_calls[0]
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments or '{}')

        if func_name == "get_coin_info":
            result = get_coin_info(args["query"])
            return f"Here’s the latest on {args['query']}:\n{result}"
        elif func_name == "get_coin_info_cmc":
            result = get_coin_info_cmc(args["query"])
            return f"CoinMarketCap data for {args['query']}:\n{result}"
        elif func_name == "brave_search_tool":
            return brave_search_tool(args["query"])
        elif func_name == "perform_duckduckgo_search":
            raw = perform_duckduckgo_search(args["query"])
            return summarize_search_results(raw, args["query"])
        elif func_name == "run_code_snippet":
            return run_code_snippet(args["message"])
        elif func_name == "get_datetime_info":
            return get_datetime_info()

    return reply
