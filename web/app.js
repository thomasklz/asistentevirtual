const messages = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('message');
const sendButton = document.getElementById('send');
const micButton = document.getElementById('mic');
const mode = document.getElementById('mode');
const privacy = document.getElementById('privacy');
const suggestions = document.getElementById('suggestions');
const avatar = document.getElementById('avatar');
const voiceStatus = document.getElementById('voice-status');
const voiceCheckbox = document.getElementById('voice');
let history = [];
let busy = false;
let recognition = null;

function bubble(role, text, error = false) {
  const item = document.createElement('div');
  item.className = `bubble ${role}${error ? ' error' : ''}`;
  const label = document.createElement('small');
  label.textContent = role === 'user' ? 'TÚ' : 'LUMA';
  const content = document.createElement('span');
  content.textContent = text;
  item.append(label, content);
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

function speak(text) {
  if (!voiceCheckbox.checked || !('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'es-EC';
  utterance.rate = .96;
  const spanish = speechSynthesis.getVoices().find(v => v.lang.toLowerCase().startsWith('es'));
  if (spanish) utterance.voice = spanish;
  utterance.onstart = () => { avatar.classList.add('speaking'); voiceStatus.textContent = 'Luma está hablando'; };
  utterance.onend = utterance.onerror = () => { avatar.classList.remove('speaking'); voiceStatus.textContent = 'Lista para conversar'; };
  speechSynthesis.speak(utterance);
}

async function ask(question) {
  const message = question.trim();
  if (!message || busy) return;
  window.speechSynthesis?.cancel();
  avatar.classList.remove('speaking');
  bubble('user', message);
  input.value = '';
  busy = true;
  sendButton.disabled = true;
  avatar.classList.add('thinking');
  voiceStatus.textContent = 'Luma está pensando…';
  const prior = history.slice(-6);
  try {
    const response = await fetch('/api/chat', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message, history:prior})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo responder');
    bubble('assistant', data.reply);
    history.push({role:'user',content:message},{role:'assistant',content:data.reply});
    history = history.slice(-8);
    speak(data.reply);
  } catch (error) {
    bubble('assistant', error.message, true);
    voiceStatus.textContent = 'No se pudo responder';
  } finally {
    busy = false;
    sendButton.disabled = false;
    avatar.classList.remove('thinking');
    input.focus();
    if (!avatar.classList.contains('speaking') && voiceStatus.textContent === 'Luma está pensando…') voiceStatus.textContent = 'Lista para conversar';
  }
}

form.addEventListener('submit', event => { event.preventDefault(); ask(input.value); });
document.getElementById('clear').addEventListener('click', () => {
  window.speechSynthesis?.cancel();
  history = [];
  messages.replaceChildren();
  bubble('assistant', '¡Hola! Soy Luma. ¿Qué te gustaría saber sobre la carrera de Computación?');
  voiceStatus.textContent = 'Lista para conversar';
  avatar.classList.remove('speaking');
  input.focus();
});
voiceCheckbox.addEventListener('change', () => { if (!voiceCheckbox.checked) window.speechSynthesis?.cancel(); });

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (Recognition) {
  recognition = new Recognition();
  recognition.lang = 'es-EC';
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.onresult = event => { const said = event.results[0][0].transcript; input.value = said; ask(said); };
  recognition.onerror = event => { voiceStatus.textContent = `Micrófono: ${event.error}. Puedes escribir tu pregunta.`; };
  recognition.onend = () => micButton.classList.remove('listening');
  micButton.addEventListener('click', () => {
    try { micButton.classList.add('listening'); voiceStatus.textContent = 'Escuchando…'; recognition.start(); }
    catch { micButton.classList.remove('listening'); voiceStatus.textContent = 'El micrófono no está disponible'; }
  });
} else {
  micButton.disabled = true;
  micButton.title = 'Reconocimiento de voz no disponible en este navegador';
}

async function boot() {
  bubble('assistant', '¡Hola! Soy Luma. ¿Qué te gustaría saber sobre la carrera de Computación?');
  try {
    const response = await fetch('/api/status');
    const data = await response.json();
    mode.textContent = data.ai_enabled ? '✦ IA conectada' : '◌ Modo demostración · sin API';
    privacy.textContent = data.ai_enabled
      ? 'Las preguntas se envían a OpenAI; no se guarda la conversación aquí.'
      : 'Modo local: responde con los datos de la carrera y sus docentes.';
    for (const question of ['¿Qué materias hay en primer nivel?', '¿Cuántos niveles tiene la carrera?', '¿Quién dicta Inteligencia artificial?', '¿Qué título se obtiene?']) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = question;
      button.addEventListener('click', () => ask(question));
      suggestions.append(button);
    }
  } catch {
    mode.textContent = 'Sin conexión';
    privacy.textContent = 'No se pudo conectar con el servidor.';
  }
}
boot();
