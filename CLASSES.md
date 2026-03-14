## Server Classes

### Class name: `Server` (`src/srvr/server.py`)
**Description**: Manages the TCP server lifecycle for both the main command channel and a separate updates channel. It accepts incoming client connections, performs a Diffie–Hellman–based key exchange for each connection, and spawns threads that handle regular and update requests using the shared protocol and methods dispatch layer.
**Variables**:
- **Instance**: `server_socket` (main listening socket), `update_socket` (updates listening socket).
**Methods**:
- **`__init__(ip, port)` → `None`**: Creates and binds the main and updates sockets on the given IP/port pair and starts listening; exits the process on failures.
- **`handle_clients()` → `None`**: Main accept loop for regular clients; for each new connection performs key exchange, wraps the socket as a connection tuple, and starts a thread for `handle_single_client`, as well as a background thread for `accept_updates`.
- **`accept_updates()` → `None`**: Accept loop for the updates socket; for each new connection performs key exchange, wraps it as a connection tuple, and spawns a thread running `handle_update_client`.
- **`handle_single_client(conn, address)` → `bool`**: Static loop per client that receives a request, dispatches it through `Methods`, sends the response, and stops on errors; returns `False` when terminating.
- **`handle_update_client(conn_updates, address)` → `None`**: Static loop per updates client; only serves `CHECK_UPDATES` requests and replies `"NO"` to any other request type, terminating on errors.
- **`receive_client_request(conn)` → `tuple[str | None, list[str] | None]`**: Static helper that receives one protocol message, splits it into request name and parameter list, and uppercases the request; returns `(None, None)` on empty input.
- **`handle_client_request(request, params)` → `str`**: Static dispatcher that resolves the appropriate handler method on `Methods` based on `params[REQUEST_TYPE]` and returns its string response.
- **`send_response_to_client(response, conn)` → `None`**: Static helper that sends a string response to the client using the shared protocol.

### Class name: `UserManager` (`src/srvr/user_manager.py`)
**Description**: Encapsulates all user-related operations backed by the SQLite database `NotebookDB.db`. It handles logging in users, signing them up, and retrieving the list of users with their permissions for a specific notebook.
**Variables**:
- **Class**: `NAME_OF_USER` (index of display name in user row), `LOGIN_FAIL_RESPONSE` (failure marker), `DEFAULT_PERMISSION` (fallback permission for notebooks), `ALL_USERS_PARAMS_NOTEBOOK_INDEX`, `PERMISSION`, `ID`.
**Methods**:
- **`LOGIN(params)` → `str`**: Validates a username/password pair by querying the `Users` table with a SHA-256–hashed password; returns `"id!name"` if a match exists, otherwise `"False"`.
- **`SIGNUP(params)` → `str`**: Attempts to create a new user row with the given username, password, and name; returns the new user id as string on success, or `"False"` on duplicate username or DB integrity error.
- **`ALL_USERS(params)` → `str`**: Given an excluded user id and a notebook identifier, returns a `!`-separated string of `"username,permission"` entries for all other users, using notebook permissions when defined and a default otherwise.
- **`get_id_permission(excluded_user, notebook)` → `tuple[list[tuple], list[tuple]]`**: Queries the database to fetch `(user_name, id)` rows for all users except one and `(user, permission)` entries for a resolved notebook; returns both result sets.

### Class name: `UserNotebookManager` (`src/srvr/user_notebook_manager.py`)
**Description**: Connects users with notebooks and their permissions using the `Notebooks` and `UsersNotebooks` tables. It creates notebook records, returns notebooks for a user, resolves ids from names, and manages access changes for sharing.
**Variables**:
- **Class**: `PERMISSION`, `CHANGE_ACCESS_PARAMS_ACCESS_INDEX`, `CHANGE_ACCESS_PARAMS_NOTEBOOK_NAME_INDEX`, `NOTEBOOK_ID_ROW_INDEX`, `USER_ID_ROW_INDEX`, `PERMISSION_ROW_INDEX`, `EXIST`, `FIRST`, `PERMISSIONS_ROW`.
**Methods**:
- **`ADD_NOTEBOOK_TO_DB(params)` → `str`**: Inserts a notebook row and a `UsersNotebooks` mapping with a given permission, then delegates to `NotebookManager.ADD_NOTEBOOK`; returns `"ok"` or a DB integrity error string.
- **`add_to_db(notebook_name, user_id, per)` → `None`**: Inserts into `Notebooks` and `UsersNotebooks` within a transaction, raising an exception on duplicates.
- **`CLIENTS_NOTEBOOKS(params)` → `str`**: For a given user id, collects all notebooks with non–“no access” permission and returns a `!`-separated list of `"name,permission"` pairs.
- **`get_all_notebooks(id, cursor, notebooks_names)` → `str`**: Helper that resolves a notebook id to its name using the `Notebooks` table, returning the name.
- **`_resolve_user_id(cursor, user_name)` → `int | None`**: Resolves a username to its numeric id from the `Users` table, or `None` if not found.
- **`_resolve_notebook_id(cursor, notebook_name)` → `int | None`**: Resolves a notebook name to its numeric id from the `Notebooks` table, or `None` if not found.
- **`_user_notebook_exists(cursor, user_id, notebook_id)` → `bool`**: Checks if a `UsersNotebooks` row already exists for a given user–notebook pair.
- **`CHANGE_ACCESS(params)` → `str`**: Creates or updates a `UsersNotebooks` row for a given username, access level, and notebook; returns `"ok"` (even when user or notebook cannot be resolved).

### Class name: `NotebookManager` (`src/srvr/notebook_manager.py`)
**Description**: Server-side notebook storage manager that persists notebook contents and incremental updates as JSON files. It coordinates page and stroke operations with concurrency control and generates per-notebook update streams for clients to poll.
**Variables**:
- **Class**: `lock` (threading lock shared across notebook operations).
**Methods**:
- **`_notebook_path(name)` → `str`**: Static helper that returns the filesystem path for the notebook JSON file for the given name.
- **`_updates_path(name)` → `str`**: Static helper that returns the filesystem path for the JSON update log for the given notebook.
- **`_atomic_write(path, data)` → `None`**: Writes JSON to a temporary file and atomically replaces the target file to prevent corruption.
- **`_load(path, default=None)` → `dict | list | Any`**: Loads JSON from disk if present, else returns the provided default (or `{}`) value.
- **`_parse_param(param)` → `dict | Any`**: Interprets a notebook-related parameter as a dict, attempting `ast.literal_eval` if it is a string.
- **`GET_NOTEBOOK(params)` → `str`**: Loads a notebook structure for the given name and returns its `repr` string.
- **`ADD_NOTEBOOK(params)` → `str`**: Writes a complete notebook dict for the given name and ensures an update file exists; returns `"ok"`.
- **`ADD_STROKE(params)` → `str`**: Adds or creates a stroke record for a page, generating a new stroke id when needed, updating `last_change`, persisting the notebook, and appending an `"ADD_STROKE"` update; returns the stroke id as string.
- **`DELETE_STROKE(params)` → `str`**: Removes a stroke from a given page, updating `last_change`, persisting the notebook, and adding a `"DELETE_STROKE"` update; returns `"ok"` or `"page_not_found"`/`"stroke_not_found"`.
- **`ADD_PAGE(params)` → `str`**: Inserts or replaces a page entry under a notebook (ensuring default `stroke_id` and `strokes` fields), updates `last_change`, and adds an `"ADD_PAGE"` update; returns `"ok"`.
- **`CLEAR(params)` → `str`**: Clears all strokes from a page, updates `last_change`, persists the notebook, emits a `"CLEAR"` update, and returns `"ok"` or `"page_not_found"`.
- **`CHANGE_BACKGROUND(params)` → `str`**: Changes the `page_type` field of a page, updates `last_change`, persists the notebook, and appends a `"CHANGE_BACKGROUND"` update; returns `"ok"` or `"page_not_found"`.
- **`CHECK_UPDATES(params)` → `str`**: Filters the update log for a given notebook name to entries newer than the provided timestamp and returns their `repr` list.
- **`create_update(notebook_name, ts, type, id_page, data)` → `None`**: Appends a typed update record to the notebook’s update list, trimming it to a configured maximum length, and writes it atomically.

### Class name: `Protocol` (`src/srvr/protocol.py`)
**Description**: Implements the server-side wire protocol for sending and receiving messages over a socket with a fixed-length header. It supports both text and binary payloads, and optionally AES-encrypts content depending on the presence of a shared key in the connection tuple.
**Variables**:
- **Class**: `STOP_RECV` (loop sentinel value), `KEY` (index of key in connection tuple), `SOCK` (index of socket in connection tuple).
**Methods**:
- **`send(conn, data)` → `None`**: Encodes a string payload, encrypts it when a key is set, prefixes it with a zero-padded length header, and sends the combined bytes.
- **`send_bin(conn, data_bit)` → `None`**: Sends raw bytes in the same length-prefixed and optionally encrypted format as `send`.
- **`recv(conn)` → `str`**: Receives the fixed-length header, then reads the expected payload size, decrypts if necessary, and returns the decoded string.
- **`recv_bin(conn)` → `bytes`**: Same as `recv` but returns raw decrypted bytes instead of decoding to text.

