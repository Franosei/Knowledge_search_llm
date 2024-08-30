import os
import sys
from PyPDF2 import PdfWriter, PdfReader
import PyPDF2
import json
import streamlit as st
import pandas as pd
from docx import Document
import time
from openai import OpenAI
import tiktoken
import openai
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def llm(text, system_message, delimiter="####", print_response=False, retries=3, sleep_time=10):
    while retries > 0:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{delimiter}{text}{delimiter}"}
        ]
        max_tokens = 128000 - (len(text) + len(system_message)) - 13
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0
            )
            response = completion.choices[0].message.content
            if print_response:
                print(response)
            break
        except openai.RateLimitError as e:
            print('Catching RateLimitError, retrying in 1 minute...')
            retries -= 1
            time.sleep(sleep_time)
    return response
