const token1 =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzMyODI3NzM0fQ.Sxvm3KsMaZL59Zbbn-Wd1pVFikCMl3Ne3wTrQz8nFik"
const token2 =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwiZXhwIjoxNzMyODI3OTI3fQ.YSsck8rAv0I80hnw2DQBkv53EGoWxAmuAPfXycL2RMI"
const roomId = 3;

const ws1 = new WebSocket(`ws://localhost:8001/api/v1/chat/ws/${roomId}?token=${token1}`);
const ws2 = new WebSocket(`ws://localhost:8001/api/v1/chat/ws/${roomId}?token=${token2}`);

ws1.onopen = () => {
    console.log('Usuário 1 conectado ao WebSocket');
};

ws2.onopen = () => {
    console.log('Usuário 2 conectado ao WebSocket');
};

ws1.onmessage = (event) => {
    displayMessage(event.data, 'chat1');
    displayMessage(event.data, 'chat2');
};

ws2.onmessage = (event) => {
    displayMessage(event.data, 'chat1');
    displayMessage(event.data, 'chat2');
};

ws1.onerror = (error) => {
    console.error('Erro no WebSocket Usuário 1:', error);
};

ws2.onerror = (error) => {
    console.error('Erro no WebSocket Usuário 2:', error);
};

ws1.onclose = () => {
    console.log('Conexão WebSocket Usuário 1 fechada');
};

ws2.onclose = () => {
    console.log('Conexão WebSocket Usuário 2 fechada');
};

function sendMessage(ws, inputId) {
    const input = document.getElementById(inputId);
    const message = input.value;
    if (message) {
        ws.send(JSON.stringify({ content: message }));
        input.value = '';
    }
}

function displayMessage(data, chatId) {
    const chat = document.getElementById(chatId);
    const message = JSON.parse(data);
    console.log('Mensagem recebida:', message);
    const sender = message.sender_username || message.user_id || 'Desconhecido';
    const content = message.content || 'Mensagem não disponível';
    chat.innerHTML += `<div><strong>${sender}:</strong> ${content}</div>`;
    chat.scrollTop = chat.scrollHeight;
}
