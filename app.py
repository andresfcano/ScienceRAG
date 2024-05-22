# Import necessary libraries
from flask import Flask, stream_with_context, Response
import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import ollama
import json


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div([
    html.H1('RAG for Scientific Papers', style={'textAlign': 'center'}),
    html.Div([
        html.Div(id='chat-output', style={
            'width': '100%',
            'height': '300px',
            'border': '1px solid #d3d3d3',
            'borderRadius': '5px',
            'padding': '10px',
            'marginBottom': '10px',
            'overflowY': 'scroll',
            'backgroundColor': '#f7f7f7'
        }),
        html.Div([
            dcc.Input(id='chat-input', type='text', style={
                'width': '100%',
                'height': '30px',
                'borderRadius': '5px',
                'border': '1px solid #d3d3d3',
                'padding': '5px'
            }),
            html.Button('Send', id='send-button', n_clicks=0, style={
                'width': '14%',
                'height': '30px',
                'marginLeft': '1%',
                'borderRadius': '5px',
                'border': 'none',
                'backgroundColor': '#007bff',
                'color': '#ffffff'
            })
        ], style={'width': '100%', 'display': 'flex'})
    ], style={'width': '80%', 'margin': 'auto'})
])

# Define your SSE endpoint
@app.server.route('/stream')
def stream_responses():
    def generate():
        # Initialize Ollama chat stream with placeholder messages
        stream = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': 'Placeholder message'}],
            stream=True,
        )
        
        # Yield each message as an SSE
        for chunk in stream:
            yield f"data: {json.dumps(chunk['message']['content'])}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

# Callback to update chat output
@app.callback(
    [Output('chat-output', 'children'),
     Output('chat-input', 'value')],
    [Input('send-button', 'n_clicks'),
     Input('chat-input', 'n_submit')],
    [State('chat-input', 'value'),
     State('chat-output', 'children')]
)
def update_output(n_clicks, n_submit, input_value, current_output):
    if n_clicks > 0 or n_submit:
        new_message = html.Div([html.B("User: "), f"{input_value}"], className="message-bubble user-message")
        if current_output:
            current_output.append(new_message)
        else:
            current_output = [new_message]
        return current_output, ''
    return current_output, input_value

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
