const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const chatBox = document.getElementById("chat-box");

sendBtn.onclick = async () => {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    const botMsg = addMessage("Waking up server…", "bot");

    try {
        const res = await fetch("https://three-tap-backend.onrender.com/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: text })
        });

        const data = await res.json();
        botMsg.textContent = data.answer || "No response.";
    } catch (err) {
        botMsg.textContent = "Server not responding.";
    }
};

function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.className = "message " + type;
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}
