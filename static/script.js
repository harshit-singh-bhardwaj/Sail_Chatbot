function addMessage(content, sender) {
    const chat = document.getElementById("chat");
    const message = document.createElement("div");
    message.className = "message " + sender;
    message.textContent = content;
    chat.appendChild(message);
    chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
    const userInput = document.getElementById("user-input");
    const message = userInput.value;
    if (message.trim() === "") return;

    addMessage(message, "user");
    userInput.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.response, "bot");
    })
    .catch(error => {
        addMessage("Error: Could not reach the server.", "bot");
        console.error("Error:", error);
    });
}
