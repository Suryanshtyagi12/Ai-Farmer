function startRecognition(lang) {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        alert("Your browser does not support Speech Recognition.");
        return;
    }
    const recognition = new Recognition();
    recognition.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.interimResults = false;
    
    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        // Sending the transcript back to Streamlit via a custom event or hidden button
        const streamlitChatInput = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
        if (streamlitChatInput) {
            streamlitChatInput.value = text;
            streamlitChatInput.dispatchEvent(new Event('input', { bubbles: true }));
            // Trigger the submit button
            const submitBtn = window.parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
            if (submitBtn) submitBtn.click();
        }
    };
    recognition.start();
}

function speakText(text, lang) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    synth.speak(utterance);
}
