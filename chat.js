// Tokens JWT para autenticação dos usuários (substitua pelos seus tokens reais (basta fazer login e copiar o token))
const token1 =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzMyODYyNjIzfQ.XqeZS1p0Npnh3B9vQEGM14nH1fm4F8-yzl0k5Ac_kw0"
const token2 =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwiZXhwIjoxNzMyODYyMjk5fQ.ry7WEPk9idVWLc1EkOUUgeA0C2jda8E05RGMAlApdxw"
const roomId = 1 // ID da sala que você deseja usar (deve existir no banco de dados)

// Cria conexões websocket para os dois usuários
const ws1 = new WebSocket(
  `ws://localhost:8001/api/v1/chat/ws/${roomId}?token=${token1}`
)
const ws2 = new WebSocket(
  `ws://localhost:8001/api/v1/chat/ws/${roomId}?token=${token2}`
)

// Eventos de conexão websocket para o usuário 1
ws1.onopen = () => {
  console.log("Usuário 1 conectado ao WebSocket")
  fetchMessageHistory("chat1") // Busca o histórico de mensagens para o chat 1
}

// Eventos de conexão websocket para o usuário 2
ws2.onopen = () => {
  console.log("Usuário 2 conectado ao WebSocket")
  fetchMessageHistory("chat2") // Busca o histórico de mensagens para o chat 2
}

// Recebe mensagens para o usuário 1 e exibe em ambos os chats
ws1.onmessage = (event) => {
  displayMessage(event.data, "chat1")
  displayMessage(event.data, "chat2")
}

// Recebe mensagens para o usuário 2 e exibe em ambos os chats
ws2.onmessage = (event) => {
  displayMessage(event.data, "chat1")
  displayMessage(event.data, "chat2")
}

// Tratamento de erros para o websocket do usuário 1
ws1.onerror = (error) => {
  console.error("Erro no WebSocket Usuário 1:", error)
}

// Tratamento de erros para o websocket do usuário 2
ws2.onerror = (error) => {
  console.error("Erro no WebSocket Usuário 2:", error)
}

// Fechamento da conexão websocket para o usuário 1
ws1.onclose = () => {
  console.log("Conexão WebSocket Usuário 1 fechada")
}

// Fechamento da conexão websocket para o usuário 2
ws2.onclose = () => {
  console.log("Conexão WebSocket Usuário 2 fechada")
}

// Envia uma mensagem pelo do websocket
function sendMessage(ws, inputId) {
  const input = document.getElementById(inputId)
  const message = input.value
  if (message) {
    ws.send(JSON.stringify({ content: message }))
    input.value = "" // Limpa o campo de entrada após o envio
  }
}

// Exibe uma mensagem recebida no chat
function displayMessage(messageData, chatId) {
  const chat = document.getElementById(chatId)
  const message = JSON.parse(messageData)

  const messageElement = document.createElement("div")
  messageElement.classList.add("message")

  const senderElement = document.createElement("strong")
  senderElement.textContent = message.sender_username + ": "
  messageElement.appendChild(senderElement)

  const contentElement = document.createElement("span")
  contentElement.textContent = message.content
  messageElement.appendChild(contentElement)

  const timeElement = document.createElement("div")
  timeElement.classList.add("message-time")
  const messageDate = new Date(message.created_at)
  const formattedDate = `${messageDate.getDate().toString().padStart(2, '0')}/${(messageDate.getMonth() + 1).toString().padStart(2, '0')} - ${messageDate.getHours().toString().padStart(2, '0')}:${messageDate.getMinutes().toString().padStart(2, '0')}`
  timeElement.textContent = formattedDate
  messageElement.appendChild(timeElement)

  chat.appendChild(messageElement)
  chat.scrollTop = chat.scrollHeight
}

// Busca o histórico de mensagens de uma sala de chat
async function fetchMessageHistory(chatId) {
  try {
    const response = await fetch(
      `http://localhost:8001/api/v1/chat/rooms/${roomId}/messages`,
      {
        headers: {
          Authorization: `Bearer ${token1}`, // Usa o token apropriado
        },
      }
    )
    const messages = await response.json()
    messages.forEach((message) => {
      displayMessage(JSON.stringify(message), chatId)
    })
  } catch (error) {
    console.error("Erro ao buscar histórico de mensagens:", error)
  }
}

