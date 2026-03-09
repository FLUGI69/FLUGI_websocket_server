<div align="center">

# FLUGI WebSocket Server

Real-time WebSocket server enabling communication between distributed desktop application clients.

</div>

<div align="center">
	<h3>Reference Portfolio Project</h3>
	<p>
		WebSocket synchronization server built with <b>Python + Socket.IO</b>,
		designed as the real-time communication backbone for the
		<a href="https://github.com/FLUGI69/FLUGI_desktop_app"><b>FLUGI Desktop App</b></a>. When the desktop GUI application
		runs on multiple machines simultaneously, this server enables all connected
		clients to communicate and stay synchronized in real time.
	</p>
</div>

<hr>

## Project Overview

FLUGI WebSocket Server is a lightweight, namespace-based Socket.IO server that acts as the central hub for real-time client-to-client communication across a distributed desktop application environment.

**Core purpose:** When the companion PyQt6 desktop application is deployed across multiple workstations, each instance connects to this WebSocket server. The server then relays events — such as Redis cache refresh signals, data updates, and automated messages — between all authenticated clients, ensuring every user sees consistent, up-to-date information without manual polling.

Key capabilities:

- **Multi-client real-time sync** — broadcasts events to all authenticated clients across namespaces
- **Token-based authentication** — validates clients on connection using an auth token handshake
- **Namespace isolation** — organizes communication channels via Socket.IO namespaces (e.g., `/Example`)
- **Pydantic data models** — strongly typed request/response payloads with automatic model discovery and validation
- **Structured logging** — color-coded console output and rotating file logs with per-session log files
- **ASGI architecture** — runs on Uvicorn for high-performance async I/O
- **Abstract namespace pattern** — easily extensible with new namespace handlers by subclassing `AbstractNamespace`
- **Environment capture** — records client IP, headers, query parameters, and connection metadata per session

