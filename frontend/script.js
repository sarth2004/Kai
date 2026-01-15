async function askAI() {
    const prompt = document.getElementById("prompt").value;
    const responseBox = document.getElementById("response");
    const button = document.querySelector("button");

    if (!prompt.trim()) {
        responseBox.innerText = "Please enter a question.";
        return;
    }

    button.disabled = true;
    responseBox.innerText = "Thinking...";

    try {
        const res = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: prompt })
        });

        const data = await res.json();

        // Display answer
        responseBox.innerHTML = `<pre>${data.answer}</pre>`;

        // Display source if available
        if (data.source) {
            responseBox.innerHTML += `
            
Source: <a href="${data.source}" target="_blank">${data.source}</a>`;
        }

    } catch (error) {
        responseBox.innerText = "Backend not reachable.";
    }

    button.disabled = false;
}
