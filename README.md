# 💬 Django Channels Chat App with JWT Auth, WebSockets, and REST API

This is a real-time chat application built using **Django**, **Django Channels**, **Redis**, **WebSockets**, and **JWT authentication**. It provides RESTful APIs for authentication and message history, along with WebSocket support for real-time messaging, typing indicators, and join/leave events.

## 🚀 Features

* 🔐 User registration, login, logout using JWT (SimpleJWT)
* 💬 Real-time private chat using WebSockets
* 🧠 Token validation inside WebSocket connection
* 📆 Message persistence in the database
* 📂 REST API for messages, users, and chat rooms
* 📡 Typing, join, and exit notifications over WebSockets

## ⚙️ Tech Stack

* **Django** – Core framework
* **Django Channels** – WebSocket support
* **Redis** – Channel layer (Pub/Sub backend)
* **SimpleJWT** – Token-based authentication
* **Uvicorn** – ASGI server for real-time support
* **SQLite/PostgreSQL** – Database

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/itx-zeeshan/django-chat-app.git
cd django-chat-app
```

### 2. Create Virtual Environment & Install Requirements

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Apply Migrations

```bash
python manage.py migrate
```

### 4. Run Redis Server (Required for Channels)

#### macOS

```bash
brew install redis
brew services start redis
```

#### Ubuntu/Linux

```bash
sudo apt update
sudo apt install redis
sudo systemctl enable redis
sudo systemctl start redis
```

#### Windows

Use Redis with Docker or install manually from [https://github.com/microsoftarchive/redis](https://github.com/microsoftarchive/redis)

### 5. Start the ASGI Server with Uvicorn

```bash
uvicorn chat_app.asgi:application --host 127.0.0.1 --port 8000 --reload
```

> ❗️ Do **not** use `python manage.py runserver` — it only supports WSGI, not ASGI.

## 🔑 API Endpoints (REST)

| Method   | Endpoint               | Description                   |
| -------- | ---------------------- | ----------------------------- |
| POST     | `/register/`           | Register a new user           |
| POST     | `/login/`              | Get access/refresh JWT tokens |
| POST     | `/logout/`             | Logout user                   |
| GET      | `/users/`              | List all users                |
| GET/POST | `/rooms/`              | List or create chat rooms     |
| GET      | `/my-rooms/`           | List rooms current user is in |
| GET/POST | `/messages/<room_id>/` | Send or list room messages    |

## 🌐 WebSocket Setup

### Endpoint

```
ws://127.0.0.1:8000/ws/chat/<room_name>/
```

> A valid JWT token must be sent with every message payload.

## 📤 WebSocket Payload Examples

### ✅ Send Message

```json
{
  "token": "<JWT_TOKEN>",
  "type": "message",
  "receiver": 2,
  "message": "Hey there!"
}
```

### 🟡 Typing Notification

```json
{
  "token": "<JWT_TOKEN>",
  "type": "typing"
}
```

### 🟢 Join Room

```json
{
  "token": "<JWT_TOKEN>",
  "type": "join"
}
```

### 🔴 Exit Room

```json
{
  "token": "<JWT_TOKEN>",
  "type": "exit"
}
```

## 📥 WebSocket Response Examples

### Message Sent

```json
{
  "type": "message",
  "sender": 1,
  "receiver": 2,
  "message": "Hey there!"
}
```

### Typing Indicator

```json
{
  "type": "typing",
  "sender": 1
}
```

### User Joined

```json
{
  "type": "join",
  "username": "john_doe"
}
```

### User Left

```json
{
  "type": "exit",
  "username": "john_doe"
}
```

## 🦖 Testing WebSockets

### Postman WebSocket

Use `ws://127.0.0.1:8000/ws/chat/testroom/` and send payloads like the examples above.

### JavaScript Console Test

```js
const socket = new WebSocket("ws://127.0.0.1:8000/ws/chat/testroom/");
socket.onmessage = (e) => console.log("Received:", e.data);
socket.onopen = () => socket.send(JSON.stringify({
  token: "<JWT_TOKEN>",
  type: "join"
}));
```

## 📁 Project Structure

```
chat_app/
├── chat/
│   ├── consumers.py          # WebSocket logic
│   ├── routing.py            # WebSocket URL patterns
│   ├── models.py             # ChatRoom, Message, User
│   ├── views.py              # REST API views
│   ├── serializers.py        # DRF serializers
│   └── urls.py               # REST routes
├── chat_app/
│   ├── asgi.py               # ASGI entrypoint
│   └── settings.py           # Django settings with Channels
├── requirements.txt
└── manage.py
```

## 🔹 Known Limitations

* Only supports 1-on-1 messaging
* No frontend included (but easily pluggable with React, Vue, Flutter, etc.)
* JWT token must be included in every WebSocket message

## 📊 Roadmap

* [ ] Group chat support
* [ ] Message seen/read indicators
* [ ] File & image upload support
* [ ] Push notifications

## 📄 License

MIT License — free to use, share, and modify.

## 👨‍💼 Author

**Zeeshan Habib**
Software Engineer
📧 [zesbox6@gmail.com](mailto:zesbox6@gmail.com)
🔗 [GitHub](https://github.com/itx-zeeshan) | [LinkedIn](https://www.linkedin.com/in/zeeshan-habib-dev/)

---

**P.S: Reach out for collaboration or freelance work!**