### Class name: `AESCipher` (`src/srvr/aes_cipher.py`)
**Description**: Provides AES-CBC encryption and decryption for the secure channel, handling low-level padding, IV generation, and base64 encoding of the ciphertext. It also includes a helper for generating random 256-bit keys.
**Variables**:
- **Class**: `KEY_RANDOM_BYTES` (length of random seed for key derivation), `NO_OVER` (padding helper constant).
**Methods**:
- **`encrypt(key, raw)` → `bytes`**: Pads raw bytes to the AES block size, encrypts with a random IV and the provided key, and returns a base64-encoded concatenation of IV and ciphertext.
- **`decrypt(key, enc)` → `bytes`**: Base64-decodes the input, separates the IV, decrypts the ciphertext, and returns the unpadded cleartext bytes.
- **`_pad(s)` → `bytes`**: Applies PKCS7-style padding to input bytes to align with the AES block size.
- **`_unpad(s)` → `bytes`**: Removes PKCS7-style padding from decrypted bytes using the last padding byte as length.
- **`generate_key()` → `bytes`**: Creates random bytes of length `KEY_RANDOM_BYTES`, hashes them with SHA-256, and returns the resulting 32-byte key.

### Class name: `DiffieHellman` (`src/srvr/diffie_hellman.py`)
**Description**: Wraps Elliptic Curve Diffie–Hellman (ECDH) key exchange on the SECP384R1 curve, exposing convenience methods for serializing keys and deriving a shared secret via HKDF-SHA256. Used by both client and server to establish symmetric keys.
**Variables**:
- **Instance**: `diffieHellman` (private EC key), `public_key` (corresponding EC public key).
**Methods**:
- **`__init__()` → `None`**: Generates a new EC private key and assigns its public key field.
- **`serialize_public_key()` → `bytes`**: Returns the public key encoded as PEM bytes using the SubjectPublicKeyInfo format.
- **`deserialize_public_key(data)` → public key object**: Parses PEM bytes to reconstruct an EC public key instance.
- **`get_key(public_key)` → `bytes`**: Executes ECDH with the peer public key, then uses HKDF-SHA256 to derive a fixed-length shared key.

### Class name: `KeyExchange` (`src/srvr/key_exchange.py`)
**Description**: Implements the higher-level protocol for exchanging ECDH public keys between two peers over the project’s `Protocol` abstraction. It encapsulates the common pattern of sending/receiving and then deriving a shared symmetric key.
**Variables**:
- **None (all stateless static methods).**
**Methods**:
- **`send_recv_key(conn)` → `bytes`**: Creates a `DiffieHellman` instance, sends its public key to the peer, receives the peer’s public key, and returns the derived shared key.
- **`recv_send_key(conn)` → `bytes`**: Receives the peer’s public key first, then sends the local public key, and returns the derived shared key.

### Class name: `Methods` (`src/srvr/methods.py`)
**Description**: Serves as a routing layer between high-level request groups (`USERS`, `NOTEBOOKS`, `USERS_NOTEBOOKS`) and their respective manager classes. It decouples the server loop from specific user, notebook, and sharing operations.
**Variables**:
- **Class**: `USER_MANAGER_CLASS_NAME`, `NOTEBOOK_MANAGER_CLASS_NAME`, `USER_NOTEBOOK_MANAGER_CLASS_NAME` (string names used with `getattr`).
**Methods**:
- **`USERS(request, params)` → `str`**: Dispatches a user-related request to the corresponding static method on `UserManager` and returns its response.
- **`NOTEBOOKS(request, params)` → `str`**: Dispatches a notebook content operation to the appropriate static method of `NotebookManager`.
- **`USERS_NOTEBOOKS(request, params)` → `str`**: Forwards sharing and permission requests to the matching method on `UserNotebookManager`.

### Class name: `Hasha256` (`src/srvr/my_sha256.py`)
**Description**: Small utility class that exposes static helpers for computing SHA-256 hashes and their hex representations. Primarily used for hashing user passwords.
**Variables**:
- **None (pure static methods).**
**Methods**:
- **`get_hash(st)` → `bytes`**: Encodes the given string as UTF-8 and returns the raw SHA-256 digest.
- **`get_hash_hex(st)` → `str`**: Encodes the given string as UTF-8 and returns the hexadecimal SHA-256 digest string.

---

## Client Classes

### Class name: `Client` (`src/clnt/client.py`)
**Description**: Manages the client-side TCP connections to the server, including both the main command socket and a separate updates socket. It performs key exchange for each connection and provides convenience methods to validate and send protocol-formatted requests, including a special path for `check_updates`.

**Variables**:
- **`my_socket`** (Instance): Main TCP socket for the command channel. Type: `socket.socket`.
- **`connection`** (Instance): Main connection tuple `(socket, key)` used for sending and receiving command requests. Type: `tuple`.
- **`check_socket`** (Instance): TCP socket for the updates channel. Type: `socket.socket`.
- **`connection_check`** (Instance): Updates connection tuple `(socket, key)` used for `check_updates` requests. Type: `tuple`.

**Methods**:
- **`__init__()` → `None`**
  - **Description**: Reads IP and port from the Windows registry, opens and connects two sockets (main and updates), performs key exchange on each, and constructs the connection tuples; exits the process on connection failure.
  - **Inputs**: None.
  - **Outputs**: None.
- **`handle_user_input()` → `None`**
  - **Description**: Implements an interactive CLI loop for manual testing that reads user-entered requests, validates them, and sends and receives responses until the user enters `"EXIT"` or `"QUIT"`.
  - **Inputs**: None.
  - **Outputs**: None.
- **`valid_request(req_and_prms)` → `bool`**
  - **Description**: Static validator that checks whether a parsed request/parameter list conforms to expected operation names and parameter counts (login, signup, notebook ops, etc.).
  - **Inputs**: `req_and_prms`: list of strings (request name and parameters, typically from splitting on `$`).
  - **Outputs**: `True` if the request is valid, `False` otherwise.
- **`login_check(req_and_prms)` → `bool`**
  - **Description**: Static helper that validates login requests and guards against simple SQL injection patterns in username and password (e.g. no `--` or `;`).
  - **Inputs**: `req_and_prms`: list containing request type and parameters including username and password.
  - **Outputs**: `True` if the request is a valid login with allowed characters, `False` otherwise.
- **`signup_check(req_and_prms)` → `bool`**
  - **Description**: Static helper that validates signup requests, checking for illegal characters in username and password.
  - **Inputs**: `req_and_prms`: list containing request type and parameters including username and password.
  - **Outputs**: `True` if the request is a valid signup with allowed characters, `False` otherwise.
- **`funcs_check(req_and_prms)` → `bool`**
  - **Description**: Static helper that validates notebook-related requests such as `add_stroke`, `delete_stroke`, `change_background`, `clear`, `add_page`, and `check_updates` (parameter counts).
  - **Inputs**: `req_and_prms`: list of request name and parameters.
  - **Outputs**: `True` if the request matches one of the known notebook ops with correct parameter count, `False` otherwise.
- **`send_request_to_server(con, request)` → `None`**
  - **Description**: Sends a string request over the given connection tuple using the client `Protocol.send`.
  - **Inputs**: `con`: connection tuple `(socket, key)`; `request`: full request string to send.
  - **Outputs**: None.
- **`handle_server_response(con)` → `str`**
  - **Description**: Receives a full response string from the given connection tuple via the protocol and returns it.
  - **Inputs**: `con`: connection tuple `(socket, key)` to receive from.
  - **Outputs**: The decoded response string from the server.
- **`send_command(request)` → `str`**
  - **Description**: High-level API for other client components; splits and validates the request string, routes `check_updates` over the update connection and all other requests over the main connection, and returns the server response or `"ILLEGAL REQUEST"`.
  - **Inputs**: `request`: full request string (e.g. `"login$user$pass$USERS"`).
  - **Outputs**: Server response string, or `"ILLEGAL REQUEST"` if validation fails.

### Class name: `LoginWindow` (`src/clnt/log_in.py`)
**Description**: The initial PyQt6 window that presents username and password fields to the user. It owns a `Client` instance, triggers login attempts, displays errors, and opens the main window on successful authentication.

**Variables**:
- **`client`** (Instance): Shared `Client` instance used for login and communication. Type: `Client`.
- **`username_line_edit`** (Instance): Line edit widget for the username. Type: `QtWidgets.QLineEdit`.
- **`password_line_edit`** (Instance): Line edit widget for the password (echo mode password). Type: `QtWidgets.QLineEdit`.
- **`error_label`** (Instance): Label used to display login/error messages. Type: `QLabel`.

