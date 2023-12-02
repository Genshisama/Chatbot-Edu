from flask import Flask, render_template, request, jsonify
import time
import openai

api_key = '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'
last_request_time = time.time()

app = Flask(__name__)

chat_messages = []

@app.route('/')
def chatbot_interface():
    initial_prompt = "Hello"
    return render_template('chatbot.html', chat_messages = chat_messages, initial_prompt = initial_prompt)

@app.route('/send_message',methods=['POST'])
def send_message():
    user_input = request.json['user_input']
    
    chatbot_response = rate_limited_assistant(f"You: {user_input}\nAssistant:")
    
    time.sleep(1)
    
    chat_messages.append(f"<div class='message user-message'><strong>You:</strong> {user_input} </div>")
    chat_messages.append(f"<div class='message user-message'><strong>Assistant:</strong> {chatbot_response} </div>")

    
    return jsonify({'response': chatbot_response})
    
def rate_limited_assistant(prompt):
    global last_request_time
    elapsed_time = time.time() - last_request_time
    
    if elapsed_time < 5:
        time.sleep(5-elapsed_time)
        
    last_request_time = time.time()
    
    openai.api_key = api_key
    
    response_text = ""

    try:
        while True:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages = [
                    {
                        "role": "system", "content": """
                            You are a game developer. You generate python scripts for games based on what people describe to you.
                            """
                    },
                    {"role": "user", "content": "Hi, I need you to help me create a game in Python. I will describe the game to you and you will give me back a script for it. Be sure to always include code for a GUI that appears for me to play the game on. Is that ok?"},
                    {"role": "assistant", "content": "Yes of course. Please provide me with some details on this game!"},
                ]

            )
            
            current_response = response.choices[0].message.content
            
            response_text += current_response
            
            if '.' in current_response or len(response_text.split()) >= 50:
                break
            
            prompt = current_response

    except Exception as e:
        print(f"Error during API request: {e}")
        
    return response_text


if __name__ == '__main__':
    app.run(debug=True)