import React, { useState, useEffect } from 'react';
import './App.css';
// import axios from 'axios';

function ChatApp({screen}) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [voices, setVoices] = useState([]);
    const [recognition, setRecognition] = useState(null);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [translatedTexts, setTranslatedTexts] = useState({});

    useEffect(() => {
        // Voice recognition setup
        if ('webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.webkitSpeechRecognition;
            const recognitionInstance = new SpeechRecognition();
            recognitionInstance.continuous = false;
            recognitionInstance.interimResults = false;
            recognitionInstance.lang = 'en-US';

            recognitionInstance.onresult = (event) => {
                const result = event.results[0][0].transcript;
                setInput(result);
                recognitionInstance.stop();
            };

            recognitionInstance.onerror = (event) => {
                console.error('Error occurred in recognition: ', event.error);
            };

            setRecognition(recognitionInstance);
        } else {
            alert('Speech recognition not supported in this browser.');
        }

        // Voices setup
        const handleVoicesChanged = () => {
            setVoices(speechSynthesis.getVoices());
        };

        speechSynthesis.onvoiceschanged = handleVoicesChanged;
        handleVoicesChanged();

        return () => {
            speechSynthesis.onvoiceschanged = null;
        };
    }, []);

    const speech = (text) => {
        if (!text) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = voices[2];

        if (isSpeaking) {
            speechSynthesis.cancel();
            setIsSpeaking(false);
        } else {
            speechSynthesis.speak(utterance);
            setIsSpeaking(true);
            utterance.onend = () => setIsSpeaking(false);
        }
    };

    const sendMessage = async () => {
        if (!input.trim()) return;
    
        const userMessage = { role: 'user', content: input };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setLoading(true);
        setInput("");
    
        let endpoint = '';
        var keyword = input.split('-')[1]; // Extract keyword after the first dash
        console.log(keyword);
    
        if (input.startsWith("video-") ) {
            endpoint = 'http://localhost:5000/extract-videos';
        } else if (input.startsWith("youtube-")) {
            endpoint = 'http://localhost:5000/search-videos';
        } else {
            endpoint = 'http://localhost:5000/qa_chat';
            keyword = input;
        }
        // Prepare the chat history for the request
        const chatHistory = messages.map(msg => ({ role: msg.role, content: msg.content }));
    
    try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ keyword,'chat_history':chatHistory }),
                // body: JSON.stringify({'keyword': keyword}),
            });
            // console.log("reponse sent to backend");
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            console.log(data);
    
            // Check if we are dealing with video links
            if (input.startsWith("video-") || input.startsWith("youtube-")) {
                if (data.video_links && data.video_links.length > 0) {
                    const videoMessages = data.video_links.map(link => ({
                        role: 'ai',
                        content: link,
                        isVideo: true
                    }));
                    setMessages(prevMessages => [...prevMessages, ...videoMessages]);
                } else if (data.youtube_link && data.youtube_link.length > 0) {
                    const youtubeMessage = data.youtube_link.map(link =>({
                        role: 'ai',
                        content: link,
                        isVideo: true
                    }));
                    console.log(youtubeMessage);
                    setMessages((prevMessages) => [...prevMessages, ...youtubeMessage]);
                    console.log(messages);
                } else {
                    alert('No video links found. Please try a different keyword.');
                }
            } else {
                // Handle AI response
                const aiMessage = { role: 'ai', content: data.answer };
                setMessages((prevMessages) => [...prevMessages, aiMessage]);
            }
        } catch (error) {
            console.error('Error fetching response from server:', error);
        } finally {
            setLoading(false);
        }
    };
    const youtubeLink = () => {
        setInput("youtube-" + input);
        
        // Set a delay of 1 second (1000 milliseconds)
        setTimeout(() => {
            const youtubeButton = document.getElementById('youtubeBtn');
            if (youtubeButton) {
                youtubeButton.click();
            }
        }, 500);
        setTimeout(() => {setInput("");  // Adjust the delay time here (in milliseconds)
        }, 500);
    };

    const startVoiceInput = () => {
        if (recognition) {
            recognition.start();
        }
    };
    
    const replaceAsterisksWithBold = (text) =>{
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }
    const replaceAsterisksWithBoldForSpeech = (text) =>{
        return text.replace(/\*\*(.*?)\*\*/g, '$1');
    }

    const translateMessage = async (text, index) => {
        if (!text) return;
    
        const maxWords = 50;  // Set your word limit per chunk
        const words = text.split(" ");
        const chunks = [];
    
        // Divide text into chunks of `maxWords` each
        for (let i = 0; i < words.length; i += maxWords) {
            const chunk = words.slice(i, i + maxWords).join(" ");
            chunks.push(chunk);
        }
    
        try {
            const translatedChunks = await Promise.all(
                chunks.map(async (chunk) => {
                    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(chunk)}&langpair=en|ta`;
                    const response = await fetch(url);
                    const data = await response.json();
    
                    if (data.responseStatus === 200) {
                        return data.responseData.translatedText;
                    } else {
                        console.error("Translation error:", data);
                        return "";  // Handle error by returning an empty string for this chunk
                    }
                })
            );
    
            // Combine the translated chunks into a single text
            const fullTranslatedText = translatedChunks.join(" ");
            
            setTranslatedTexts((prev) => ({
                ...prev,
                [index]: fullTranslatedText,
            }));
    
        } catch (error) {
            console.error("Error fetching translation:", error);
        }
    };
    
//<span className='speech-icon' onClick={ youtubeLink} aria-label="Speak message">
//<img width="24" height="24" src="https://img.icons8.com/?size=100&id=19318&format=png&color=000000" alt="youtube" /></span>
    return (
        <div className="chat-container">
            <strong><h1>CHAT WITH PDF</h1></strong>
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index}>
                        <div className={`message ${msg.role}`}>
                            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
                            {msg.isVideo ? (
                                <iframe
                                    width='100%'
                                    height='270px'
                                    src={msg.content}
                                    frameBorder="0"
                                    allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                ></iframe>
                            ) : (
                                <pre dangerouslySetInnerHTML={{ __html: translatedTexts[index] || replaceAsterisksWithBold(msg.content) }} />
                            )}
                        </div>
                        {msg.role === 'ai' && !msg.isVideo && (
                            <>
                                <span className='speech-icon' onClick={() => speech(replaceAsterisksWithBoldForSpeech(msg.content))} aria-label="Speak message">
                                    <img width="20" height="16" src="https://img.icons8.com/windows/32/speaker.png" alt="speaker" />
                                </span>
                                <span className='translate-icon' style={{ margin: "2px" }} 
                                    onClick={() => {
                                        if (translatedTexts[index]) {
                                            setTranslatedTexts((prev) => {
                                                const newTexts = { ...prev };
                                                delete newTexts[index];
                                                return newTexts;
                                            });
                                        } else {
                                            translateMessage(replaceAsterisksWithBold(msg.content), index);
                                        }
                                    }}>
                                    <img width="24" height="24" src="https://img.icons8.com/?size=100&id=13647&format=png&color=000000" alt="translation" />
                                </span>
                                
                            </>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="message ai">
                        <strong>AI:</strong>
                        <pre>Loading...</pre>
                    </div>
                )}
            </div>
            <div className="input-area">
                <span onClick={startVoiceInput} aria-label="Voice Input" style={{ marginTop: '5px' }}>
                    <img width="24" height="24" src="https://img.icons8.com/material-sharp/24/microphone--v1.png" alt="microphone--v1" />
                </span>
                <textarea
    value={input}
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
    placeholder="Type your message..."
    style={{ }}
/>

                <button onClick={sendMessage} id='youtubeBtn'>Send</button>
            </div>
        </div>
    );
}

export default ChatApp;