**Methods**:
- **`__init__()` → `None`**
  - **Description**: Sets window title, styling, minimum size, builds the central UI via `create_central_widget`, and constructs the `Client`.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_central_widget()` → `None`**
  - **Description**: Assembles the central widget containing username and password line edits, error label, and login/signup buttons, and sets it as the main window’s central widget.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_central_layout(central_layout, username_layout, password_layout, button_layout, error_layout)` → `None`**
  - **Description**: Lays out the login form by adding the provided layouts to the central layout with margins and vertical spacing.
  - **Inputs**: `central_layout`: main vertical layout; `username_layout`, `password_layout`, `button_layout`, `error_layout`: horizontal layouts to add in order.
  - **Outputs**: None.
- **`create_layout(layout, name)` → `QtWidgets.QLineEdit`**
  - **Description**: Adds a label and a line edit to the given horizontal layout and returns the created line edit.
  - **Inputs**: `layout`: horizontal layout to add to; `name`: label text (e.g. `"Username: "`).
  - **Outputs**: The created `QLineEdit` instance.
- **`create_error_layout(layout)` → `QLabel`**
  - **Description**: Creates an error label centered in the given layout row (with stretches) and returns it.
  - **Inputs**: `layout`: horizontal layout to add the label to.
  - **Outputs**: The created `QLabel` instance for error text.
- **`create_button_layout(button_layout)` → `None`**
  - **Description**: Places the Login and Sign up buttons into the provided layout with stretches.
  - **Inputs**: `button_layout`: horizontal layout to add buttons to.
  - **Outputs**: None.
- **`create_button(name, func)` → `QPushButton`**
  - **Description**: Builds a styled push button with the given text, wires its clicked signal to `func`, and returns it.
  - **Inputs**: `name`: button label; `func`: callable (e.g. slot) for the clicked signal.
  - **Outputs**: The created `QPushButton`.
- **`login_button_clicked()` → `None`**
  - **Description**: Collects username and password from the line edits, sends a login request via `Client.send_command`, and on success opens the `MainWindow` and hides the login window; on failure sets the error label text.
  - **Inputs**: None.
  - **Outputs**: None.
- **`signin_button_clicked()` → `None`**
  - **Description**: Opens the `SignupWindow` (passing `self` as parent), shows it, and hides the login window to transition to the registration flow.
  - **Inputs**: None.
  - **Outputs**: None.

### Class name: `SignupWindow` (`src/clnt/sign_up.py`)
**Description**: A PyQt6 window for registering new users. It presents username, display name, and password fields, and on success opens the main window while linking back to the login window that spawned it.
**Variables**:
- **`username_line_edit`** (Instance): Line edit for the username. Type: `QtWidgets.QLineEdit`.
- **`name_line_edit`** (Instance): Line edit for the display name. Type: `QtWidgets.QLineEdit`.
- **`password_line_edit`** (Instance): Line edit for the password. Type: `QtWidgets.QLineEdit`.
- **`error_label`** (Instance): Label for signup error messages. Type: `QLabel`.
- **`client`** (Instance): Own `Client` instance used for signup request. Type: `Client`.
- **`login`** (Instance): Reference to the parent `LoginWindow` that opened this dialog. Type: `LoginWindow`.

**Methods**:
- **`__init__(login)` → `None`**
  - **Description**: Builds the central layout with username, name, and password input fields and error area, initializes a `Client`, and stores the reference to the originating login window.
  - **Inputs**: `login`: the `LoginWindow` instance that opened this signup window.
  - **Outputs**: None.
- **`create_central_layout(central_layout, username_layout, name_layout, password_layout, button_layout, error_layout)` → `None`**
  - **Description**: Applies margins and stacking for the signup form by adding the provided layouts to the central layout in order.
  - **Inputs**: `central_layout`: main vertical layout; `username_layout`, `name_layout`, `password_layout`, `button_layout`, `error_layout`: layouts to add.
  - **Outputs**: None.
- **`create_layout(layout, name)` → `QtWidgets.QLineEdit`**
  - **Description**: Creates a label and line-edit pair for one input line, adds them to the given layout, and returns the line-edit.
  - **Inputs**: `layout`: horizontal layout; `name`: label text.
  - **Outputs**: The created `QLineEdit`.
- **`create_error_layout(layout)` → `QLabel`**
  - **Description**: Creates an error label with stretches and adds it to the layout; returns the label for later error text.
  - **Inputs**: `layout`: horizontal layout to add the label to.
  - **Outputs**: The created `QLabel`.
- **`create_button_layout(button_layout)` → `None`**
  - **Description**: Adds the Sign up button to the layout and wires its clicked signal to `signup_button_clicked`.
  - **Inputs**: `button_layout`: horizontal layout to add the button to.
  - **Outputs**: None.
- **`signup_button_clicked()` → `None`**
  - **Description**: Sends a signup request via `Client.send_command`; on invalid/illegal parameters sets error to a generic message, on duplicate username sets a specific message, and on success opens the `MainWindow` and closes this window.
  - **Inputs**: None.
  - **Outputs**: None.

### Class name: `MainWindow` (`src/clnt/main_window.py`)
**Description**: The primary application dashboard shown after login. It displays a toolbar with user identity, log-out and refresh actions, and an add-notebook control, plus a flow layout of notebook tiles for quick access, and a floating frame for creating new notebooks.

**Variables**:
- **`login_window`** (Instance): Back-reference to the login window, used for log out and clearing fields. Type: `LoginWindow`.
- **`central_widget`** (Instance): Main widget set as the window's central widget. Type: `QWidget`.
- **`layout`** (Instance): Main vertical layout attached to the central widget. Type: `QVBoxLayout`.
- **`main_toolbar`** (Instance): Top toolbar with user name, log out, refresh, and add-notebook button. Type: `QToolBar`.
- **`box`** (Instance): Floating `QFrame` containing the add-notebook form (label, line-edit, create button). Type: `QFrame`.
- **`box_margin_right`** (Instance): Right margin in pixels for positioning the floating box. Type: `int`.
- **`box_margin_top`** (Instance): Top margin in pixels for positioning the floating box. Type: `int`.
- **`client`** (Instance): Shared `Client` used for server commands. Type: `Client`.
- **`notebooks_layout`** (Instance): Flow layout holding notebook tile buttons. Type: `FlowLayout`.
- **`id`** (Instance): Current user id string. Type: `str`.
- **`notebooks_dict`** (Instance): Mapping from full notebook name to its push button. Type: `dict`.
- **`names_perms`** (Instance): Mapping from notebook name to permission integer. Type: `dict`.

**Methods**:
- **`__init__(client, id, login_window, name)` \u2192 `None`**
  - **Description**: Initializes window styling and minimum size, sets central widget and main layout, builds the toolbar and floating add frame, creates the flow layout container, stores the user id and login window reference, and loads notebooks for the user.
  - **Inputs**: `client`: shared `Client`; `id`: user id string; `login_window`: login window reference; `name`: user display name for toolbar.
  - **Outputs**: None.
- **`create_flow_layout()` → `None`**
  - **Description**: Constructs a `FlowLayout`, wraps it in a `QWidget`, and adds that widget to the main layout.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_toolbar(name)` → `None`**
  - **Description**: Builds the main toolbar with the user's name label, log out and refresh buttons, a spacer, and the add-notebook button.
  - **Inputs**: `name`: user display name for the label.
  - **Outputs**: None.
- **`create_add_button()` → `QPushButton`**
  - **Description**: Creates the plus-icon button used to toggle the floating add-notebook frame; connects clicked to `create_new_notebook_frame`.
  - **Inputs**: None.
  - **Outputs**: The created `QPushButton`.
- **`create_log_out_button()` → `None`**
  - **Description**: Adds a styled log out button to the toolbar and wires its clicked signal to `log_out`.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_refresh_button()` → `None`**
  - **Description**: Adds a refresh button with icon to the toolbar and wires its clicked signal to `refresh`.
  - **Inputs**: None.
  - **Outputs**: None.
- **`refresh()` → `None`**
  - **Description**: Clears the notebook tile layout and reloads notebooks for the current user id via `load_notebooks_for_user`.
  - **Inputs**: None.
  - **Outputs**: None.
- **`log_out()` → `None`**
  - **Description**: Clears the login window's username and password line edits, shows the login window, and closes this main window.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_add_frame()` → `None`**
  - **Description**: Creates the floating frame (via `create_box`), adds label, line-edit, and create button to it, sets margins, and initially hides the box.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_box()` → `None`**
  - **Description**: Instantiates and styles the `QFrame` that acts as the floating add-notebook box (size, frame shape, stylesheet).
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_button(line_edit)` → `QPushButton`**
  - **Description**: Creates the create button and connects it so that on click it calls `create_new_notebook(self.id, line_edit.text())`.
  - **Inputs**: `line_edit`: the line edit whose text is used as the notebook name.
  - **Outputs**: The created `QPushButton`.
