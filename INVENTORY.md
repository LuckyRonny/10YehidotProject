# Project INVENTORY

## Project Overview

Shared virtual notebook: a multi-client client–server system that supports concurrent editing of a shared virtual notebook over an IP network. The server maintains notebooks and user data; clients create, edit, and share notebooks. Communication is encrypted and uses login/authentication. Notebooks support access control (view/edit/admin). Each notebook has multiple pages with text, drawings, marker strokes, colors, line widths, and page backgrounds (blank, ruled, grid). The server keeps notebook integrity and allows simultaneous editing; clients use a cached copy for responsiveness.

---

## Python Files

### Server (`src/srvr/`)

| File | Description |
|------|-------------|
| **server.py** | Main server entry: creates TCP sockets (main + updates port), accepts clients, performs key exchange per connection, and spawns threads to handle each client. Dispatches requests to `Methods` and sends responses; update connections only serve `CHECK_UPDATES`. |
| **user_manager.py** | User authentication and listing: `LOGIN` (validate username/password via SQLite, return id and display name or fail), `SIGNUP` (insert user, return id or fail on duplicate), `ALL_USERS` (list users with notebook permissions, excluding one user). Uses `NotebookDB.db` and SHA-256 hashed passwords. |
| **user_notebook_manager.py** | Links users to notebooks and permissions: `ADD_NOTEBOOK_TO_DB` (create notebook in DB and in NotebookManager), `CLIENTS_NOTEBOOKS` (list notebooks for a user with permissions), `CHANGE_ACCESS` (set/update permission for a user on a notebook). Uses SQLite and delegates content to NotebookManager. |
| **notebook_manager.py** | Notebook content and updates: loads/saves notebooks and updates as JSON under `server_data/`. Handles `GET_NOTEBOOK`, `ADD_NOTEBOOK`, `ADD_STROKE`, `DELETE_STROKE`, `ADD_PAGE`, `CLEAR`, `CHANGE_BACKGROUND`, `CHECK_UPDATES`. Uses a lock for concurrency; appends updates and trims list when too long. |
| **protocol.py** | Length-prefixed, optionally encrypted messaging: `send`/`recv` for strings and `send_bin`/`recv_bin` for bytes. Encrypts/decrypts with AES when connection has a key. |
| **aes_cipher.py** | AES CBC encryption/decryption for the secure channel: pad/unpad (PKCS7-style), encrypt (IV + ciphertext, base64), decrypt, and `generate_key` (random bytes hashed with SHA-256). Uses PyCryptodome. |
| **constants.py** | Server constants: port, IP, message length, protocol/request indices, DB column indices, and names for notebooks, users, and requests. |
| **diffie_hellman.py** | ECDH key agreement on SECP384R1: generates key pair, serializes/deserializes public key (PEM), derives shared secret with HKDF-SHA256 to a 32-byte key. |
| **key_exchange.py** | Key exchange over the protocol: `send_recv_key` (send local DH public key, receive peer, derive key); `recv_send_key` (receive then send, used by server). Uses unencrypted binary send/recv for the handshake. |
| **methods.py** | Request routing: dispatches by domain to `UserManager` (USERS), `NotebookManager` (NOTEBOOKS), and `UserNotebookManager` (USERS_NOTEBOOKS) based on the request type in params. |
| **my_sha256.py** | SHA-256 helpers: `get_hash` (raw digest) and `get_hash_hex` (hex string) for password hashing and other digests. |

---

### Client (`src/clnt/`)

