document.addEventListener("DOMContentLoaded", () => {
    const sendButton = document.getElementById("send-button");
    const ttsButton = document.getElementById("tts-button");
    const resetButton = document.getElementById("reset-button");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");
    const coverContainer = document.getElementById("cover-container");
    const enterChatButton = document.getElementById("enter-chat-button");
    const chatContainer = document.getElementById("chat-container");

    let ttsEnabled = true;
    let waitingForDream = false;
    let waitingForConfirmation = false;

    function addMessage(content, isUser = false) {
        const template = document.getElementById(isUser ? 'user-message-template' : 'bot-message-template');
        const messageElement = template.content.cloneNode(true).children[0];
        messageElement.textContent = content;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoadingMessage() {
        const loadingDiv = document.createElement("div");
        loadingDiv.id = "loading";
        loadingDiv.textContent = "Thinking...";
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeLoadingMessage() {
        const loadingDiv = document.getElementById("loading");
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    function displayDreamAnalysis(data) {
        const template = document.getElementById('dream-analysis-template');
        const analysisElement = template.content.cloneNode(true).children[0];
        
        analysisElement.querySelector('.nouns').textContent = data.nouns.join(", ");
        analysisElement.querySelector('.keywords').textContent = data.keywords.join(", ");
        analysisElement.querySelector('.named-entities').textContent = data.named_entities.map(ne => `${ne[0]} (${ne[1]})`).join(", ");
        analysisElement.querySelector('.sentiment-score').textContent = data.sentiment_score;
        analysisElement.querySelector('.sentiment-label').textContent = data.sentiment_label;

        if (data.image_path) {
            const imageElement = analysisElement.querySelector('.dream-image');
            imageElement.src = `/get_image?image_path=${data.image_path}&t=${new Date().getTime()}`;
            imageElement.style.display = 'block';
        }

        chatMessages.appendChild(analysisElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (ttsEnabled && data.audio_path) {
            const audio = new Audio(`/get_audio?audio_path=${encodeURIComponent(data.audio_path)}`);
            audio.play();
        }
    }

    function botResponse(userMessage) {
        addLoadingMessage();
        setTimeout(() => {
            removeLoadingMessage();
            if (waitingForDream) {
                addMessage("Thank you for sharing your text. I'll analyze it for you now.");
                analyzeDream(userMessage);
                waitingForDream = false;
            } else if (waitingForConfirmation) {
                if (userMessage.toLowerCase().match(/yes|yeah|sure|okay|ok|yep|yea/)) {
                    addMessage("Great! Please describe your text in as much detail as you can remember.");
                    waitingForDream = true;
                    waitingForConfirmation = false;
                } else {
                    addMessage("Alright. If you'd like to analyze a text later, just let me know.");
                    waitingForConfirmation = false;
                }
            } else {
                const lowerMessage = userMessage.toLowerCase();
                if (lowerMessage.includes("hello") || lowerMessage.includes("hi")) {
                    addMessage("Hello! It's nice to meet you. I'm the text Analyzer AI. How can I assist you today?");
                } else if (lowerMessage.includes("analyze") || lowerMessage.includes("dream")) {
                    addMessage("I'm here to help you analyze your text. Would you like to share a text with me for analysis?");
                    waitingForConfirmation = true;
                } else {
                    addMessage("I'm here to help you analyze your text. Would you like to share a text with me for analysis?");
                    waitingForConfirmation = true;
                }
            }
        }, 1000);
    }

    function analyzeDream(dreamDescription) {
        addLoadingMessage();
        fetch("/process_dream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ dream_description: dreamDescription, tts_enabled: ttsEnabled })
        })
        .then(response => response.json())
        .then(data => {
            removeLoadingMessage();
            if (data.error) {
                addMessage(`I apologize, but there was an error analyzing your text : ${data.error}`);
            } else {
                displayDreamAnalysis(data);
                addMessage("I hope this analysis provides some insight into your text. Is there anything else you'd like to know about the text?");
            }
        })
        .catch(error => {
            removeLoadingMessage();
            addMessage(`I'm sorry, but an error occurred while analyzing your text: ${error.message}`);
        });
    }

    sendButton.addEventListener("click", () => {
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        addMessage(userMessage, true);
        userInput.value = "";
        botResponse(userMessage);
    });

    ttsButton.addEventListener("click", () => {
        ttsEnabled = !ttsEnabled;
        ttsButton.textContent = "TTS: " + (ttsEnabled ? "ON" : "OFF");
    });

    resetButton.addEventListener("click", () => {
        chatMessages.innerHTML = "";
        addMessage("Hello! I'm the Text Analyzer AI. How can I assist you today?");
        waitingForDream = false;
        waitingForConfirmation = false;
    });

    enterChatButton.addEventListener("click", () => {
        coverContainer.style.display = "none";
        chatContainer.style.display = "flex";
        addMessage("Hello! I'm the Text Analyzer AI. How can I assist you today?");
    });
});
