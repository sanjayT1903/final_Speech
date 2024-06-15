import os
import psycopg2
from gensim.utils import simple_preprocess
from gensim.models import Word2Vec
import numpy as np
from PyPDF2 import PdfReader
import requests
#https://learn.microsoft.com/en-us/answers/questions/1377984/install-cuda-toolkit-and-drivers-in-vm
import json
import streamlit as st

url = "http://40.78.124.98:11434/api/generate"

# prompt_Side_Characters = """
# Respond in JSON with the format {Side_Characters: [{Name: "Character1_NAME"}, {Name: "Character2_NAME"}, ...]}.
# THERE MAY BE MULTIPLE CHARACTERS, ONLY DESCRIBE their MULTIPLE NAMES.
# Example: {Side_Characters: [{Name: "Gabe"}, {Name: "Mack"}]}.

# If the side characters described by context are not given, then ALWAYS respond with Only {Side_Characters: NULL}.
# Remember there are possibly MULTIPLE side characters. 

# Examples:
# 1. Given side characters Gabe and Mack:
#    {Side_Characters: [{Name: "Gabe"}, {Name: "Mack"}]
# 2. Given side characters Anna, Bob, and Carla:
#    {Side_Characters: [{Name: "Anna"}, {Name: "Bob"}, {Name: "Carla"}]}
# 3. Given no side characters:
#    {Side_Characters: NULL}
# """

# question_basis = ["Who is the main character?",
# "How does the main character have as hair color?",
# "How does the main character have as height?",
# "Who is the Mentor character?",
# "Who are the side-Characters excluding mentor characters? (A side character is anyone that assists the Main character) DO NOT include MENOTR characters",
# "What was the call to action?"]


# question_format = ["Respond in JSON with the format {Main_Character: MAIN_CHARACTER_NAME} (Let this be string) OR if the MAIN_CHARACTER_NAME is unknown/null then ALWAYS respond with Only  {Main_Character_Name: NULL})",
# "Respond in JSON with the format {Main_Character_Hair: MAIN_CHARACTER_HAIR} (Let this be string Color ) OR if the hair color is unknown then ALWAYS respond with Only {Main_Character_Hair: NULL} )",
# "Respond in JSON with the format {Main_Character_Height: MAIN_CHARACTER_HEIGHT}  OR if the height is unknown then ALWAYS respond with only {Main_Character_Height: NULL} )",
# "Respond in JSON with the format {Mentor: MENTOR_NAME}  OR if the mentor character described by context is not given then ALWAYS respond with Only {Mentor: NULL})",
# prompt_Side_Characters, #this is a string above, many hallucinations here
# "Respond in JSON with the format, this should be A single PHRASE, ALWAYS less than 25 words! {Call_To_Action: CALL_TO_ACTION} (Let this be string or Null)"]

format_string_v2= (
"Answer the following questions as best you can. You have access to the following tools and using the Context provided above Only:\n\n"
"ALWAYS use the following format and respond with nothing else:\n\n"
"ALWAYS have Unknown Values as Null\n\n"
    "NEVER add any parameters outside the given ones. Any unknown values should be NULL only"
)

question_format_v2 = [
    '''
    Respond IN JSON to all Characters of the Story with Only
    {
        "Characters": [
            {"name": "Character_Name", "age": "Character_Age", "hair": "Character_Hair_Color", "height": "Character_Height", "role": "Character_Role"}
        ]
    }
    Note:
    - FOLLOW THIS EXACT FORMAT.
    - Character_Role can only be "Main" (only one main character), "Mentor" (mentor character), "Antagonist" (character working against the main character), or "Side Character" (if none of the above).
    - Character_Height should be described as 5 feet 3 inches or 5'3".
    - Any unclear information for a character must be Null.
    - DO NOT ADD ANY JSON OUTSIDE OF THE GIVEN FORMAT.
    ''',
    '''
    Respond in JSON with the format:
    {
        "Call_To_Action": "CALL_TO_ACTION"
    }
    - The call to action should be a single phrase, always less than 25 words.
    - It should describe what caused the main character to act.
    - Let this be a string or Null.
    - DO NOT ADD ANY JSON OUTSIDE OF THE GIVEN FORMAT.
    '''
]





def prompt_model(context):
    data = {
    "model": "mistral",
    "prompt": context,
    "format": "json", #still need to mkae sure you prompt the model to output jSON
    "stream": False
    }
    response_str = requests.post(url, json=data) # bascially prompting the model and then sorting the response
    clean_response_str = response_str.json()
    x = clean_response_str['response']

    response_json = json.loads(x)
    #print(response_json)
    return response_json


def craft(user_input): 
    #model, allChunks = initDocs(documents_path )
    context_submit = ""
    lister = []

    
    story = user_input
            # construct the prompt with the strings above with the similarty search
    for index in range(len(question_format_v2)): # one at a time to avoid hallucinations
                context_submit = ""
                #str_context = question_basis[index] + "\n"+question_format[index] 
                str_context_V2 = question_format_v2[index] 
    
                context_submit += "Work on this {" + story + "}" + '\n'
                context_submit +=format_string_v2
                context_submit += str_context_V2 + '\n'
                k = prompt_model(context_submit)
                print(k)
                lister.append(k) #THIS CONTIANS EACH JSON OUTPUT
    #print(lister)
    print("Here is it all")
            
    for indexer in range(len(lister)):
        print(lister[indexer]) #need to grab each json and try to combine and pass ur choice?

# new_story = """
# In the mystical realm of Althera, there lived a young mage named Kieran. At 14 years old, Kieran stood 5'6" tall, with dark brown hair and piercing blue eyes. Kieran was known for his extraordinary magical abilities and a heart full of compassion. One day, a terrible calamity struck Althera when an evil warlock named Zarek unleashed a plague of shadows upon the land.

# An ancient sage named Thalor, whose age was unknown but had a wise and calming presence, took Kieran under his guidance. Thalor, with his silver hair and long, flowing robes, became Kieran's mentor, teaching him the ways of ancient magic and the history of Althera.

# Kieran's loyal friends, Arin and Mira, joined him on this perilous mission. Arin, a 15-year-old archer with a height of 5'7", had no distinctive features but was known for his unwavering bravery. Mira, also 14, with her blonde hair and 5'5" frame, possessed a brilliant mind and quick wit. Together, they formed a determined team, committed to saving their homeland.

# Their journey took them through dark forests, over treacherous mountains, and into forgotten ruins. Along the way, they encountered mystical beings and overcame formidable challenges. The bond between Kieran, Arin, and Mira grew stronger with each obstacle they faced.

# As they approached Zarek's fortress, Thalor revealed an ancient relic – the Amulet of Light – capable of dispelling the shadows. With newfound hope, Kieran and his friends prepared for the final battle against Zarek. The clash of magic and valor echoed through the land.

# In the end, Kieran's courage and Thalor's wisdom triumphed. The Amulet of Light vanquished Zarek's dark powers, lifting the plague from Althera. Light and peace were restored, and the people of Althera celebrated their heroes. Kieran, Arin, and Mira were hailed as saviors, and Thalor's teachings became legendary.

# Through their bravery and friendship, Kieran and his companions saved Althera and brought hope to their people. Their tale was passed down through generations, inspiring others to stand against evil with courage and unity.
# """


# craft(new_story)

#'Unknown', None, "NULL", 
