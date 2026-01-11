let sessionId = null;

const uploadScreen = document.getElementById("upload-screen");
const chatScreen = document.getElementById("chat-screen");

const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const pdfInput = document.getElementById("pdf-input");

const chatWindow = document.getElementById("chat-window");
const chatMessage = document.getElementById("chat-message");
const sendBtn = document.getElementById("send-btn");

// ===== Upload PDF =====

uploadBtn.onclick = async () => {
  const file = pdfInput.files[0];
  if (!file) {
    alert("Выберите PDF файл");
    return;
  }

  uploadStatus.textContent = "Документ анализируется, пожалуйста подождите...";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/upload/", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    sessionId = data.session_id;

    uploadScreen.classList.remove("active");
    chatScreen.classList.add("active");

    addBotMessage("Клиническая рекомендация загружена. Опишите клинический случай.");

  } catch (err) {
    uploadStatus.textContent = "Ошибка при загрузке";
  }
};

// ===== Chat =====

sendBtn.onclick = sendMessage;
chatMessage.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

async function sendMessage() {
  const text = chatMessage.value.trim();
  if (!text) return;

  addUserMessage(text);
  chatMessage.value = "";

  const res = await fetch("/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: text
    })
  });

  const data = await res.json();

  if (data.type === "questions") {
    data.content.forEach(q => addBotMessage(q));
  }

  if (data.type === "final_decision") {
    addBotMessage("Итоговая тактика лечения:");
    addBotMessage(data.content);
  }
}

function addUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message user";
  div.innerHTML = formatText(text);
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addBotMessage(text) {
  const div = document.createElement("div");
  div.className = "message bot";
  div.innerHTML = formatText(text);
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}
