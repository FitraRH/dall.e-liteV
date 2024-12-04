
# Dream Analyzer Flask App

## Description
The Dream Analyzer Flask App is a web application that allows users to process dream descriptions, generate related images, and analyze the sentiment, keywords, and named entities from the description. Additionally, the app provides options for Text-to-Speech (TTS) generation to describe the analysis.

### Key Features:
- **Dream Processing**: Submit dream descriptions to generate insights such as keywords, nouns, sentiment score, and named entities.
- **Image Generation**: Generate an image related to the dream description using an external image generation API.
- **Sentiment Analysis**: Analyze the sentiment of the dream description using a sentiment analysis pipeline (supports both English and Indonesian languages).
- **Named Entity Recognition (NER)**: Extract named entities from the dream description using the spaCy NLP library.
- **Text-to-Speech**: Optionally, generate an audio file that describes the dream analysis using Google's TTS (Text-to-Speech) API.
- **Multiple Language Support**: The app detects the language of the input and adapts the analysis accordingly.

## Requirements
To run the Dream Analyzer Flask app, ensure that you have the following dependencies installed:

1. **Python 3.x** - The app is built with Python 3.
2. **Flask** - Web framework used for building the web application.
3. **spaCy** - NLP library used for Named Entity Recognition (NER).
4. **Transformers** - For sentiment analysis.
5. **Requests** - Used for making HTTP requests (e.g., image generation).
6. **gTTS** - Google Text-to-Speech library for generating audio.
7. **Langdetect** - Language detection to automatically determine the input language.
8. **Sklearn** - For processing and extracting keywords via TF-IDF.

### Install Dependencies:
You can install the required dependencies using `pip`:

```bash
pip install Flask spacy transformers requests gTTS langdetect scikit-learn
python -m spacy download en_core_web_sm
```

## How to Run the App

1. Clone or download the project repository.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Run the Flask app:

```bash
python app.py
```

4. The app will be hosted locally. Navigate to `http://127.0.0.1:5000/` to start interacting with the app.

## API Endpoints

- **POST `/process_dream`**:
    - Description: Process a dream description.
    - Request Payload:
      ```json
      {
        "dream_description": "My dream was about flying over mountains.",
        "tts_enabled": true
      }
      ```
    - Response:
      ```json
      {
        "nouns": ["dream", "flying", "mountains"],
        "keywords": ["flying", "mountains"],
        "named_entities": [["flying", "NOUN"]],
        "sentiment_score": 0.85,
        "sentiment_label": "POSITIVE",
        "image_path": "rsc/dream_1/generated_image.jpg",
        "language": "en",
        "audio_path": "rsc/dream_1/dream_analysis.mp3"
      }
      ```

- **GET `/get_image`**:
    - Description: Get the generated image of the dream.
    - Parameters: `image_path` (path to the image file).
    - Example: `GET /get_image?image_path=rsc/dream_1/generated_image.jpg`

- **GET `/get_audio`**:
    - Description: Get the generated audio for the dream analysis.
    - Parameters: `audio_path` (path to the audio file).
    - Example: `GET /get_audio?audio_path=rsc/dream_1/dream_analysis.mp3`

## File Structure
```
/rsc/                # Contains generated results for dreams (images, audio, text files).
    /dream_1/
        generated_image.jpg
        dream_result.txt
        dream_analysis.mp3
/requirements.txt    # List of dependencies for the app.
app.py               # Main Flask app file.
index.html           # Frontend HTML file.
```

## Contributing
Feel free to fork the repository and contribute improvements. If you have any suggestions or find issues, open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