- **`create_new_notebook_frame()` → `None`**
  - **Description**: Toggles the visibility of the floating add frame; when shown, raises it and repositions it.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_new_notebook(id, notebook_name)` → `None`**
  - **Description**: Builds a new empty `Notebook`, serializes it, sends `add_notebook_to_db` via the client; on success creates a new notebook button tile, adds it to the flow layout, and wires it to `open_notebook`.
  - **Inputs**: `id`: user id; `notebook_name`: name entered by user (will be suffixed with `_id` for full name).
  - **Outputs**: None.
- **`resizeEvent(event)` → `None`**
  - **Description**: Override that repositions the floating add frame whenever the window is resized.
  - **Inputs**: `event`: resize event.
  - **Outputs**: None.
- **`reposition_box()` → `None`**
  - **Description**: Computes the top-right position for the floating box relative to the central widget and moves and raises the box.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_notebook_button(name)` → `QPushButton`**
  - **Description**: Creates a fixed-size push button with the given name (display name for the tile).
  - **Inputs**: `name`: button label (e.g. notebook display name).
  - **Outputs**: The created `QPushButton`.
- **`load_notebooks_for_user(user_id)` → `None`**
  - **Description**: Sends `clients_notebooks` request, parses the response, populates `names_perms` and the flow layout with a button per notebook, each wired to `open_notebook` with the full notebook name.
  - **Inputs**: `user_id`: user id string.
  - **Outputs**: None.
- **`open_notebook(name)` → `None`**
  - **Description**: Fetches notebook content with `get_notebook`, constructs a `NotebookArea` with the data and permission, shows it, and hides the main window.
  - **Inputs**: `name`: full notebook name (e.g. `displayname_id`).
  - **Outputs**: None.

### Class name: `NotebookArea` (`src/clnt/notebook_area.py`)
**Description**: Hosts the interactive view of a single notebook, including drawing tools, page navigation controls, and background selection. It also runs a background thread that polls the server for updates and applies them live across pages.
**Variables**:
- **`notebook_update_signal`** (Class): Qt signal carrying a list of updates and a page index. Type: `pyqtSignal(list, int)`.
- **`name`** (Instance): Notebook identifier (full name). Type: `str`.
- **`notebook_widget`** (Instance): The `Notebook` instance showing pages. Type: `Notebook`.
- **`current_page`** (Instance): Current page index in the stacked widget. Type: `int`.
- **`id`** (Instance): User id string. Type: `str`.
- **`client`** (Instance): Shared `Client` for server requests. Type: `Client`.
- **`main_window`** (Instance): Parent `MainWindow` reference. Type: `MainWindow`.
- **`running`** (Instance): Whether the background update loop should keep running. Type: `bool`.
- **`main_toolbar`** (Instance): Main toolbar widget. Type: `QToolBar`.
- **`sub_toolbars`** (Instance): List of sub-toolbars (page, pen, marker, eraser, select). Type: `list`.
- **`perm`** (Instance): Permission code for this notebook (e.g. view-only, edit, admin). Type: `int`.
- **`button_layout`** (Instance): Layout for bottom navigation buttons (prev, next, add page). Type: `QHBoxLayout`.
- **`scroll_area`** (Instance): Centered scroll area hosting the notebook widget. Type: `CenteredScrollArea`.
- **`page_toolbar`** (Instance): Sub-toolbar for page background selection. Type: `QToolBar`.
- **`pen_toolbar`** (Instance): Sub-toolbar for pen tool and size/color. Type: `QToolBar`.
- **`marker_toolbar`** (Instance): Sub-toolbar for marker tool. Type: `QToolBar`.
- **`eraser_toolbar`** (Instance): Sub-toolbar for eraser tool. Type: `QToolBar`.
- **`select_toolbar`** (Instance): Sub-toolbar for select tool. Type: `QToolBar`.
- **`page_button`** (Instance): Toolbar button that toggles page sub-toolbar. Type: `QPushButton`.
- **`pen_button`** (Instance): Toolbar button that toggles pen sub-toolbar. Type: `QPushButton`.
- **`marker_button`** (Instance): Toolbar button that toggles marker sub-toolbar. Type: `QPushButton`.
- **`eraser_button`** (Instance): Toolbar button that toggles eraser sub-toolbar. Type: `QPushButton`.
- **`select_button`** (Instance): Toolbar button that toggles select sub-toolbar. Type: `QPushButton`.
- **`btn_prev`** (Instance): Previous page button. Type: `QPushButton`.
- **`btn_next`** (Instance): Next page button. Type: `QPushButton`.
- **`btn_add`** (Instance): Add page button (optional, for non-view-only). Type: `QPushButton` or None.
- **`pen_size_button`** (Instance): Spin box for pen size. Type: `QSpinBox`.
- **`pen_color_button`** (Instance): Combo box for pen color. Type: `QComboBox`.
- **`marker_size_button`** (Instance): Spin box for marker size. Type: `QSpinBox`.
- **`marker_color_button`** (Instance): Combo box for marker color. Type: `QComboBox`.
- **`eraser_size_button`** (Instance): Spin box for eraser size. Type: `QSpinBox`.

**Methods**:
- **`__init__(mainwindow, id, client, notebook, name, perm)` → `None`**
  - **Description**: Initializes the window, builds the central layout and toolbars, constructs or creates a `Notebook`, sets permission behavior, starts the background polling thread, and connects the update signal.
  - **Inputs**: `mainwindow`: parent `MainWindow`; `id`: user id; `client`: shared `Client`; `notebook`: notebook dict or None; `name`: notebook name; `perm`: permission code.
  - **Outputs**: None.
- **`loop()` → `None`**
  - **Description**: Runs in a thread, repeatedly sending `check_updates` with the notebook name and last change time; on receiving non-empty updates, parses them and emits `notebook_update_signal`.
  - **Inputs**: None.
  - **Outputs**: None.
- **`create_toolbars(central_layout, perm)` → `None`**
  - **Description**: Creates the main toolbar and sub-toolbars for page, pen, marker, eraser, and select tools, then lays out page navigation controls and content.
  - **Inputs**: `central_layout`: central layout to add to; `perm`: permission code.
  - **Outputs**: None.
- **`save_notebook()` → `None`**
  - **Description**: Sends an `add_notebook` request to persist the current notebook state on the server.
  - **Inputs**: None.
  - **Outputs**: None.
- **`clear_page(page_id)` → `None`**
  - **Description**: Sends a `clear` command for the specified page to the server.
  - **Inputs**: `page_id`: id of the page to clear.
  - **Outputs**: None.
- **`change_background(type, page_id)` → `None`**
  - **Description**: Sends a `change_background` command to set the background type for a page on the server.
  - **Inputs**: `type`: background type (e.g. blank, lines, grid); `page_id`: page id.
  - **Outputs**: None.
- **`add_stroke(stroke, id_page, id)` → `str`**
  - **Description**: Serializes a `Stroke` object and sends an `add_stroke` command; returns the stroke id allocated by the server.
  - **Inputs**: `stroke`: `Stroke` to add; `id_page`: page id; `id`: optional stroke id.
  - **Outputs**: The stroke id string returned by the server.
- **`add_page(id_page, page)` → `None`**
  - **Description**: Sends an `add_page` command with the serialized `DrawingCanvas` state to create a new page.
  - **Inputs**: `id_page`: page id; `page`: `DrawingCanvas` or serialized page state.
  - **Outputs**: None.
- **`delete_stroke(id_page, id)` → `None`**
  - **Description**: Sends a `delete_stroke` command for the given page and stroke id.
  - **Inputs**: `id_page`: page id; `id`: stroke id to delete.
  - **Outputs**: None.
- **`add_to_central_layout(central_layout, perm)` → `None`**
  - **Description**: Configures and inserts the scroll area and bottom buttons into the central layout.
  - **Inputs**: `central_layout`; `perm`
  - **Outputs**: None
- **`create_central_layout()` → `tuple[QVBoxLayout, QWidget]`**
  - **Description**: Creates and returns the central layout and associated widget.
  - **Inputs**: None
  - **Outputs**: See return type: tuple[QVBoxLayout, QWidget]
- **`show_sub_toolbar(index)` → `None`**
  - **Description**: Toggles visibility for sub-toolbars based on which tool button is pressed and sets the current drawing tool accordingly.
  - **Inputs**: `index`
  - **Outputs**: None
- **`set_tool_and_size_and_color(i, toolbar)` → `None`**
  - **Description**: Sets the active tool, brush size, and color according to the selected toolbar type.
  - **Inputs**: `i`; `toolbar`
  - **Outputs**: None
- **`tool_size_and_color(tool, size, color)` → `None`**
  - **Description**: Helper that sets the tool, then size and color for the current canvas.
  - **Inputs**: `tool`; `size`; `color`
  - **Outputs**: None
