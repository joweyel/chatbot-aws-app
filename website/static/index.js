document.addEventListener("DOMContentLoaded", function() {
    MathJax.typesetPromise().catch(function (err) {
      console.error("MathJax typesetting failed: " + err.message);
    });
    document.getElementById("chat-form").addEventListener("submit", function (event) {

        const userMessage = document.getElementById("user_message").value.trim();
        if (userMessage.length === 0) {  // Check if the textarea is empty
            alert("Please enter a message before submitting!");
            event.preventDefault();
            return;
        }

        event.preventDefault();
        fetch("/", {
          method: "POST",
          body: new FormData(this)
        }).then(
            response => response.json()
        ).then(data => {
            // Create new div for user message
            let usr_msg = document.createElement("div");
            // Add attributre: class="chat-message user-message"
            usr_msg.classList.add("chat-message", "user-message");
            usr_msg.innerHTML = data.usr_msg;

            // Create new div for assistant message
            let ai_msg = document.createElement("div");
            // Add attributre: class="chat-message ai-message"
            ai_msg.classList.add("chat-message", "assistant-message");
            ai_msg.innerHTML = data.ai_msg;

            // Append user message to chat-box
            document.getElementById("chat_messages").appendChild(usr_msg);
            document.getElementById("chat_messages").appendChild(ai_msg);
            document.getElementById("user_message").value = "";

            MathJax.typesetPromise();
        }).catch(error => {
            console.error("Error: " + error);
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("clear-form").addEventListener("submit", function (event) {
        event.preventDefault();
        fetch(
            "/reset_chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        ).then(
            response => response.json()
        ).then(
            data => {
                if (data.status === "success") {
                    document.querySelectorAll(".chat-message").forEach(msg => msg.remove());
                    document.querySelectorAll("br").forEach(br => br.remove());
                    MathJax.typesetPromise().catch(function (err) {
                        console.error("MathJax typesetting failed: " + err.message);
                    });
                }
            }
        ).catch(error => {
            console.error("Error: ", error);
        });
    });
});

function moveToBottom() {
    const userMessage = document.getElementById("user_message");
    userMessage.focus();
    
    // Scroll to the bottom of the page directly
    window.scrollTo(0, document.body.scrollHeight);
}