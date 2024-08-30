import json
from typing import Sequence, List, Dict
from llama_index.llms.openai import OpenAI
import nest_asyncio
from dotenv import load_dotenv
from pathlib import Path
from typing import List
from shiny import App, Inputs, Outputs, Session, reactive, render, ui, req
import shutil
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader, get_response_synthesizer
from llama_index.core import DocumentSummaryIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from nature_retrive import main
from GoogleScholar import main_google
from pubmed_central import main_pubmed_central
from knowledge_graph import knowledge_graph
import pandas as pd
import networkx as nx
import plotly.graph_objs as go
import matplotlib.colors as mcolors
import itertools
from shinywidgets import output_widget, render_widget 
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import asyncio

nest_asyncio.apply()
load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
api_key = os.getenv('OPENAI_API_KEY')


TITLE = " "

# Layout -----

desired_directory = Path(__file__).parent / "www"

page_dependencies = ui.tags.head(
    ui.tags.link(rel = "stylesheet",type = "text/css",href = "style.css")
)
# Navbar -----
app_ui = ui.page_navbar(
    ui.nav_panel(
        "Nature",
        ui.card(ui.panel_title("Hello AI Medical Writer!!"),
            ui.card_header(f"""Enter keywords in the "Enter your keywords" field and click "Search" to retrieve related articles from various publication websites. 
                           The links to the articles will be provided for you to copy and download if desired. Automatic summaries of the articles will be displayed below. 
                           Use the chatbot in the sidebar to ask questions about the articles by typing your question and pressing "Enter". 
                           The chatbot will respond based on the content of the retrieved articles."""),
                full_screen=True,
                ),
        ui.page_sidebar(
            ui.sidebar(
                ui.input_text("keyword1", "Enter your keywords:",placeholder = "Antibiotic resistance", autocomplete='on', spellcheck=True),
                ui.input_numeric("numbers1", "Max Number of Articles:", 10, min=1, max=100),
                ui.popover(ui.input_task_button("btn1", "Search"),
                            "Please note: The responses are based on the latest published articles."
                            ),
                 ui.output_text_verbatim("process_descrip1"),
                 ui.output_plot("plot11",
                            click=True,
                            dblclick=True,  
                            hover=True,
                            brush=True),
                ui.chat_ui("chat1"),
                width=500
                   
            ),
            ui.output_text_verbatim("process_descrip2"),
            output_widget("plot111")
            ),
        ui.card(
           ui.card_header(f"""
                       Disclaimer: The information and summaries provided by this application are for informational purposes only and are not intended as professional advice. 
                       The app retrieves articles from various publication websites and generates summaries using automated methods, specifically the GPT-4o model. 
                       The accuracy, completeness, and reliability of the information may vary. 
                       The developers of this app are not responsible for any errors, omissions, or actions taken based on the content provided by this application."""),
        full_screen=True,
    )
        ),
    
    ui.nav_panel(
        "Google Scholar",
        ui.card(ui.panel_title("Hello AI Medical Writer!!"),
            ui.card_header(f"""Enter keywords in the "Enter your keywords" field and click "Search" to retrieve related articles from various publication websites. 
                           The links to the articles will be provided for you to copy and download if desired. Automatic summaries of the articles will be displayed below. 
                           Use the chatbot in the sidebar to ask questions about the articles by typing your question and pressing "Enter". 
                           The chatbot will respond based on the content of the retrieved articles."""),
                full_screen=True,
                ),
        ui.page_sidebar(
            ui.sidebar(
                ui.input_text("keyword2", "Enter your keywords:",placeholder = "Antibiotic resistance", autocomplete='on', spellcheck=True),
                ui.input_numeric("numbers2", "Max Number of Articles:", 10, min=1, max=100),
                ui.popover(ui.input_task_button("btn2", "Search"),
                            "Please note: The responses are based on a mixture of both recent and older published articles."
                            ),
                ui.output_text_verbatim("process_descrip3"),
                ui.output_plot("plot2",
                            click=True,
                            dblclick=True,  
                            hover=True,
                            brush=True),
                ui.page_fillable(
                    ui.chat_ui("chat2"),  
                    fillable_mobile=True),
                #ui.chat_ui("chat2"),
                width=500
                   
            ),
             ui.card(ui.output_text_verbatim("process_descrip4")),
             output_widget("plot22")
            ),
        ui.card(
           ui.card_header(f"""
                       Disclaimer: The information and summaries provided by this application are for informational purposes only and are not intended as professional advice. 
                       The app retrieves articles from various publication websites and generates summaries using automated methods, specifically the GPT-4o model. 
                       The accuracy, completeness, and reliability of the information may vary. 
                       The developers of this app are not responsible for any errors, omissions, or actions taken based on the content provided by this application."""),
        full_screen=True,
    )
        ),
    
    ui.nav_panel(
        "PubMed Central",
        ui.card(ui.panel_title("Hello AI Medical Writer!!"),
            ui.card_header(f"""Enter keywords in the "Enter your keywords" field and click "Search" to retrieve related articles from various publication websites. 
                           The links to the articles will be provided for you to copy and download if desired. Automatic summaries of the articles will be displayed below. 
                           Use the chatbot in the sidebar to ask questions about the articles by typing your question and pressing "Enter". 
                           The chatbot will respond based on the content of the retrieved articles."""),
                full_screen=True,
                ),
        ui.page_sidebar(
            ui.sidebar(
                ui.input_text("keyword3", "Enter your keywords:",placeholder = "Antibiotic resistance", autocomplete='on', spellcheck=True),
                ui.input_numeric("numbers3", "Max Number of Articles:", 10, min=1, max=100),
                ui.popover(ui.input_task_button("btn3", "Search"),
                            "Please note: The responses are based on the most relevent articles based on your keywords."
                            ),
                ui.output_text_verbatim("process_descrip5"),
                ui.output_plot("plot3",
                            click=True,
                            dblclick=True,  
                            hover=True,
                            brush=True),
                ui.page_fillable(
                    ui.chat_ui("chat3"),
                    fillable_mobile=True),
                #ui.chat_ui("chat2"),
                width=500
                   
            ),
            ui.card(ui.output_text_verbatim("process_descrip6")),
            output_widget("plot4")
            ),
        ui.card(
           ui.card_header(f"""
                       Disclaimer: The information and summaries provided by this application are for informational purposes only and are not intended as professional advice. 
                       The app retrieves articles from various publication websites and generates summaries using automated methods, specifically the GPT-4o model. 
                       The accuracy, completeness, and reliability of the information may vary. 
                       The developers of this app are not responsible for any errors, omissions, or actions taken based on the content provided by this application."""),
        full_screen=True,
    )
        ),
    
    title = ui.tags.div(
        ui.img(src = "baye.jpg",height = "70px",
               Style = "margin.5px;"),
        ui.h4(" "  + TITLE),
        Style = "display:flex;-webkit-filter: drop-show(2px 2px 2px #222);"
    ),
    bg = "#effb11",
    inverse = False,
    header = page_dependencies
    
)