- **`create_buttons(perm)` → `None`**
  - **Description**: Adds toolbar buttons such as clear, back, and (for admins) access management.
  - **Inputs**: `perm`
  - **Outputs**: None
- **`create_buttons_layout(perm)` → `None`**
  - **Description**: Creates the bottom navigation layout with previous, next, and optionally add-page buttons.
  - **Inputs**: `perm`
  - **Outputs**: None
- **`create_sub_toolbars(central_layout)` → `None`**
  - **Description**: Initializes all sub-toolbars and corresponding toggle buttons.
  - **Inputs**: `central_layout`
  - **Outputs**: None
- **`create_sub_toolbar_page(central_layout)` → `None`**
  - **Description**: Builds the page background selection sub-toolbar, adds its controls, and wires it to the main toolbar.
  - **Inputs**: `central_layout`
  - **Outputs**: None
- **`create_sub_toolbar_pen(central_layout)` → `None`**
  - **Description**: Builds the pen tool sub-toolbar with size and color controls and wires it to the main toolbar.
  - **Inputs**: `central_layout`
  - **Outputs**: None
- **`create_sub_toolbar_marker(central_layout)` → `None`**
  - **Description**: Builds the marker tool sub-toolbar with size and color controls and wires it to the main toolbar.
  - **Inputs**: `central_layout`
  - **Outputs**: None
- **`create_sub_toolbar_eraser(central_layout)` → `None`**
  - **Description**: Builds the eraser tool sub-toolbar with size control and wires it to the main toolbar.
  - **Inputs**: `central_layout`
  - **Outputs**: None
- **`create_sub_toolbar_select(central_layout)` → `None`**
  - **Description**: Builds the select tool sub-toolbar and wires it to the main toolbar.
  - **Inputs**: `central_layout`
  - **Outputs**: None
- **`set_checked(i, toolbar, is_visible)` → `None`**
  - **Description**: Manages the checked state and visibility of toolbar buttons when switching tools.
  - **Inputs**: `i`; `toolbar`; `is_visible`
  - **Outputs**: None
- **`toolbar_button(button, index)` → `None`**
  - **Description**: Wires a toolbar button to show the appropriate sub-toolbar.
  - **Inputs**: `button`; `index`
  - **Outputs**: None
- **`clear_current_page()` → `None`**
  - **Description**: Clears the current page’s strokes via the active `DrawingCanvas`.
  - **Inputs**: None
  - **Outputs**: None
- **`back_current_page()` → `None`**
  - **Description**: Undoes the last stroke on the current page.
  - **Inputs**: None
  - **Outputs**: None
- **`set_tool_for_current(tool_name)` → `None`**
  - **Description**: Applies a tool name (pen, marker, eraser, select, page) to the current canvas.
  - **Inputs**: `tool_name`
  - **Outputs**: None
- **`no_tool_for_all()` → `None`**
  - **Description**: Disables tools on all pages (used for view-only permissions).
  - **Inputs**: None
  - **Outputs**: None
- **`set_size_for_current(size)` → `None`**
  - **Description**: Adjusts pen size on the current canvas.
  - **Inputs**: `size`
  - **Outputs**: None
- **`set_color_for_current(color)` → `None`**
  - **Description**: Adjusts pen/marker color on the current canvas.
  - **Inputs**: `color`
  - **Outputs**: None
- **`set_background_for_current(background)` → `None`**
  - **Description**: Changes the background type of the current page and persists it.
  - **Inputs**: `background`
  - **Outputs**: None
- **`toolbar_features(toolbar)` → `None`**
  - **Description**: Applies shared style and behavior to a sub-toolbar and tracks it.
  - **Inputs**: `toolbar`
  - **Outputs**: None
- **`main_toolbar_button(button, func)` → `None`**
  - **Description**: Styles a main toolbar button and connects it to its handler.
  - **Inputs**: `button`; `func`
  - **Outputs**: None
- **`create_page_buttons()` → `tuple[QPushButton, QPushButton, QPushButton]`**
  - **Description**: Builds the blank, lines, and grid background selection buttons.
  - **Inputs**: None
  - **Outputs**: See return type: tuple[QPushButton, QPushButton, QPushButton]
- **`create_page_toolbar()` → `QToolBar`**
  - **Description**: Creates the page background selection toolbar.
  - **Inputs**: None
  - **Outputs**: See return type: QToolBar
- **`create_select_toolbar()` → `QToolBar`**
  - **Description**: Creates the (currently empty) selection toolbar.
  - **Inputs**: None
  - **Outputs**: See return type: QToolBar
- **`create_pen_toolbar_and_size_and_color()` → `tuple[QToolBar, QSpinBox, QComboBox]`**
  - **Description**: Constructs the pen toolbar with size and color controls.
  - **Inputs**: None
  - **Outputs**: See return type: tuple[QToolBar, QSpinBox, QComboBox]
- **`create_marker_toolbar_and_size_and_color()` → `tuple[QToolBar, QSpinBox, QComboBox]`**
  - **Description**: Constructs the marker toolbar with width and color selectors.
  - **Inputs**: None
  - **Outputs**: See return type: tuple[QToolBar, QSpinBox, QComboBox]
- **`create_eraser_toolbar_and_size()` → `tuple[QToolBar, QSpinBox]`**
  - **Description**: Builds the eraser toolbar with size selection.
  - **Inputs**: None
  - **Outputs**: See return type: tuple[QToolBar, QSpinBox]
- **`create_size_button(size_range, start_value, size_step)` → `QSpinBox`**
  - **Description**: Creates a spin box configured for choosing pen/marker/eraser size.
  - **Inputs**: `size_range`; `start_value`; `size_step`
  - **Outputs**: See return type: QSpinBox
- **`create_color_button(colors)` → `QComboBox`**
  - **Description**: Creates a drop-down with the provided color names and wires it to color changes.
  - **Inputs**: `colors`
  - **Outputs**: See return type: QComboBox
- **`closeEvent(event)` → `None`**
  - **Description**: Restores the parent main window, stops the update loop, and accepts the close event.
  - **Inputs**: `event`
  - **Outputs**: None
- **`parse_users_access_response(resp)` → `list[tuple[str, int]]`**
  - **Description**: Parses the server’s `all_users` response into a list of `(username, permission_int)`.
  - **Inputs**: `resp`
  - **Outputs**: See return type: list[tuple[str, int]]
- **`apply_access_changes(access_data)` → `None`**
  - **Description**: Sends `change_access` requests for each user in the access data mapping.
  - **Inputs**: `access_data`
  - **Outputs**: None
- **`open_access_dialog()` → `None`**
  - **Description**: Fetches current access levels, opens the `AccessDialog`, and applies user changes on acceptance.
  - **Inputs**: None
  - **Outputs**: None
- **`reload_notebook(data, current_page)` → `None`**
  - **Description**: Applies a list of server updates to the notebook widget, repaints pages, restores the current page, and re-applies view-only restrictions if needed.
  - **Inputs**: `data`; `current_page`
  - **Outputs**: None

### Class name: `Notebook` (`src/clnt/notebook.py`)
**Description**: Client-side container for a notebook’s set of drawing pages, implemented as a stacked widget. It manages page creation, navigation, zooming, and applying server-side update events to the individual canvases.
**Variables**:
- **`notebook_area`** (Instance): Parent `NotebookArea` reference. Type: `NotebookArea`.
- **`pages`** (Instance): Stacked widget holding page canvases. Type: `QStackedWidget`.
- **`pages_list`** (Instance): List of `DrawingCanvas` instances in order. Type: `list`.
- **`global_scale_factor`** (Instance): Current zoom factor applied to all pages. Type: `float`.
- **`main_layout`** (Instance): Main vertical layout. Type: `QVBoxLayout`.
- **`last_change`** (Instance): Timestamp of last change (for sync). Type: `float`.

**Methods**:
- **`__init__(pages, last_change, notebook_area)` → `None`**
  - **Description**: Initializes a notebook with existing page data or creates the first blank page, sets up the stacked widget layout, and links back to the owning `NotebookArea`.
  - **Inputs**: `pages`; `last_change`; `notebook_area`
  - **Outputs**: None
- **`__dict__()` → `dict`**
  - **Description**: Serializes the notebook into a dict with `pages` and `last_change`, with each page serialized via its canvas `__dict__`.
  - **Inputs**: None
  - **Outputs**: See return type: dict
- **`current_canvas()` → `DrawingCanvas | None`**
  - **Description**: Returns the currently visible `DrawingCanvas` page.
  - **Inputs**: None
  - **Outputs**: See return type: DrawingCanvas | None
- **`add_page(page, notify_server=True)` → `None`**
  - **Description**: Adds an existing or new page canvas to the stacked widget, optionally informs the server of the new page, and updates the current page index.
  - **Inputs**: `page`; `notify_server`
  - **Outputs**: None
- **`prev_page()` → `None`**
  - **Description**: Navigates to the previous page if possible and updates the `NotebookArea`’s current page index.
  - **Inputs**: None
  - **Outputs**: None
