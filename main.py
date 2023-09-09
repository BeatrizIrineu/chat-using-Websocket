from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

connected_clients = set()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://192.168.0.8:8000/ws");
            
            //!!!!!!!!evento para lidar no lado do cliente com as mensagem enviadas ao servidor
            //!!!!!!!!aqui é criado elementos de lista <li> para cada mensagem e adiciona esses elementos à lista de mensagens na página HTML.

            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')

                var data = JSON.parse(event.data);
                console.log(data);
                if (data.type === "self") {
                    message.style.color = "blue";
                } else {
                    message.style.color = "green";
                }
                var content = document.createTextNode(data.message)
                
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")

                //!!!!!!!!função para lidar no lado do servidor com as mensagem enviadas pelo cliente

                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

#endpoint WebSocket, quando um cliente tenta estabelecer uma conexão WebSocket em "ws://192.168.0.8:8000/ws", a função websocket_endpoint será executada.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    #aceita a conexão WebSocket, permitindo que o cliente e o servidor estabeleçam uma conexão WebSocket bidirecional
    await websocket.accept()
    # Adiciona uma lista de cliente conectados 
    connected_clients.add(websocket)  
    try:
        #o servidor recebendo mensagens continuamente do cliente.
        while True:
            #aguarda a recepção de uma mensagem de texto do cliente através da conexão WebSocket e armazena essa mensagem na variável 
            data = await websocket.receive_text()

            # transmite a message para todos os clientes
            for client in connected_clients:
                #envia para o sender
                if client == websocket:
                    await client.send_text(json.dumps({"type": "self", "message": data}))
                #envia para os outros clientes 
                else:
                    await client.send_text(json.dumps({"type": "other", "message": data}))

    except:
        pass
    finally:
        # Remove o cliente quando desconectado
        connected_clients.remove(websocket)  