def server(input: Inputs, output: Outputs, session: Session):
    
    ############################# Nature document retrieval ######################## 
    @output
    @render.text()
    @reactive.event(input.btn1, ignore_none=True)
    async def process_descrip1():
        
        with ui.Progress(min=1, max=18) as p:
            p.set(1, message="Search in progress", detail="This may take a while...")
            max_articles = input.numbers1() or 10
            webpage = main(f"{input.keyword1()}", max_articles)
            
        return webpage
    
    @output
    @render.text()
    @reactive.event(input.btn1, ignore_none=True)
    async def process_descrip2():
        
        with ui.Progress(min=1, max=18) as p:
            p.set(1, message="Searching for related articles", detail="This may take a while...")
            def list_text_files(directory):
                text_files = [os.path.splitext(file)[0] for file in os.listdir(directory) if file.endswith('.txt')]
                text_files.sort(key=lambda x: int(x.split('_')[1]))
                
                return text_files

            directory = 'articles'
            wiki_titles = list_text_files(directory)
            
            p.set(5, message="Searching for related articles", detail="This may take a while...")
            city_docs = []
            for wiki_title in wiki_titles:
                docs = SimpleDirectoryReader(
                    input_files=[f"articles/{wiki_title}.txt"]
                ).load_data()
                docs[0].doc_id = wiki_title
                city_docs.extend(docs)
                
            shutil.rmtree(directory)
            
            chatgpt = OpenAI(temperature=0, model="gpt-4o-mini")
            splitter = SentenceSplitter(chunk_size=1024)
            p.set(10, message="summarizing articles", detail="This may take a while...")
            response_synthesizer = get_response_synthesizer(
                response_mode="tree_summarize", use_async=True)
            doc_summary_index = DocumentSummaryIndex.from_documents(
                city_docs,
                llm=chatgpt,
                transformations=[splitter],
                response_synthesizer=response_synthesizer,
            show_progress=True,
        )
            p.set(15, message="summarizing articles", detail="This may take a while...")
            messages = []
            for i, title in enumerate(wiki_titles, start=1):
                summary = doc_summary_index.get_document_summary(title)
                messages.append(f"{i}. {summary}")
                messages.append("\n")
            
            doc_summary_index.storage_context.persist("index")  
            
            infomat = "\n".join(messages)
            
            with open("summaries.txt", 'w', encoding='utf-8') as file:
                file.write(infomat)
            p.set(18, message="summarizing articles", detail="This may take a while...")
        return "\n".join(messages)
    
    @render.plot(alt="A histogram")
    @reactive.event(input.btn1, ignore_none=True)
    async def plot11():
        
        with ui.Progress(min=18, max=20) as p:
            p.set(19, message="Analysing summarise", detail="This may take a while...")
        
            try:
                with open("summaries.txt", "r") as file:
                    infomat = file.read()
            except Exception as e:
                print(f"Error reading the file: {e}")
                return
            wordcloud = WordCloud(width=1200, height=1000, background_color='white').generate(infomat)
            
            fig, ax = plt.subplots(figsize=(14, 10))  # Creating plot
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            ax.set_title("")
            
            p.set(20, message="generating word cloud", detail="This may take a while...")
        
        return fig 
    

    @render_widget 
    @reactive.event(input.btn1, ignore_none=True) 
    def plot111():
        with ui.Progress(min=20, max=22) as p:
            p.set(21, message="Generating resarch network", detail="This may take a while...")
            fig = knowledge_graph("summaries.txt")
            
            p.set(22, message="Generating resarch network", detail="This may take a while...")
        
        return fig
    
    
    chat1 = ui.Chat(id="chat1")  
    chat1.ui()
    @chat1.on_user_submit  
    async def _(): 
        
        storage_context = StorageContext.from_defaults(persist_dir="index")
        doc_summary_index = load_index_from_storage(storage_context)
        
        query_engine = doc_summary_index.as_query_engine(
            response_mode="tree_summarize", use_async=True
        )
        response = query_engine.query(f"{chat1.user_input()}")
        output = f"{response}"
        
        await chat1.append_message(output)
        
        
   #############################Google scholar document retrieval ########################    

    @output
    @render.text()
    @reactive.event(input.btn2, ignore_none=True)
    async def process_descrip3():
        
        with ui.Progress(min=1, max=18) as p:
            p.set(1, message="Search in progress", detail="This may take a while...")
            max_articles = input.numbers2()
            webpage = main_google(f"{input.keyword2()}", max_articles)
            
        return webpage
    
    @output
    @render.text()
    @reactive.event(input.btn2, ignore_none=True)
    async def process_descrip4():
        
        with ui.Progress(min=1, max=18) as p:
            p.set(1, message="summarizing articles", detail="This may take a while...")
            def list_text_files(directory):
                text_files = [os.path.splitext(file)[0] for file in os.listdir(directory) if file.endswith('.txt')]
                text_files.sort(key=lambda x: int(x.split('_')[1]))
                
                return text_files

            directory = 'articles'
            wiki_titles = list_text_files(directory)
            
            p.set(5, message="summarizing articles", detail="This may take a while...")
            city_docs = []
            for wiki_title in wiki_titles:
                docs = SimpleDirectoryReader(
                    input_files=[f"articles/{wiki_title}.txt"]
                ).load_data()
                docs[0].doc_id = wiki_title
                city_docs.extend(docs)
                
            shutil.rmtree(directory)
            
            chatgpt = OpenAI(temperature=0, model="gpt-4o-mini")
            splitter = SentenceSplitter(chunk_size=1024)
            p.set(10, message="summarizing articles", detail="This may take a while...")
            response_synthesizer = get_response_synthesizer(
                response_mode="tree_summarize", use_async=True)
            doc_summary_index = DocumentSummaryIndex.from_documents(
                city_docs,
                llm=chatgpt,
                transformations=[splitter],
                response_synthesizer=response_synthesizer,
            show_progress=True,
        )
            p.set(15, message="summarizing articles", detail="This may take a while...")
            messages = []
            for i, title in enumerate(wiki_titles, start=1):
                summary = doc_summary_index.get_document_summary(title)
                messages.append(f"{i}. {summary}")
                messages.append("\n")
            
            doc_summary_index.storage_context.persist("index")
            p.set(18, message="summarizing articles", detail="This may take a while...")   
            
            infomat = "\n".join(messages)
            
            with open("summaries.txt", 'w', encoding='utf-8') as file:
                file.write(infomat)
                
        return "\n".join(messages)
    
    
    @render.plot(alt="A histogram")
    @reactive.event(input.btn2, ignore_none=True)
    async def plot2():
        
        with ui.Progress(min=18, max=10) as p:
        
            try:
                with open("summaries.txt", "r") as file:
                    infomat = file.read()
            except Exception as e:
                print(f"Error reading the file: {e}")
                return
            wordcloud = WordCloud(width=1200, height=1000, background_color='white').generate(infomat)
            
            fig, ax = plt.subplots(figsize=(14, 10))  # Creating plot
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            ax.set_title("")
            
            p.set(20, message="summarizing articles", detail="This may take a while...")
        
        return fig
    
    @render_widget 
    @reactive.event(input.btn2, ignore_none=True) 
    def plot22():
        with ui.Progress(min=20, max=22) as p:
            p.set(21, message="summarizing articles", detail="This may take a while...")
            fig = knowledge_graph("summaries.txt")
            
            p.set(22, message="summarizing articles", detail="This may take a while...")
        
        return fig
    
    
    chat2 = ui.Chat(id="chat2")  
    chat2.ui()
    @chat2.on_user_submit  
    async def _(): 
        
        storage_context = StorageContext.from_defaults(persist_dir="index")
        doc_summary_index = load_index_from_storage(storage_context)
        query_engine = doc_summary_index.as_query_engine(
            response_mode="tree_summarize", use_async=True
        )
        response = query_engine.query(f"{chat2.user_input()}")
        output = f"{response}"
        
        await chat2.append_message(output)
        
          
  #############################Pubmed Central document retrieval########################    
 
    @output
    @render.text()
    @reactive.event(input.btn3, ignore_none=True)
    async def process_descrip5():
        
        with ui.Progress(min=1, max=18) as p:
            p.set(1, message="Search in progress", detail="This may take a while...")
            max_articles = input.numbers3()
            webpage = main_pubmed_central(f"{input.keyword3()}", max_articles)
            
        return webpage
    
    @output
    @render.text()
    @reactive.event(input.btn3, ignore_none=True)
    async def process_descrip6():
        
        with ui.Progress(min=1, max=18) as p:
            p.set(1, message="summarizing articles", detail="This may take a while...")
            def list_text_files(directory):
                text_files = [os.path.splitext(file)[0] for file in os.listdir(directory) if file.endswith('.txt')]
                text_files.sort(key=lambda x: int(x.split('_')[1]))
                
                return text_files

            directory = 'articles'
            wiki_titles = list_text_files(directory)
            
            p.set(5, message="summarizing articles", detail="This may take a while...")
            city_docs = []
            for wiki_title in wiki_titles:
                docs = SimpleDirectoryReader(
                    input_files=[f"articles/{wiki_title}.txt"]
                ).load_data()
                docs[0].doc_id = wiki_title
                city_docs.extend(docs)
                
            shutil.rmtree(directory)
            
            chatgpt = OpenAI(temperature=0, model="gpt-4o-mini")
            splitter = SentenceSplitter(chunk_size=1024)
            p.set(10, message="summarizing articles", detail="This may take a while...")
            response_synthesizer = get_response_synthesizer(
                response_mode="tree_summarize", use_async=True)
            doc_summary_index = DocumentSummaryIndex.from_documents(
                city_docs,
                llm=chatgpt,
                transformations=[splitter],
                response_synthesizer=response_synthesizer,
            show_progress=True,
        )
            p.set(15, message="summarizing articles", detail="This may take a while...")
            messages = []
            for i, title in enumerate(wiki_titles, start=1):
                summary = doc_summary_index.get_document_summary(title)
                messages.append(f"{i}. {summary}")
                messages.append("\n")
            
            doc_summary_index.storage_context.persist("index")  
            
            infomat = "\n".join(messages)
            
            with open("summaries.txt", 'w', encoding='utf-8') as file:
                file.write(infomat)
            p.set(18, message="summarizing articles", detail="This may take a while...")
        return "\n".join(messages)
    
    
    @render.plot(alt="A histogram")
    @reactive.event(input.btn3, ignore_none=True)
    async def plot3():
        
        with ui.Progress(min=18, max=20) as p:
        
            try:
                with open("summaries.txt", "r") as file:
                    infomat = file.read()
            except Exception as e:
                print(f"Error reading the file: {e}")
                return
            wordcloud = WordCloud(width=1200, height=1000, background_color='white').generate(infomat)
            
            fig, ax = plt.subplots(figsize=(14, 10))  # Creating plot
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            ax.set_title("")
            
            p.set(20, message="summarizing articles", detail="This may take a while...")
        
        return fig 
    

    @render_widget 
    @reactive.event(input.btn3, ignore_none=True) 
    def plot4():
        with ui.Progress(min=20, max=22) as p:
            p.set(21, message="summarizing articles", detail="This may take a while...")
            fig = knowledge_graph("summaries.txt")
            
            p.set(22, message="summarizing articles", detail="This may take a while...")
        
        return fig
    
    
    chat3 = ui.Chat(id="chat3")  
    chat3.ui()
    @chat3.on_user_submit  
    async def _(): 
        
        storage_context = StorageContext.from_defaults(persist_dir="index")
        doc_summary_index = load_index_from_storage(storage_context)
        query_engine = doc_summary_index.as_query_engine(
            response_mode="tree_summarize", use_async=True
        )
        response = query_engine.query(f"{chat3.user_input()}")
        output = f"{response}"
        
        await chat3.append_message(output)
        
    
www_dir = Path(__file__).parent / "www"
app = App(app_ui,server,static_assets=www_dir)