- **`next_page()` → `None`**
  - **Description**: Navigates to the next page if not already at the last, updating the current page index accordingly.
  - **Inputs**: None
  - **Outputs**: None
- **`zoom_in()` → `None`**
  - **Description**: Increases the global zoom factor within min/max bounds and applies it to all pages.
  - **Inputs**: None
  - **Outputs**: None
- **`zoom_out()` → `None`**
  - **Description**: Decreases the global zoom factor within bounds and applies it to all pages.
  - **Inputs**: None
  - **Outputs**: None
- **`apply_zoom_to_all()` → `None`**
  - **Description**: Resizes and repaints every page canvas according to the current global zoom.
  - **Inputs**: None
  - **Outputs**: None
- **`update_notebook(ts, type, page, data)` → `None`**
  - **Description**: Applies a server update by either adding a new page (`ADD_PAGE`) or forwarding commands (e.g., `ADD_STROKE`, `DELETE_STROKE`, `CLEAR`, `CHANGE_BACKGROUND`) to the correct page; updates `last_change`.
  - **Inputs**: `ts`; `type`; `page`; `data`
  - **Outputs**: None
- **`delete_old_data()` → `None`**
  - **Description**: Clears all page widgets and resets the stack, used when reloading notebook data from scratch.
  - **Inputs**: None
  - **Outputs**: None

### Class name: `DrawingCanvas` (`src/clnt/canvas.py`)
**Description**: A custom drawing widget that allows pen and marker strokes, erasing, selecting and moving strokes, and zooming via pinch and scroll gestures. It maintains a rendered background (blank, lined, or grid) and communicates stroke changes back to the server through its owning `NotebookArea`.

**Variables**:
- **`background_layer`** (Instance): Pixmap for the page background. Type: `QPixmap`.
- **`strokes`** (Instance): List of `Stroke` objects. Type: `list`.
- **`current_stroke_points`** (Instance): Points collected for the stroke being drawn. Type: `list`.
- **`current_stroke_times`** (Instance): Timestamps for the current stroke points. Type: `list`.
- **`selected_stroke`** (Instance): Currently selected stroke (for move). Type: `Stroke` or None.
- **`drawing`** (Instance): Whether a stroke is currently being drawn. Type: `bool`.
- **`history`** (Instance): List of previous strokes (for undo). Type: `list`.
- **`last_point`** (Instance): Last point (for move/distance). Type: `QPoint`.
- **`first_point`** (Instance): First point of current stroke. Type: `QPoint`.
- **`pen_color`** (Instance): Current pen/marker color. Type: `QColor`.
- **`pen_size`** (Instance): Current pen/marker/eraser size. Type: numeric.
- **`tool`** (Instance): Current tool name (pen, marker, eraser, select, page, no). Type: `str`.
- **`page_type`** (Instance): Background type (blank, lines, grid). Type: `str`.
- **`is_gesturing`** (Instance): Whether a pinch gesture is in progress. Type: `bool`.
- **`scale_factor`** (Instance): Current zoom scale. Type: `float`.
- **`base_width`** (Instance): Base width before zoom. Type: numeric.
- **`base_height`** (Instance): Base height before zoom. Type: numeric.
- **`notebook_area`** (Instance): Parent `NotebookArea` reference. Type: `NotebookArea`.
- **`id`** (Instance): Page id. Type: `int`.
- **`stroke_id`** (Instance): Next local stroke id. Type: `int`.

**Methods**:
- **`__init__(width, height, strokes, page_type, notebook_area, stroke_id, id)` → `None`**
  - **Description**: Initializes background, restoring strokes (if any), history and pen state, zoom parameters, parent reference, and stroke id counters.
  - **Inputs**: `width`; `height`; `strokes`; `page_type`; `notebook_area`; `stroke_id`; `id`
  - **Outputs**: None
- **`_handle_eraser_click(pos)` → `None`**
  - **Description**: Removes the first stroke that intersects the hit point with eraser tolerance and notifies the `NotebookArea` to delete the stroke on the server.
  - **Inputs**: `pos`
  - **Outputs**: None
- **`__dict__()` → `dict`**
  - **Description**: Serializes the canvas state including dimensions, serialized strokes, page type, current stroke id, and page id.
  - **Inputs**: None
  - **Outputs**: See return type: dict
- **`create_background_layer(width, height)` → `None`**
  - **Description**: Sets a fixed size and creates the initial white background pixmap.
  - **Inputs**: `width`; `height`
  - **Outputs**: None
- **`create_strokes_params(strokes)` → `None`**
  - **Description**: Initializes the strokes list from serialized data and sets up transient stroke-drawing state.
  - **Inputs**: `strokes`
  - **Outputs**: None
- **`create_history_params()` → `None`**
  - **Description**: Initializes undo/history-related attributes and last/first point placeholders.
  - **Inputs**: None
  - **Outputs**: None
- **`create_pen_params(page_type)` → `None`**
  - **Description**: Sets the default pen color, size, tool type, and applies the initial page background style.
  - **Inputs**: `page_type`
  - **Outputs**: None
- **`create_zoom_in_params(width, height)` → `None`**
  - **Description**: Enables pinch gestures and records base width/height and scale factor.
  - **Inputs**: `width`; `height`
  - **Outputs**: None
- **`paintEvent(event)` → `None`**
  - **Description**: Renders the background, all existing strokes, and the currently drawn stroke with proper scaling and anti-aliasing.
  - **Inputs**: `event`
  - **Outputs**: None
- **`draw_strokes(painter)` → `None`**
  - **Description**: Iterates through all stored strokes, drawing them and highlighting selected ones.
  - **Inputs**: `painter`
  - **Outputs**: None
- **`draw_background(painter)` → `None`**
  - **Description**: Fills the widget with the surrounding color and draws the scaled background pixmap.
  - **Inputs**: `painter`
  - **Outputs**: None
- **`draw_current_stroke(painter)` → `None`**
  - **Description**: Draws the in-progress stroke using the current pen parameters.
  - **Inputs**: `painter`
  - **Outputs**: None
- **`draw_stroke(stroke, painter)` → `None`**
  - **Description**: Renders a single stroke as a polyline.
  - **Inputs**: `stroke`; `painter`
  - **Outputs**: None
- **`mousePressEvent(event)` → `None`**
  - **Description**: Handles left-button presses to start drawing (pen/marker), select strokes, or erase strokes depending on the active tool.
  - **Inputs**: `event`
  - **Outputs**: None
- **`check_which_selected(pos)` → `None`**
  - **Description**: Walks strokes from last to first, marking as selected the first stroke that contains the click point.
  - **Inputs**: `pos`
  - **Outputs**: None
- **`create_pen(pen_size, pen_color)` → `QtGui.QPen`**
  - **Description**: Creates and returns a configured pen for drawing.
  - **Inputs**: `pen_size`; `pen_color`
  - **Outputs**: See return type: QtGui.QPen
- **`mouseMoveEvent(event)` → `None`**
  - **Description**: While dragging, either moves the selected stroke or adds points to the current drawing stroke.
  - **Inputs**: `event`
  - **Outputs**: None
- **`move_selected_stroke(e, pos)` → `bool`**
  - **Description**: Shifts the selected stroke by the pointer delta and returns `True` if a move was performed.
  - **Inputs**: `e`; `pos`
  - **Outputs**: See return type: bool
- **`distance(point1, point2)` → `float`**
  - **Description**: Static helper computing Euclidean distance between two points.
  - **Inputs**: `point1`; `point2`
  - **Outputs**: See return type: float
- **`_are_last_points_close(point_list, time_list, close_points_distance, close_points_time)` → `bool`**
  - **Description**: Determines whether a drawn stroke should be treated as a straight line based on spatial and temporal thresholds.
  - **Inputs**: `point_list`; `time_list`; `close_points_distance`; `close_points_time`
  - **Outputs**: See return type: bool
- **`mouseReleaseEvent(event)` → `None`**
  - **Description**: Finalizes a stroke or a selection move; may send new or updated strokes to the server via `NotebookArea`.
  - **Inputs**: `event`
  - **Outputs**: None
- **`add_new_stroke()` → `Stroke | None`**
  - **Description**: Creates either a straight-line stroke or a freehand stroke from accumulated points, increments the stroke id, and returns the new stroke.
  - **Inputs**: None
  - **Outputs**: See return type: Stroke | None
- **`create_straight_line()` → `Stroke`**
  - **Description**: Builds and appends a new `Stroke` using only the first and last points, clearing the in-progress state.
  - **Inputs**: None
  - **Outputs**: See return type: Stroke
- **`end_stroke()` → `Stroke`**
  - **Description**: Converts the current stroke point list into a `Stroke`, appends it, clears the buffers, and returns it.
  - **Inputs**: None
  - **Outputs**: See return type: Stroke
- **`clear_canvas()` → `None`**
  - **Description**: Clears all strokes and notifies the `NotebookArea` to clear the corresponding page on the server.
  - **Inputs**: None
  - **Outputs**: None
