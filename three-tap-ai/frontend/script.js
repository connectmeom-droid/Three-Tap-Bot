// {/* <script>
// const chatBox = document.getElementById("chat-box");

// /* Load chat history */
// window.onload = function () {
//     const saved = localStorage.getItem("chat_history");
//     if (saved) {
//         chatBox.innerHTML = saved;
//         chatBox.scrollTop = chatBox.scrollHeight;
//      }
// };

// function saveChat() {
//     localStorage.setItem("chat_history", chatBox.innerHTML);
// }

// async function sendMessage() {
//     const input = document.getElementById("user-input");
//     const text = input.value.trim();
//     if (!text) return;

//     // User message
//     const userMsg = document.createElement("div");
//     userMsg.className = "message user";
//     userMsg.innerText = text;
//     chatBox.appendChild(userMsg);

//     input.value = "";

//     // Bot message
//     const botMsg = document.createElement("div");
//     botMsg.className = "message bot";
//     botMsg.innerText = "Thinking...";
//     chatBox.appendChild(botMsg);

//     chatBox.scrollTop = chatBox.scrollHeight;
//     saveChat();

//     try {
//         const res = await fetch("http://127.0.0.1:8000/chat", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ question: text })
//         });

//         const data = await res.json();
//         botMsg.innerText = data.answer;

//     } catch {
//         botMsg.innerText = "Server not responding.";
//     }

//     chatBox.scrollTop = chatBox.scrollHeight;
//     saveChat();
// }
// </script> */}
