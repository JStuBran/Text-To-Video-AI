import os
from openai import OpenAI
import json

# Use OpenAI GPT-4o for script generation
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_API_KEY)
model = "gpt-4o"

def generate_script(topic):
    prompt = (
        """You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
        Your facts shorts are concise, each lasting less than 50 seconds (approximately 140 words). 
        They are incredibly engaging and original. When a user requests a specific type of facts short, you will create it.

        For instance, if the user asks for:
        Weird facts
        You would produce content like this:

        Weird facts you don't know:
        - Bananas are berries, but strawberries aren't.
        - A single cloud can weigh over a million pounds.
        - There's a species of jellyfish that is biologically immortal.
        - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.
        - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.
        - Octopuses have three hearts and blue blood.

        You are now tasked with creating the best short script based on the user's requested type of 'facts'.

        Keep it brief, highly interesting, and unique.

        Stictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {"script": "Here is the script ..."}
        """
    )

    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        script = json.loads(content)["script"]
    except Exception as e:
        print(f"JSON parsing error: {e}")
        print(f"Content: {content}")
        try:
            # Try to fix common escape issues
            json_start_index = content.find('{')
            json_end_index = content.rfind('}')
            content_cleaned = content[json_start_index:json_end_index+1]
            
            # Fix common escape issues
            content_cleaned = content_cleaned.replace('\\', '\\\\')  # Escape backslashes
            content_cleaned = content_cleaned.replace('\\"', '"')   # Fix escaped quotes
            content_cleaned = content_cleaned.replace('\\n', '\\\\n')  # Fix newlines
            content_cleaned = content_cleaned.replace('\\t', '\\\\t')  # Fix tabs
            
            script = json.loads(content_cleaned)["script"]
        except Exception as e2:
            print(f"Fallback parsing also failed: {e2}")
            # Last resort: extract content between quotes after "script":
            import re
            match = re.search(r'"script":\s*"([^"]*(?:\\"[^"]*)*)"', content)
            if match:
                script = match.group(1).replace('\\"', '"')
            else:
                raise Exception(f"Could not parse script from OpenAI response: {content}")
    return script