// Realiza login e obtém o token JWT
async function login(usernameId, passwordId, tokenVar, user2Id) {
  const username = document.getElementById(usernameId).value
  const password = document.getElementById(passwordId).value

  try {
    const response = await fetch("http://localhost:8001/api/v1/users/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: username, password: password }),
    })

    if (response.ok) {
      const data = await response.json()
      window[tokenVar] = data.access_token
      setCookie(tokenVar, data.access_token, 7) // Armazena o token em um cookie
      console.log(`Token para ${username}: ${window[tokenVar]}`)

      const roomId = await createChatRoom(user2Id, tokenVar)
      connectWebSocket(roomId, tokenVar)
    } else {
      console.error("Erro ao fazer login:", response.statusText)
    }
  } catch (error) {
    console.error("Erro ao fazer login:", error)
  }
}

// Conecta ao WebSocket usando o jwt
function connectWebSocket(roomId, tokenVar) {
  const ws = new WebSocket(
    `ws://localhost:8001/api/v1/chat/ws/${roomId}?token=${window[tokenVar]}`
  )

  ws.onopen = () => {
    console.log(`Usuário conectado ao WebSocket com token ${tokenVar}`)
    fetchMessageHistory(`chat${tokenVar === "token1" ? 1 : 2}`)
  }

  ws.onmessage = (event) => {
    displayMessage(event.data, `chat${tokenVar === "token1" ? 1 : 2}`)
  }

  ws.onerror = (error) => {
    console.error(`Erro no WebSocket com token ${tokenVar}:`, error)
  }

  ws.onclose = () => {
    console.log(`Conexão WebSocket com token ${tokenVar} fechada`)
  }
}

// Cria uma nova sala de chat
async function createChatRoom(user2Id, tokenVar) {
  try {
    const response = await fetch("http://localhost:8001/api/v1/chat/rooms/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${window[tokenVar]}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user2_id: user2Id }),
    })

    if (response.ok) {
      const data = await response.json()
      console.log(`Sala de chat criada: ${data.id}`)
      return data.id
    } else {
      console.error("Erro ao criar sala de chat:", response.statusText)
    }
  } catch (error) {
    console.error("Erro ao criar sala de chat:", error)
  }
}

// Define um cookie
function setCookie(name, value, days) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString()
  document.cookie =
    name + "=" + encodeURIComponent(value) + "; expires=" + expires + "; path=/"
}

// Obtém um cookie
function getCookie(name) {
  return document.cookie.split("; ").reduce((r, v) => {
    const parts = v.split("=")
    return parts[0] === name ? decodeURIComponent(parts[1]) : r
  }, "")
}

// Executa ao carregar a página
window.onload = async () => {
  let roomId = getCookie("roomId")

  if (!roomId) {
    // Cria uma nova sala de chat se não existir
    const user1Id = 5 // ID do usuário 1 (deve existir no banco de dados)
    const user2Id = 6 // ID do usuário 2 (deve existir no banco de dados)

    roomId = await createChatRoom(user1Id, user2Id)
    if (roomId) {
      setCookie("roomId", roomId, 1) // Armazena o ID da sala em um cookie 
    }
  }

  if (roomId) {
    if (token1) {
      window.token1 = token1
      connectWebSocket(roomId, "token1")
    }

    if (token2) {
      window.token2 = token2
      connectWebSocket(roomId, "token2")
    }
  }
}

// Cria uma nova sala de chat
async function createChatRoom(user1Id, user2Id) {
  try {
    const response = await fetch("http://localhost:8001/api/v1/chat/rooms/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token1}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user1_id: user1Id, user2_id: user2Id }),
    })

    if (response.ok) {
      const data = await response.json()
      console.log(`Sala de chat criada: ${data.id}`)
      return data.id
    } else if (response.status === 400) {
      const data = await response.json()
      console.log(`Sala de chat já existe: ${data.id}`)
      return data.id
    } else {
      console.error("Erro ao criar sala de chat:", response.statusText)
    }
  } catch (error) {
    console.error("Erro ao criar sala de chat:", error)
  }
}
