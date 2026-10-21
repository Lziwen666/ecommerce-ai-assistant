const chatForm = document.querySelector('#chatForm');
const messageInput = document.querySelector('#messageInput');
const chatBox = document.querySelector('#chatBox');
const history = [];

function addMessage(content, role) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = content;
  wrapper.appendChild(bubble);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(message) {
  const content = message.trim();
  if (!content) return;

  addMessage(content, 'user');
  messageInput.value = '';
  history.push({ role: 'user', content });

  const loading = document.createElement('div');
  loading.className = 'message assistant';
  loading.innerHTML = '<div class="bubble">正在为您查询...</div>';
  chatBox.appendChild(loading);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content, history, use_ai: true })
    });
    if (!response.ok) throw new Error('API request failed');
    const data = await response.json();
    loading.remove();
    addMessage(data.reply, 'assistant');
    history.push({ role: 'assistant', content: data.reply });
  } catch (error) {
    loading.remove();
    const fallback = '服务暂时不可用，请稍后再试，或联系人工客服。';
    addMessage(fallback, 'assistant');
    history.push({ role: 'assistant', content: fallback });
  }
}

chatForm.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage(messageInput.value);
});

document.querySelectorAll('.quick-questions button').forEach((button) => {
  button.addEventListener('click', () => sendMessage(button.dataset.question));
});