- **`draw_all_canvas()` → `QtGui.QPixmap`**
  - **Description**: Renders the entire canvas (background and strokes) to an off-screen pixmap and returns it.
  - **Inputs**: None
  - **Outputs**: See return type: QtGui.QPixmap
- **`set_tool(tool_type)` → `None`**
  - **Description**: Sets the current drawing tool (pen, marker, eraser, select, page, no).
  - **Inputs**: `tool_type`
  - **Outputs**: None
- **`change_pen_size(size)` → `None`**
  - **Description**: Adjusts the pen or eraser size based on the active tool.
  - **Inputs**: `size`
  - **Outputs**: None
- **`change_pen_color(i)` → `None`**
  - **Description**: Sets pen or marker color using palette indices and appropriate alpha levels.
  - **Inputs**: `i`
  - **Outputs**: None
- **`back()` → `None`**
  - **Description**: Removes the most recently drawn stroke, and if a `NotebookArea` is present, instructs the server to delete it.
  - **Inputs**: None
  - **Outputs**: None
- **`zoom_in()` → `None`**
  - **Description**: Increases the scale factor within bounds and updates the widget size.
  - **Inputs**: None
  - **Outputs**: None
- **`zoom_out()` → `None`**
  - **Description**: Decreases the scale factor within bounds and updates the widget size.
  - **Inputs**: None
  - **Outputs**: None
- **`_update_size()` → `None`**
  - **Description**: Recomputes fixed size from base dimensions and scale factor, then repaints.
  - **Inputs**: None
  - **Outputs**: None
- **`event(event)` → `bool`**
  - **Description**: Intercepts gesture events and delegates pinch gestures to `gesture_event`.
  - **Inputs**: `event`
  - **Outputs**: See return type: bool
- **`gesture_event(event)` → `bool`**
  - **Description**: Handles pinch gestures by toggling `is_gesturing` and relaying to `handle_pinch`.
  - **Inputs**: `event`
  - **Outputs**: See return type: bool
- **`handle_pinch(pinch)` → `None`**
  - **Description**: Updates the scale factor based on pinch scaling and resizes/redraws accordingly.
  - **Inputs**: `pinch`
  - **Outputs**: None
- **`blank()` → `None`**
  - **Description**: Sets a blank white background for the page.
  - **Inputs**: None
  - **Outputs**: None
- **`lines()` → `None`**
  - **Description**: Draws ruled lines and margins on the background pixmap.
  - **Inputs**: None
  - **Outputs**: None
- **`_draw_grid_background()` → `None`**
  - **Description**: Draws a grid pattern on the background pixmap.
  - **Inputs**: None
  - **Outputs**: None
- **`grid()` → `None`**
  - **Description**: Sets the page type to grid and applies the grid background.
  - **Inputs**: None
  - **Outputs**: None
- **`ADD_STROKE(data)` → `None`**
  - **Description**: Applies a stroke insertion update from the server, replacing any stroke with the same id.
  - **Inputs**: `data`
  - **Outputs**: None
- **`DELETE_STROKE(id)` → `None`**
  - **Description**: Processes a server-side delete stroke update by removing the stroke with the matching id.
  - **Inputs**: `id`
  - **Outputs**: None
- **`CHANGE_BACKGROUND(data)` → `None`**
  - **Description**: Applies a background change update from the server.
  - **Inputs**: `data`
  - **Outputs**: None
- **`CLEAR(data)` → `None`**
  - **Description**: Clears strokes as a result of a server-side clear update.
  - **Inputs**: `data`
  - **Outputs**: None

### Class name: `CanvasContainer` (`src/clnt/canvas_container.py`)
**Description**: A simple container widget that centers its child (typically the drawing canvas) within a vertically and horizontally stretched layout and paints a unified background color behind it.

**Variables**:
- **`child_widget`** (Instance): The wrapped canvas or widget. Type: `QWidget`.

**Methods**:
- **`__init__(child_widget)` → `None`**
  - **Description**: Configures nested layouts to center the child widget with stretch spacers.
  - **Inputs**: `child_widget`
  - **Outputs**: None
- **`paintEvent(event)` → `None`**
  - **Description**: Fills the widget’s rectangle with the configured background color on repaint.
  - **Inputs**: `event`
  - **Outputs**: None

### Class name: `CenteredScrollArea` (`src/clnt/scroll_area.py`)
**Description**: A scroll area specialized for hosting the notebook widget; it centers the notebook inside an inner widget and supports Ctrl+mouse-wheel zooming by invoking the notebook’s zoom methods.
**Variables**:
- **`notebook`** (Instance): The hosted `Notebook` (or notebook widget). Type: `Notebook`.

**Methods**:
- **`__init__(notebook_widget)` → `None`**
  - **Description**: Sets up a resizable scroll area with an inner widget that centers the given notebook widget.
  - **Inputs**: `notebook_widget`
  - **Outputs**: None
- **`wheelEvent(event)` → `None`**
  - **Description**: When Ctrl is pressed, converts wheel movements to zoom-in or zoom-out calls on the notebook; otherwise passes the event to the default scroll behavior.
  - **Inputs**: `event`
  - **Outputs**: None

### Class name: `Stroke` (`src/clnt/stroke.py`)
**Description**: Represents a single drawn stroke as a sequence of points with corresponding timestamps, a pen color, and a pen size. It supports hit-testing for selection and serializes itself for storage or transmission.

**Variables**:
- **`points`** (Instance): List of `QPoint` positions. Type: `list`.
- **`times`** (Instance): List of timestamps per point. Type: `list`.
- **`pen_color`** (Instance): Stroke color. Type: `QColor`.
- **`pen_size`** (Instance): Stroke width. Type: numeric.
- **`selected`** (Instance): Whether the stroke is selected. Type: `bool`.
- **`id`** (Instance): Integer identifier. Type: `int`.

**Methods**:
- **`__init__(points, times, pen_color, pen_size, id)` → `None`**
  - **Description**: Normalizes the list of input points to `QPoint` objects, sets times, color, size, and id, and initializes `selected=False`.
  - **Inputs**: `points`; `times`; `pen_color`; `pen_size`; `id`
  - **Outputs**: None
- **`contains_point(pt, tolerance)` → `bool`**
  - **Description**: Returns `True` if the given point is within a specified distance of any segment of the stroke.
  - **Inputs**: `pt`; `tolerance`
  - **Outputs**: See return type: bool
- **`point_line_distance(p, a, b)` → `float`**
  - **Description**: Static helper computing the minimal distance between a point and a line segment.
  - **Inputs**: `p`; `a`; `b`
  - **Outputs**: See return type: float
- **`__dict__()` → `dict`**
  - **Description**: Serializes points as coordinate tuples, and includes times, pen color hex string, pen size, and id.
  - **Inputs**: None
  - **Outputs**: See return type: dict

### Class name: `AccessDialog` (`src/clnt/access.py`)
**Description**: A modal dialog for managing per-user access levels to a notebook. It builds a row of username labels and permission combo boxes for existing access entries and exposes the updated mapping to callers.

**Variables**:
- **`access_levels`** (Instance): List of access level strings (e.g. No Access, View, Edit, Admin). Type: `list`.
- **`user_boxes`** (Instance): Dict mapping username to `QComboBox` for that user's level. Type: `dict`.

**Methods**:
- **`__init__(users_with_access, parent=None)` → `None`**
  - **Description**: Builds the dialog UI with one row per user, pre-selecting the combo box based on the user’s current access level and adding Save and Cancel buttons.
  - **Inputs**: `users_with_access`; `parent`
  - **Outputs**: None
- **`get_access_data()` → `dict[str, str]`**
  - **Description**: Returns a mapping from each username to the selected access level string (e.g., `"Admin"`, `"Edit"`).
  - **Inputs**: None
  - **Outputs**: See return type: dict[str, str]

### Class name: `FlowLayout` (`src/clnt/flow_layout.py`)
**Description**: Custom `QLayout` implementation that arranges child widgets in a flowing, word-wrap–style manner. Used to lay out notebook tiles in the main window, automatically wrapping them as the available width changes.

**Variables**:
- **`itemList`** (Instance): List of layout items (wrapped widgets). Type: `list`.

**Methods**:
- **`__init__(parent=None)` → `None`**
  - **Description**: Initializes the layout with no items, default margins, and spacing.
  - **Inputs**: `parent`
  - **Outputs**: None
- **`addItem(item)` → `None`**
  - **Description**: Adds a layout item to the internal list.
  - **Inputs**: `item`
  - **Outputs**: None
- **`count()` → `int`**
  - **Description**: Returns the number of items in the layout.
  - **Inputs**: None
  - **Outputs**: See return type: int
- **`itemAt(index)` → `QLayoutItem | None`**
  - **Description**: Retrieves the item at the given index or `None` if out of range.
  - **Inputs**: `index`
  - **Outputs**: See return type: QLayoutItem | None
