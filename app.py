# Import necessary libraries
import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import ollama


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div([
    html.H1('RAG for Scientific Papers', style={'textAlign': 'center'}),
    html.Div([
        html.Div(id='chat-output', style={
            'width': '100%',
            'height': '600px',
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
    ], style={'width': '80%', 'margin': 'auto'}),
    dcc.Store(id='store-input-value')  # Store to hold the input value temporarily
])

# Function to interact with ollama API
def get_response_from_ollama(user_input):
    try:
        response = ollama.generate(model='llama3', prompt=user_input)
        response_text = response['response']
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

# Callback to display user message immediately and store the input value
@app.callback(
    [Output('chat-output', 'children', allow_duplicate=True),
     Output('chat-input', 'value'),
     Output('store-input-value', 'data')],
    [Input('send-button', 'n_clicks'),
     Input('chat-input', 'n_submit')],
    [State('chat-input', 'value'),
     State('chat-output', 'children')],
    prevent_initial_call=True
)
def update_user_message(n_clicks, n_submit, input_value, current_output):
    if n_clicks > 0 or n_submit:
        if not input_value:
            return current_output, '', None

        # Add user's message to the chat output
        new_message_user = html.Div([html.B("User: "), f"{input_value}"], className="message-bubble-user")
        if current_output is None:
            current_output = []
        current_output.append(new_message_user)

        # Store the input value for the bot response
        return current_output, '', input_value

    return current_output, input_value, None

# Callback to get bot response and update chat output
@app.callback(
    Output('chat-output', 'children'),
    [Input('store-input-value', 'data')],
    [State('chat-output', 'children')]
)
def update_bot_response(stored_input, current_output):
    if stored_input:
        # Get response from ollama API
        ollama_response = get_response_from_ollama(stored_input)

        # Add ollama's response to the chat output
        new_message_bot = html.Div([html.B("LLM: "), f"{ollama_response}"], className="message-bubble-bot")
        current_output.append(new_message_bot)

    return current_output

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
