from chatcompletion import llm
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI
import networkx as nx
import plotly.graph_objs as go
import matplotlib.colors as mcolors
import itertools
import os
import json

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def knowledge_graph(file_path):

    system_message = """You are a text analyst responsible for analyzing the summary of a research article and responsible for finding relationship between keywords.
    The main aim is to derive new key ideas/discoveries from the provided research reviews for key related terms.
    Analyse the full text very carefully since some relationships can be found from differnt article and in that case they should have one  main topic
    To plot the graph using a table format, you can structure the data in a way that lists each connection between a main key words and its subtopics. 
    This table should have two columns: one for the "Main Topic" and another for the "Subtopic". Each row will represent an edge (connection) in the graph.
    Please make sure the entry names are short but very clear and understandable and also make sure the nodes are very important for research discoveries and analysis.
    Please make sure the final JSON can be read by pandas and must be enclosed with [ ].
    Please make sure the final output is JSON with column names, "Main Topic" and "Subtopic".
    """
    with open(file_path, "r") as file:
        infomat = file.read()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": infomat}
        ]
    )

    response = completion.choices[0].message.content


    cleaned_output = response.replace("```json", "").replace("```", "").strip()
    cleaned_json_path = 'cleaned_output.json'

    with open(cleaned_json_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_output)

    df = pd.read_json(cleaned_json_path)

    G = nx.DiGraph()

    for index, row in df.iterrows():
        G.add_node(row['Main Topic'], type='Main Topic')
        G.add_node(row['Subtopic'], type='Subtopic')
        G.add_edge(row['Main Topic'], row['Subtopic'])

    pos = nx.spring_layout(G, iterations=100, k=1)

    colors = itertools.cycle(mcolors.CSS4_COLORS)
    node_colors = {}

    for component in nx.weakly_connected_components(G):
        color = next(colors)
        for node in component:
            node_colors[node] = color

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            size=[], 
            color=[], 
            opacity=0.9,
            line=dict(width=3, color='rgba(0, 0, 0, 0.5)'),
            symbol='circle',
        ))

    # Add the nodes and their positions to the node_trace
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        
        if G.nodes[node]['type'] == 'Main Topic':
            subtopics = [f"{i+1}. {n}" for i, n in enumerate(G.neighbors(node))]
            hover_text = f"{node}<br>Subtopics:<br>" + "<br>".join(subtopics)
            node_trace['text'] += (hover_text,)
        else:
            node_trace['text'] += ('',)
        
        node_size = 30 if G.nodes[node]['type'] == 'Main Topic' else 20
        node_trace['marker']['size'] += (node_size,)
        
        node_color = mcolors.to_rgba(node_colors[node], alpha=0.9)
        node_trace['marker']['color'] += (f"rgba({int(node_color[0]*255)}, {int(node_color[1]*255)}, {int(node_color[2]*255)}, 0.9)",)

    # Pre-create edge traces, initially invisible, and use the color of the main topic
    edge_traces = []
    for edge in G.edges():
        main_topic = edge[0]  # The main topic is the source node of the edge
        color = mcolors.to_rgba(node_colors[main_topic], alpha=0.9)
        
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=2, color=f'rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, {color[3]})'),
            hoverinfo='none',
            mode='lines',
            visible=False
        ))

    # Create buttons for dropdown menu
    buttons = []
    main_topics = sorted([node for node in G.nodes() if G.nodes[node]['type'] == 'Main Topic'])

    for node in main_topics:
        node_edges = [i for i, edge in enumerate(G.edges()) if edge[0] == node]
        button = dict(
            label=node,
            method='update',
            args=[{
                'visible': [False] * len(edge_traces) + [True],
            }]
        )
        for i in node_edges:
            button['args'][0]['visible'][i] = True  # Make the relevant edges visible
            edge_traces[i]['line']['width'] = 6  # Make the edge bold
        buttons.append(button)

    fig = go.Figure(data=edge_traces + [node_trace],
                    layout=go.Layout(
                        title='Interactive Network Graph',
                        titlefont_size=20,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, visible=False), 
                        yaxis=dict(showgrid=False, zeroline=False, visible=False),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        width=800,
                        height=800,
                        updatemenus=[{
                            'type': 'dropdown',
                            'showactive': True,
                            'buttons': buttons,
                        }]
                    ))
    
    return fig
