document.addEventListener("DOMContentLoaded", function() {
    MathJax.typesetPromise().catch(function (err) {
        console.error("MathJax typesetting failed: " + err.message);
    });

    document.getElementById("chat-form").addEventListener("submit", function(event) {
        event.preventDefault();
        const userMessage = document.getElementById("user_message").value.trim();
        if (userMessage.length === 0) {
            alert("Please enter a message before submitting!");
            return;
        }

        fetch("/", {
            method: "POST",
            body: new FormData(this)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response Data:", data);

            let usr_msg = document.createElement("div");
            usr_msg.classList.add("chat-message", "user-message");
            usr_msg.innerHTML = data.usr_msg;

            let ai_msg = document.createElement("div");
            ai_msg.classList.add("chat-message", "assistant-message");
            ai_msg.innerHTML = data.ai_msg;

            document.getElementById("chat_messages").appendChild(usr_msg);
            document.getElementById("chat_messages").appendChild(ai_msg);

            document.getElementById("user_message").value = "";

            MathJax.typesetPromise().catch(function (err) {
                console.error("MathJax typesetting failed: " + err.message);
            });
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });

    document.getElementById("clear-form").addEventListener("submit", function(event) {
        event.preventDefault();
        fetch("/reset_chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.querySelectorAll(".chat-message").forEach(msg => msg.remove());
                document.querySelectorAll("br").forEach(br => br.remove());

                MathJax.typesetPromise().catch(function (err) {
                    console.error("MathJax typesetting failed: " + err.message);
                });
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});

function moveToBottom() {
    const userMessage = document.getElementById("user_message");
    userMessage.focus();
    window.scrollTo(0, document.body.scrollHeight);
}