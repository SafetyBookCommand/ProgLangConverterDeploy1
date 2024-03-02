import os
import json
from string import punctuation as PUNCTUATION

# import expressvpn  # !!!!
from openai import OpenAI
from dotenv import load_dotenv

# change this data afterward
ADDITIONAL_DATA_FOLDER = ("/Users/cryptogazer/Desktop/IAs/Efim CS "
                          "IA/prototype1_2/prototype2_1_venv/assets/additional_data")
LANGUAGES = ("Python", "Java", "C++", 'C', "C#", "JavaScript", "Pascal", "Ruby", "Go", "Dart", "Swift", "Kotlin")
WITH_JSON = False

if WITH_JSON:
    print("WITH JSON\n")
    API_KEYS_FILE = "api_keys.json"
    OPENAI_API_KEY_NAME = "openai_efim_ks_key_pavel"

    with open(os.path.join(ADDITIONAL_DATA_FOLDER, API_KEYS_FILE)) as json_file:
        api_keys: dict = json.load(json_file)
        OPENAI_API_KEY = api_keys.get(OPENAI_API_KEY_NAME)
else:
    print("WITH ..env:\n")
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)


def get_completion_elements(code: str = '',
                            from_lang: str = '',
                            to_lang: str = '') -> list | dict | str:
    # client = OpenAI(api_key=OPENAI_API_KEY)

    def get_completion(query: str) -> str:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": ("You are a professional and skilled assistant, who can help "
                                "translate the code from one programming language into another one")
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        return completion.choices[0].message.content

    def remove_punctuation(str_: str) -> str:
        return str_.translate(str.maketrans('', '', PUNCTUATION))

    if code and from_lang and to_lang:
        response_fits_from_lang = get_completion(
            (f"Please, check, whether the following code is "
             f"written in {from_lang}: {code}. "
             f"Just give a short response: \"yes\" or \"no\".")
        )
        response_fits_from_lang = remove_punctuation(response_fits_from_lang).lower()
        if response_fits_from_lang.startswith('y'):
            response_text = get_completion(
                (f"Please, convert the code, written in {from_lang} "
                 f"into {to_lang}: \"{code}\"")
            )
            print(response_text)
            response_elements = response_text.split("```")[1:]

            if not response_elements:
                return response_text

            if len(response_elements) > 2:  # if there are surprisingly "```" inside the text in the code
                response_elements = ["```".join(response_elements[:-1])] + [response_elements[-1]]
            return response_elements
        else:
            return {
                2: (f"Your code doesn't relate to {from_lang}!\n"
                    f"or is not clear and understandable!\n")
            }
    elif not code:
        return {
            1: ("Your code field is empty!\n"
                "Please, enter the code!\n")
        }
