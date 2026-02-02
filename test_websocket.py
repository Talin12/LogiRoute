import websocket
import json

def on_message(ws, message):
    print("Received:", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")

def on_open(ws):
    print("### Connected to WebSocket ###")
    # Request update
    ws.send(json.dumps({"type": "request_update"}))

# Connect to package tracking
ws = websocket.WebSocketApp(
    "ws://127.0.0.1:8000/ws/track/PKG-F44B72572275/",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

print("Attempting to connect to WebSocket...")
ws.run_forever()
