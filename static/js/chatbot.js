// minimal chat UI
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("chat-toggle");
  const box = document.getElementById("chatbox");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const thread = document.getElementById("chat-thread");

  if (!btn || !box || !form) return;

  btn.addEventListener("click", () => {
    box.classList.toggle("open");
    if (box.classList.contains("open")) input?.focus();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendBubble(text, "user");
    input.value = "";
    const reply = await askBot(text);
    appendBubble(reply, "bot");
    box.scrollTop = box.scrollHeight;
  });

  function appendBubble(text, who) {
    const li = document.createElement("div");
    li.className = "chat-bubble " + who;
    li.innerText = text;
    thread.appendChild(li);
  }

  async function askBot(message) {
    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });
      const data = await resp.json();
      return data.reply || "Hmm, no reply.";
    } catch {
      return "Sorry, something went wrong.";
    }
  }
});
