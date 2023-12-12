from flask import Flask, render_template, request, jsonify
import time
import openai
import json

with open('config.json') as config_file:
    config_data = json.load(config_file)

api_key = config_data.get('api_key')
last_request_time = time.time()

app = Flask(__name__)

chat_messages = []

@app.route('/')
def chatbot_interface():
    initial_prompt = "Welcome! Ask me anything about historical facts, and I'll do my best to provide you with detailed and accurate information. Feel free to start the conversation with a historical question."
    return render_template('chatbot.html', chat_messages = chat_messages, initial_prompt = initial_prompt)

@app.route('/send_message',methods=['POST'])
def send_message():
    user_input = request.json['user_input']
    
    if not user_input:
        return jsonify({'response': "Sorry but it seems like you forgot to input your inquiry. Please try again."})
        
    chatbot_response = rate_limited_assistant(f"You: {user_input}\nAssistant:")
    
    time.sleep(1)
    
    chat_messages.append(f"<div class='message user-message'><strong>You:</strong> {user_input} </div>")
    chat_messages.append(f"<div class='message user-message'><strong>Assistant:</strong> {chatbot_response} </div>")

    
    return jsonify({'response': chatbot_response})
    
def rate_limited_assistant(prompt):
    global last_request_time
    elapsed_time = time.time() - last_request_time
    
    if elapsed_time < 5:
        time.sleep(5 - elapsed_time)
        
    last_request_time = time.time()
    
    openai.api_key = api_key
    
    response_text = ""

    messages = [
        {
            "role": "system", "content": """
                You are a historical facts expert, well-versed in various historical events and figures. 
                You can provide detailed and accurate answers to history-related questions. 
                If the query is related to a different subject (e.g., math, science, literature), clearly state that you are focused on history and unable to assist with inquiries outside this field. 
                If the question pertains to an unrelated topic, kindly express that it falls outside your field of expertise. 
                If the user asks who or what you are, say you are a historical expert.
                Answer briefly unless asked for explanation.
                Greet user in brief manner.
            """
        },
        {
            "role": "user", "content": """
                You are a user seeking information from a historical facts expert. 
                Feel free to ask any history-related questions, and the expert will provide you with accurate information.
            """
        },
        {"role": "assistant", "content": "Yes, I understand. Please go ahead and ask any historical question, and I'll do my best to provide you with detailed and accurate information."}
    ]
    
    try:
        while True:
            message = prompt
            if message:
                messages.append(
                    {"role": "user", "content": message},
                )
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            current_response = response.choices[0].message.content
            
            response_text += current_response
            
            if '.' in current_response or len(response_text.split()) >= 50:
                break
            
            messages[-1]["content"] = f"You: {current_response}\nAssistant:"
            print(messages)
    except Exception as e:
        print(f"Error during API request: {e}")
        
    return response_text


if __name__ == '__main__':
    app.run(debug=True)