- **`takeAt(index)` → `QLayoutItem | None`**
  - **Description**: Removes and returns the item at the given index or `None` if invalid.
  - **Inputs**: `index`
  - **Outputs**: See return type: QLayoutItem | None
- **`expandingDirections()` → `Qt.Orientation`**
  - **Description**: Indicates that the layout does not expand in any orientation on its own.
  - **Inputs**: None
  - **Outputs**: See return type: Qt.Orientation
- **`hasHeightForWidth()` → `bool`**
  - **Description**: Signals that the layout’s height depends on its width.
  - **Inputs**: None
  - **Outputs**: See return type: bool
- **`heightForWidth(width)` → `int`**
  - **Description**: Computes the required height for a given width by running the layout in test mode.
  - **Inputs**: `width`
  - **Outputs**: See return type: int
- **`setGeometry(rect)` → `None`**
  - **Description**: Applies geometry and physically positions child items according to the flow rules.
  - **Inputs**: `rect`
  - **Outputs**: None
- **`sizeHint()` → `QSize`**
  - **Description**: Returns a general recommended size based on the minimum size.
  - **Inputs**: None
  - **Outputs**: See return type: QSize
- **`minimumSize()` → `QSize`**
  - **Description**: Computes the smallest bounding size that can contain all items.
  - **Inputs**: None
  - **Outputs**: See return type: QSize
- **`do_layout(rect, test_only)` → `int`**
  - **Description**: Core layout routine that either computes or applies positions for all items, returning the total height used.
  - **Inputs**: `rect`; `test_only`
  - **Outputs**: See return type: int
- **`process_item(item, rect, x, y, line_height, spacing_x, spacing_y, test_only)` → `tuple[int, int, int]`**
  - **Description**: Places a single item, handling wrapping to new rows as needed, and returns updated coordinates and line height.
  - **Inputs**: `item`; `rect`; `x`; `y`; `line_height`; `spacing_x`; `spacing_y`; `test_only`
  - **Outputs**: See return type: tuple[int, int, int]
- **`clear(delete_widgets=True)` → `None`**
  - **Description**: Removes all items; optionally schedules their associated widgets for deletion.
  - **Inputs**: `delete_widgets`
  - **Outputs**: None
- **`reset_items(new_widgets=None)` → `None`**
  - **Description**: Clears current items and optionally adds a new list of widgets as children.
  - **Inputs**: `new_widgets`
  - **Outputs**: None

### Class name: `ToolbarsEnum` (`src/clnt/style.py`)
**Description**: Enum defining indices for the various drawing toolbars (page, pen, marker, eraser, select). It allows the `NotebookArea` logic to refer to toolbars via clear symbolic names rather than raw integers.

**Variables**:
- **`PAGE`** (Enum member): Index for page toolbar. Value: 0.
- **`PEN`** (Enum member): Index for pen toolbar. Value: 1.
- **`MARKER`** (Enum member): Index for marker toolbar. Value: 2.
- **`ERASER`** (Enum member): Index for eraser toolbar. Value: 3.
- **`SELECT`** (Enum member): Index for select toolbar. Value: 4.

**Methods**:
- **Enum standard methods** inherited from `Enum` (no custom methods).

### Class name: `Reg` (`src/clnt/winreg_file.py`)
**Description**: Thin wrapper around the Windows registry that reads the server IP and port configuration from a specific key. Used during client startup to locate the server dynamically.

**Variables**:
- None (uses module-level `VALUES_COUNT`, `IP`, `PORT` from constants).

**Methods**:
- **`read_reg()` → `tuple[str, int]`**
  - **Description**: Opens the `HKEY_LOCAL_MACHINE\SOFTWARE\Technition Server` key, iterates values to override default IP and port if present, prints the discovered values, and returns `(ip, port)`.
  - **Inputs**: None
  - **Outputs**: See return type: tuple[str, int]

### Class name: `Protocol` (`src/clnt/protocol.py`)
**Description**: Client-side mirror of the server protocol that handles length-prefixed text and binary messages with optional AES encryption. It provides an identical interface to the server’s `Protocol` so that shared key exchange logic can run on both ends.
**Variables**:
- **Class**: `STOP_RECV`, `KEY`, `SOCK` (same semantics as server side).
**Methods**:
- **`send(conn, data)` → `None`**
  - **Description**: Sends a string payload with length prefix and optional encryption.
  - **Inputs**: `conn`; `data`
  - **Outputs**: None
- **`send_bin(conn, data_bit)` → `None`**
  - **Description**: Sends raw bytes in length-prefixed form, optionally encrypted.
  - **Inputs**: `conn`; `data_bit`
  - **Outputs**: None
- **`recv(conn)` → `str`**
  - **Description**: Receives and decrypts a payload, returning the decoded string.
  - **Inputs**: `conn`
  - **Outputs**: See return type: str
- **`recv_bin(conn)` → `bytes`**
  - **Description**: Receives and decrypts a payload, returning raw bytes.
  - **Inputs**: `conn`
  - **Outputs**: See return type: bytes

### Class name: `KeyExchange` (`src/clnt/key_exchange.py`)
**Description**: Client-side counterpart to the server’s key exchange logic, providing the same static methods and using the client `Protocol` module. It encapsulates the send-first and receive-first ECDH handshake flows.
**Variables**:
- **None (all stateless static methods).**
**Methods**:
- **`send_recv_key(conn)` → `bytes`**
  - **Description**: Sends the client’s ECDH public key, receives the server’s public key, and returns the derived shared key.
  - **Inputs**: `conn`
  - **Outputs**: See return type: bytes
- **`recv_send_key(conn)` → `bytes`**
  - **Description**: Receives the peer’s key, sends the client’s key, and derives the shared key (used where the client plays the “server-like” role).
  - **Inputs**: `conn`
  - **Outputs**: See return type: bytes

### Class name: `AESCipher` (`src/clnt/aes_cipher.py`)
**Description**: Client-side AES-CBC cipher implementation; functionally identical to the server version but scoped to client modules. It encrypts/decrypts bytes and can generate random symmetric keys.

**Variables**:
- **`KEY_RANDOM_BYTES`** (Module constant): Length of random bytes for key generation. Type: int.
- **`NO_OVER`** (Module constant): Padding helper constant. Type: int.

**Methods**:
- **`encrypt(key, raw)` → `bytes`**
  - **Description**: Pads and encrypts raw bytes, returning base64-encoded IV + ciphertext.
  - **Inputs**: `key`; `raw`
  - **Outputs**: See return type: bytes
- **`decrypt(key, enc)` → `bytes`**
  - **Description**: Decrypts base64-encoded content and strips padding, returning cleartext bytes.
  - **Inputs**: `key`; `enc`
  - **Outputs**: See return type: bytes
- **`_pad(s)` → `bytes`**
  - **Description**: Applies PKCS7-style padding.
  - **Inputs**: `s`
  - **Outputs**: See return type: bytes
- **`_unpad(s)` → `bytes`**
  - **Description**: Removes PKCS7-style padding.
  - **Inputs**: `s`
  - **Outputs**: See return type: bytes
- **`generate_key()` → `bytes`**
  - **Description**: Generates a random 256-bit key using SHA-256 over random bytes.
  - **Inputs**: None
  - **Outputs**: See return type: bytes

### Class name: `DiffieHellman` (`src/clnt/diffie_hellman.py`)
**Description**: Client-side ECDH helper identical in behavior to the server’s `DiffieHellman` class. It manages keypair creation, public key serialization, and shared key derivation.
**Variables**:
- **Instance**: `diffieHellman` (private key), `public_key` (public key).
**Methods**:
- **`__init__()` → `None`**
  - **Description**: Creates a new EC keypair on SECP384R1.
  - **Inputs**: None
  - **Outputs**: None
- **`serialize_public_key()` → `bytes`**
  - **Description**: Serializes the public key to PEM.
  - **Inputs**: None
  - **Outputs**: See return type: bytes
- **`deserialize_public_key(data)` → public key object**: Parses a PEM-encoded public key.
- **`get_key(public_key)` → `bytes`**
  - **Description**: Runs ECDH and HKDF-SHA256 to produce a shared key.
  - **Inputs**: `public_key`
  - **Outputs**: See return type: bytes

### Class name: `Hasha256` (`src/clnt/my_sha256.py`)
**Description**: Client-side SHA-256 utility class that mirrors the server’s implementation. It is primarily used for test tooling or local hashing needs on the client.
**Variables**:
- **None (static utility).**
**Methods**:
- **`get_hash(st)` → `bytes`**
  - **Description**: Returns the raw SHA-256 digest of a string.
  - **Inputs**: `st`
  - **Outputs**: See return type: bytes
- **`get_hash_hex(st)` → `str`**
  - **Description**: Returns the hex digest of a string’s SHA-256 hash.
  - **Inputs**: `st`
  - **Outputs**: See return type: str