| File | Description |
|------|-------------|
| **client.py** | Client connection and requests: reads IP/port from Windows registry, opens main and updates sockets, performs key exchange for both. Validates request format and parameter count; `send_command` routes `check_updates` to the updates socket and all other requests to the main socket. |
| **log_in.py** | Login window (PyQt6): username/password fields, Login and Sign up buttons, error label. On success sends login request, opens MainWindow with client and user id/name, hides login. |
| **sign_up.py** | Sign-up window: username, name, password, Sign up button. Sends signup request; on success opens MainWindow and closes; on failure shows error. |
| **main_window.py** | Main app window after login: toolbar (user name, log out, refresh, add notebook), flow layout of notebook buttons, floating “add notebook” box. Loads user notebooks via `clients_notebooks`, opens NotebookArea on notebook click. |
| **notebook_area.py** | Single-notebook view: toolbars (page/pen/marker/eraser/select), scroll area with notebook widget, prev/next/add page, clear, save, back, Access (if admin). Starts a background thread that polls `check_updates` and emits updates to refresh the notebook; applies server updates (ADD_STROKE, DELETE_STROKE, etc.) and manages access dialog. |
| **notebook.py** | Notebook widget: stacked pages (DrawingCanvas), zoom in/out, add/prev/next page. Serializes to dict (pages + last_change). Applies server-driven updates (ADD_PAGE, ADD_STROKE, DELETE_STROKE, etc.) and keeps `last_change` in sync. |
| **canvas.py** | Drawing canvas: pen, marker, eraser, select tools; stroke input (points + times), straight-line detection, zoom (scale factor and pinch). Backgrounds: blank, lines, grid. Paints strokes, handles select/move and eraser; notifies notebook_area for add_stroke, delete_stroke, clear_page, change_background. Implements ADD_STROKE/DELETE_STROKE/CLEAR/CHANGE_BACKGROUND for server updates. |
| **canvas_container.py** | Simple container widget that centers a child and paints a light blue background; used to wrap the canvas in the UI. |
| **scroll_area.py** | Centered scroll area for the notebook: Ctrl+wheel zooms in/out by calling the notebook’s zoom methods; otherwise delegates to default wheel behavior. |
| **stroke.py** | Stroke model: list of points (QPoint or (x,y)), times, pen color/size, id. `contains_point` for hit-testing with tolerance; `__dict__` for serialization (points, times, pen_color hex, pen_size, id). |
| **access.py** | Access management dialog: one row per user with a combo (Admin/Edit/View/No Access). Save applies choices; `get_access_data` returns a dict username → access string for the parent to send `change_access` commands. |
| **flow_layout.py** | Flow layout (QLayout): places widgets left-to-right and wraps to next line; used for the notebook buttons on the main window. Supports clear and optional widget deletion. |
| **protocol.py** | Same as server protocol: length-prefixed send/recv for strings and binary, with optional AES encryption when connection has a key. |
| **key_exchange.py** | Client-side key exchange: `send_recv_key` sends client DH public key, receives server key, derives shared key (mirror of server’s `recv_send_key`). |
| **aes_cipher.py** | Same as server: AES CBC encrypt/decrypt and key generation for the secure channel. |
| **diffie_hellman.py** | Same as server: ECDH on SECP384R1 and HKDF for shared key derivation. |
| **my_sha256.py** | Same as server: SHA-256 digest and hex helpers (client may use for local checks; main use is server-side passwords). |
| **constants.py** | Client constants: default IP, port, message length, request/parameter indices, and parameter counts for login, signup, get_notebook, add_notebook, clients_notebooks, add_stroke, delete_stroke, etc. |
| **style.py** | UI constants and styles: window size, margins, canvas/background sizes, pen/marker/eraser ranges, colors, Qt stylesheets for main window, toolbars, buttons, login, combo, scroll bar, dialogs. Defines `ToolbarsEnum` for toolbar indices. |
| **winreg_file.py** | Reads server IP and port from Windows registry (`HKEY_LOCAL_MACHINE\SOFTWARE\Technition Server`); used by client at startup. |
| **pep8_tester.py** | Utility script to run PEP8 style checks on Python files in the current directory (uses the `pep8` package). |

---

## Summary

- **Server:** 11 files (server, user/notebook/user-notebook managers, protocol, crypto, key exchange, methods, constants, SHA-256).
- **Client:** 21 files (client, login/signup/main/notebook-area UI, notebook and canvas, stroke, access dialog, flow layout, scroll area, protocol, crypto, key exchange, constants, style, registry, PEP8 tester).

Total: **32** Python files.