This repository is a **reference portfolio project** and serves as the server-side counterpart to the [FLUGI Desktop App](https://github.com/FLUGI69/FLUGI_desktop_app).

## Tech Stack

<table>
	<tr><th>Area</th><th>Technology</th></tr>
	<tr><td>Language</td><td>Python 3.14.3</td></tr>
	<tr><td>WebSocket / Real-time</td><td>python-socketio, python-engineio</td></tr>
	<tr><td>ASGI Server</td><td>Uvicorn</td></tr>
	<tr><td>Data Validation</td><td>Pydantic</td></tr>
	<tr><td>Logging</td><td>colorlog, logging (stdlib)</td></tr>
	<tr><td>HTTP</td><td>Requests, Starlette</td></tr>
</table>

## Complete Technology Stack & Libraries

### WebSocket & Real-time Communication
- **python-socketio** (5.13.0) — Socket.IO server implementation
- **python-engineio** (4.12.2) — Engine.IO protocol layer
- **simple-websocket** (1.1.0) — WebSocket transport
- **websockets** (15.0.1) — async WebSocket implementation
- **wsproto** (1.2.0) — WebSocket protocol library

### ASGI Server & Web Framework
- **uvicorn** (0.35.0) — lightning-fast ASGI server
- **starlette** (0.47.3) — lightweight ASGI framework
- **httptools** (0.7.1) — fast HTTP parsing
- **watchfiles** (1.1.1) — file change detection for auto-reload

### Data Validation & Serialization
- **pydantic** (2.12.5) — data validation using Python type hints
- **pydantic_core** (2.41.5) — core validation logic for Pydantic
- **annotated-types** (0.7.0) — type annotation utilities
- **typing-inspection** (>=0.4.2) — type inspection utilities
- **typing_extensions** (4.15.0) — backported typing features

### HTTP & Network
- **requests** (2.32.5) — HTTP client library
- **urllib3** (2.5.0) — HTTP client with connection pooling
- **certifi** (2025.8.3) — Mozilla CA certificate bundle
- **charset-normalizer** (3.4.3) — character encoding detection
- **idna** (3.10) — internationalized domain names
- **anyio** (4.10.0) — async networking and concurrency
- **sniffio** (1.3.1) — async library detection
- **h11** (0.16.0) — HTTP/1.1 protocol library

### Logging & Terminal
- **colorlog** (6.9.0) — colored terminal logging
- **colorama** (0.4.6) — cross-platform colored terminal output

### Configuration
- **PyYAML** (6.0.3) — YAML parser
- **python-dotenv** (1.1.1) — environment variable management
- **click** (8.2.1) — command-line interface utilities

### Async & Concurrency
- **bidict** (0.23.1) — bidirectional dictionary (used by Socket.IO internals)

## Architecture

```
websocket/
├── __main__.py                        # Entry point — creates server and registers namespaces
├── config/
│   ├── config.py                      # Application configuration (host, port, auth, DB, Redis, logging)
│   └── config_example.py             # Template config with placeholder values
├── dataclass/
│   └── base.py                        # DataclassBaseModel — Pydantic base with model discovery,
│                                      #   recursive serialization, and dynamic model selection
├── namespaces/
│   ├── abstract_namespace.py          # AbstractNamespace — base class for all namespace handlers;
│   │                                  #   manages client sessions, auth, environ capture, broadcasting
│   └── example_gui/
│       └── example_gui.py             # ExampleGuiNamespace — concrete handler for the desktop GUI;
│                                      #   handles connect/disconnect and redis_refresh broadcasting
├── socketio_server/
│   └── socketio_server.py             # SocketIOServer — wraps Socket.IO + Uvicorn ASGI app
└── utils/
    ├── logger.py                      # LoggerMixin — structured logging with file + console handlers,
    │                                  #   custom PRINT level, global print/excepthook override
    └── dc/websocket/
        ├── auto_message.py            # AutoMessage model — server-generated notification messages
        ├── client.py                  # WebsocketClient model — client identity and auth state
        ├── environ.py                 # Environ model — captured connection environment metadata
        ├── redis_event.py             # RedisEvent model — Redis cache invalidation event payload
        ├── websocket_request.py       # WebsocketRequest model — incoming client request envelope
        ├── websocket_request_response.py  # WebsocketRequestResponse — acknowledgement payload
        └── websocket_response.py      # WebsocketResponse model — outgoing server response envelope
```

## How It Works

### Connection Flow

1. A desktop GUI client connects to a namespace (e.g., `/Example`) with an auth payload containing a `WebsocketClient` object (name + auth token).
2. The server validates the auth token against the configured secret.
3. On success, the client is marked as `authenticated` and receives a `websocket_response` confirmation.
4. Connection environment (IP, headers, query params) is captured and stored per session.

### Event Broadcasting

1. An authenticated client emits an event (e.g., `redis_refresh`) with a `WebsocketRequest` payload.
2. The server's namespace handler receives the event and calls `broadcast_event`.
3. All other authenticated clients in that namespace receive the event data as a `WebsocketResponse`.
4. The original sender receives a `websocket_response_ack` acknowledgement.

### Data Model Discovery

The `DataclassBaseModel.select_model()` method dynamically discovers all model classes in the `utils/dc/websocket/` directory. When a dict payload arrives with a `__class__` key, the server automatically instantiates the correct Pydantic model — enabling type-safe, extensible message schemas without manual registration.

## Python 3.14.3 Setup

This project should be run with **Python 3.14.3**.

### 1. Verify Python 3.14.3

Windows (PowerShell):

```powershell
py -3.14 --version
```

Expected output should include `Python 3.14.3`.

If you have multiple Python versions, always force 3.14 when creating the virtual environment.

### 2. Create Virtual Environment

From repository root:

```powershell
py -3.14 -m venv .venv
```

### 3. Activate Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If execution policy blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Command Prompt (`cmd`):

```bat
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 4. Upgrade Packaging Tools

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### 5. Install Dependencies

All dependencies are listed in `requirements.txt`.

```powershell
pip install -r requirements.txt
```

### 6. Confirm Environment

```powershell
python --version
pip --version
```

`python --version` should show `3.14.3` while the venv is active.

## Configuration

The application expects `websocket/config/config.py` to exist and contain valid runtime values.

1. Use `websocket/config/config_example.py` as your reference.
2. Copy and fill in your values:

```powershell
cp websocket/config/config_example.py websocket/config/config.py
```

3. Provide values for:
	 - `websocket.host` / `websocket.port` — server bind address
	 - `websocket.auth_token` — shared secret for client authentication
	 - `log.level` — logging verbosity (`DEBUG`, `INFO`, `WARNING`, etc.)
	 - Database and Redis credentials (if applicable)

Important:

- Do not commit real secrets/tokens to public repositories.
- Keep private keys and credentials outside versioned source whenever possible.

## Run the Server

From repository root with active venv:

```powershell
python websocket
```

The server will start on the configured host and port, ready to accept Socket.IO connections.

## Adding a New Namespace

1. Create a new class extending `AbstractNamespace`:

```python
from namespaces.abstract_namespace import AbstractNamespace
from utils.dc.websocket.websocket_response import WebsocketResponse

class MyNamespace(AbstractNamespace):

    async def connected(self, sid: str) -> WebsocketResponse:
        # Handle client connection
        ...

    async def disconnected(self, sid: str, reason: str) -> WebsocketResponse:
        # Handle client disconnection
        ...
```

2. Register it in `__main__.py`:

```python
server = SocketIOServer(
    host=Config.websocket.host,
    port=Config.websocket.port,
    namespaces=[
        ExampleGuiNamespace("/Example"),
        MyNamespace("/MyNamespace"),
    ]
)
```

## Adding a New Data Model

Create a new file in `websocket/utils/dc/websocket/`:

```python
from dataclass import DataclassBaseModel

class MyEvent(DataclassBaseModel):
    field_one: str
    field_two: int
```

The model is automatically discovered and available for deserialization — no manual registration needed.

> **Important:** The data models defined in `websocket/utils/dc/websocket/` must be identical across the server and **all connected clients** — whether they are desktop GUI apps, web applications, or any other service. When Client 1 (e.g., a GUI instance) emits an event, the server deserializes it using its local model, then broadcasts it to Client 2 (another GUI instance) and Client 3 (e.g., a web app) — each of which deserializes the payload using the same model on their side. If the models are out of sync (e.g., a field is missing or renamed on one side), deserialization will fail and the event will be lost. Always keep the model definitions synchronized between this server and every client that connects to it.

## Author

**Flugi**

## License

This project is a reference portfolio project and is not licensed for production use.
