from flask import Flask, render_template, request, jsonify, send_file
import spacy
from transformers import pipeline
import requests
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from gtts import gTTS
import mimetypes
import time
from langdetect import detect

# Load the English language model
nlp_en = spacy.load("en_core_web_sm")

# Load the sentiment analysis pipeline
sentiment_pipeline_en = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
sentiment_pipeline = pipeline("sentiment-analysis", model="w11wo/indonesian-roberta-base-sentiment-classifier")

# Flask app
app = Flask(__name__)

# Ensure the 'rsc' directory exists
if not os.path.exists('rsc'):
    os.makedirs('rsc')

# Initialize dream counter
dream_counter_file = 'rsc/dream_counter.txt'
if os.path.exists(dream_counter_file):
    with open(dream_counter_file, 'r') as file:
        dream_counter = int(file.read().strip())
else:
    dream_counter = 0

def generate_dream_folder():
    global dream_counter
    dream_counter += 1
    with open(dream_counter_file, 'w') as file:
        file.write(str(dream_counter))
    folder_name = f"rsc/dream_{dream_counter}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def generate_image_filename(dream_folder):
    return os.path.join(dream_folder, "generated_image.jpg")

def generate_image(dream_description):
    max_retries = 5
    delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        response = requests.get(f"https://image.pollinations.ai/prompt/{dream_description}")
        if response.status_code == 200:
            return response.content
        elif response.status_code == 429:  # Too Many Requests
            print(f"Queue full. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
        else:
            print(f"Error: Failed to generate image. Status code: {response.status_code}, Response: {response.text}")
            break

    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_dream', methods=['POST'])
def process_dream():
    data = request.get_json()
    dream_description = data.get('dream_description', '')
    tts_enabled = data.get('tts_enabled', False)

    try:
        # Detect the language of the input
        detected_lang = detect(dream_description)

        # Choose the appropriate NLP model and sentiment pipeline based on the language
        if detected_lang == 'id':
            nlp = None  # No spaCy model for Indonesian
            sentiment_pipeline = sentiment_pipeline
            lang = 'id'
        else:
            nlp = nlp_en
            sentiment_pipeline = sentiment_pipeline_en
            lang = 'en'

        dream_folder = generate_dream_folder()
        image_filename = generate_image_filename(dream_folder)
        
        # Generate the image
        image_content = generate_image(dream_description)
        if image_content:
            with open(image_filename, "wb") as image_file:
                image_file.write(image_content)
        else:
            return jsonify({"error": "Failed to generate image"}), 500

        # Process dream description with appropriate NLP model
        if lang == 'en':
            nouns, keywords = extract_nouns_and_keywords(dream_description, nlp)
            named_entities = extract_named_entities(dream_description, nlp)
        else:
            # For Indonesian, only extract sentiment (no named entities or keywords)
            nouns, keywords, named_entities = [], [], []

        sentiment_score, sentiment_label = analyze_sentiment(dream_description, sentiment_pipeline)

        result = {
            "nouns": nouns,
            "keywords": keywords,
            "named_entities": named_entities,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "image_path": image_filename,
            "language": lang
        }

        # Save dream result to a file
        dream_result_file = os.path.join(dream_folder, "dream_result.txt")
        with open(dream_result_file, 'w') as file:
            file.write(f"Dream description: {dream_description}\n")
            file.write(f"Nouns: {', '.join(nouns)}\n")
            file.write(f"Keywords: {', '.join(keywords)}\n")
            file.write(f"Named Entities: {', '.join([f'{ent[0]} ({ent[1]})' for ent in named_entities])}\n")
            file.write(f"Sentiment Score: {sentiment_score}\n")
            file.write(f"Sentiment Label: {sentiment_label}\n")
            file.write(f"Image Path: {image_filename}\n")

        # Generate and save audio if TTS is enabled
        if tts_enabled:
            try:
                audio_text = f"Dream analysis: Nouns: {', '.join(nouns)}. Keywords: {', '.join(keywords)}. Sentiment: {sentiment_label} with score {sentiment_score}."
                audio_filename = os.path.join(dream_folder, "dream_analysis.mp3")

                tts = gTTS(text=audio_text, lang=lang)                                                                                                                                                                                                                                                                
                tts.save(audio_filename)

                if os.path.exists(audio_filename):
                    print(f"Audio file created successfully: {audio_filename}")
                    result["audio_path"] = audio_filename
                else:
                    print(f"Failed to create audio file: {audio_filename}")
            except Exception as e:
                print(f"Error in TTS processing: {str(e)}")

        return jsonify(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_audio', methods=['GET'])
def get_audio():
    audio_path = request.args.get('audio_path', '')
    try:
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404
        mime_type, _ = mimetypes.guess_type(audio_path)
        return send_file(audio_path, mimetype=mime_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_image')
def get_image():
    image_path = request.args.get('image_path', '')
    try:
        if not os.path.exists(image_path):
            return jsonify({"error": "Image file not found"}), 404
        mime_type, _ = mimetypes.guess_type(image_path)
        return send_file(image_path, mimetype=mime_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_nouns_and_keywords(description, nlp):
    doc = nlp(description)
    nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
    lemmatized_text = " ".join([token.lemma_.lower() for token in doc])
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([lemmatized_text])
    feature_names = vectorizer.get_feature_names_out()
    dense = vectors.todense()
    denselist = dense.tolist()
    tfidf_dict = {feature_names[i]: denselist[0][i] for i in range(len(feature_names))}
    sorted_tfidf = sorted(tfidf_dict.items(), key=lambda item: item[1], reverse=True)
    num_keywords = 5
    extracted_keywords = [word for word, score in sorted_tfidf[:num_keywords]]
    return nouns, extracted_keywords

def extract_named_entities(description, nlp):
    doc = nlp(description)
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    if not named_entities:
        named_entities = [(token.text, "PROPER_NOUN") for token in doc if token.pos_ == "PROPN"]
    
    return named_entities

def analyze_sentiment(description, sentiment_pipeline):
    sentiment_results = sentiment_pipeline(description)
    sentiment_score = sentiment_results[0]['score']
    sentiment_label = sentiment_results[0]['label']

    if sentiment_label == "NEGATIVE":
        adjusted_score = -sentiment_score
    elif sentiment_label == "POSITIVE":
        adjusted_score = sentiment_score
    else:
        adjusted_score = 0

    return adjusted_score, sentiment_label

if __name__ == '__main__':
    app.run(debug=True)
