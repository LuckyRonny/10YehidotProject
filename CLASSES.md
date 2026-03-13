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
- **Instance**: `my_socket` (main socket), `connection` (main connection tuple `(socket, key)`), `check_socket` (updates socket), `connection_check` (updates connection tuple).
**Methods**:
- **`__init__()` → `None`**: Reads IP/port from the Windows registry, opens and connects two sockets, performs key exchange on each, and constructs connection tuples; exits the process on connection failure.
- **`handle_user_input()` → `None`**: Implements an interactive CLI loop for manual testing that reads user-entered requests, validates them, and sends/receives responses until `"EXIT"` or `"QUIT"`.
- **`valid_request(req_and_prms)` → `bool`**: Static validator that checks that a parsed request/parameter list conforms to expected operation names and parameter counts.
- **`login_check(req_and_prms)` → `bool`**: Static helper validating login requests and guarding against simple SQL injection patterns in username and password.
- **`signup_check(req_and_prms)` → `bool`**: Static helper validating signup requests, similarly checking for illegal characters in username and password.
- **`funcs_check(req_and_prms)` → `bool`**: Static helper validating notebook-related requests such as `add_stroke`, `delete_stroke`, `change_background`, `clear`, `add_page`, and `check_updates`.
- **`send_request_to_server(con, request)` → `None`**: Sends a string request over the given connection tuple using the client `Protocol`.
- **`handle_server_response(con)` → `str`**: Receives a full response string from the given connection tuple and returns it.
- **`send_command(request)` → `str`**: High-level API for other client components; splits and validates the request string, then routes `check_updates` over the update connection and all other requests over the main connection, returning the server response or `"ILLEGAL REQUEST"`.

### Class name: `LoginWindow` (`src/clnt/log_in.py`)
**Description**: The initial PyQt6 window that presents username and password fields to the user. It owns a `Client` instance, triggers login attempts, displays errors, and opens the main window on successful authentication.
**Variables**:
- **Instance**: `client` (shared `Client` instance), `username_line_edit`, `password_line_edit`, `error_label`, and various layout widgets stored implicitly by Qt (central widget, layouts, etc.).
**Methods**:
- **`__init__()` → `None`**: Sets window title, styling, minimum size, builds the central UI, and constructs the `Client`.
- **`create_central_widget()` → `None`**: Assembles the central widget containing username and password line edits, error label, and login/signup buttons.
- **`create_central_layout(central_layout, username_layout, password_layout, button_layout, error_layout)` → `None`**: Lays out the login form with margins and vertical spacing.
- **`create_layout(layout, name)` → `QtWidgets.QLineEdit`**: Utility method that adds a label and line edit to a horizontal layout and returns the created line edit.
- **`create_error_layout(layout)` → `QLabel`**: Creates and returns an error label centered in its layout row.
- **`create_button_layout(button_layout)` → `None`**: Places the Login and Sign up buttons into the provided layout.
- **`create_button(name, func)` → `QPushButton`**: Builds a styled button wired to the specified clicked handler.
- **`login_button_clicked()` → `None`**: Collects user input, sends a login request via `Client`, handles error states, and opens the `MainWindow` on success.
- **`signin_button_clicked()` → `None`**: Opens the `SignupWindow` and hides the login window to transition to the registration flow.

### Class name: `SignupWindow` (`src/clnt/sign_up.py`)
**Description**: A PyQt6 window for registering new users. It presents username, display name, and password fields, and on success opens the main window while linking back to the login window that spawned it.
**Variables**:
- **Instance**: `username_line_edit`, `name_line_edit`, `password_line_edit`, `error_label`, `client` (own `Client` instance), `login` (reference to parent `LoginWindow`).
**Methods**:
- **`__init__(login)` → `None`**: Builds the central layout with input fields and error area, initializes a `Client`, and stores the reference to the originating login window.
- **`create_central_layout(central_layout, username_layout, name_layout, password_layout, button_layout, error_layout)` → `None`**: Applies margins and stacking for the signup form components.
- **`create_layout(layout, name)` → `QtWidgets.QLineEdit`**: Creates a label/line-edit pair for one input line and returns the line-edit.
- **`create_error_layout(layout)` → `QLabel`**: Creates an error label with spacing and returns it.
- **`create_button_layout(button_layout)` → `None`**: Adds the “Sign up” button to the layout and wires its click signal.
- **`signup_button_clicked()` → `None`**: Sends a `signup` request via `Client`, shows specific error text on invalid/duplicate data, or opens the `MainWindow` and closes itself on success.

### Class name: `MainWindow` (`src/clnt/main_window.py`)
**Description**: The primary application dashboard shown after login. It displays a toolbar with user identity, log-out and refresh actions, and an add-notebook control, plus a flow layout of notebook tiles for quick access, and a floating frame for creating new notebooks.
**Variables**:
- **Instance**: `login_window` (back-reference for log out), `central_widget`, `layout` (main vertical layout), `main_toolbar`, `box` (floating add-notebook frame), `box_margin_right`, `box_margin_top`, `client` (shared `Client`), `notebooks_layout` (flow layout), `id` (user id string), `notebooks_dict` (notebook name → button), `names_perms` (notebook name → permission int).
**Methods**:
- **`__init__(client, id, login_window, name)` → `None`**: Initializes window styling and layout, builds the toolbar and floating add frame, creates the flow layout container, stores the user id and login window, and loads notebooks for the user.
- **`create_flow_layout()` → `None`**: Constructs a `FlowLayout`, wraps it in a `QWidget`, and adds it to the main layout.
- **`create_toolbar(name)` → `None`**: Builds the main toolbar with the user’s name label, log out and refresh buttons, spacer, and add-notebook button.
- **`create_add_button()` → `QPushButton`**: Creates the plus icon button used to toggle the floating add-notebook frame.
- **`create_log_out_button()` → `None`**: Adds a styled “log out” button to the toolbar and wires it to `log_out`.
- **`create_refresh_button()` → `None`**: Adds a refresh button with icon to the toolbar and wires it to `refresh`.
- **`refresh()` → `None`**: Clears the notebook tile layout and reloads notebooks for the current user id.
- **`log_out()` → `None`**: Clears login input fields in the `LoginWindow`, shows it again, and closes the main window.
- **`create_add_frame()` → `None`**: Creates the floating frame containing the notebook-name label, line-edit, and create button; computes and stores its margins.
- **`create_box()` → `None`**: Instantiates and styles the `QFrame` that acts as the floating add notebook box.
- **`create_button(line_edit)` → `QPushButton`**: Generates the “create” button that triggers notebook creation using the text from the associated line-edit.
- **`create_new_notebook_frame()` → `None`**: Toggles the visibility of the floating add frame and positions it on top when shown.
- **`create_new_notebook(id, notebook_name)` → `None`**: Builds a new empty `Notebook` object, serializes it, sends `add_notebook_to_db`, and on success creates a new notebook button tile wired to `open_notebook`.
- **`resizeEvent(event)` → `None`**: Repositions the floating add frame whenever the window is resized.
- **`reposition_box()` → `None`**: Computes and sets the top-right location for the floating add frame relative to the central widget.
- **`create_notebook_button(name)` → `QPushButton`**: Creates a fixed-size push button representing a notebook tile.
- **`load_notebooks_for_user(user_id)` → `None`**: Uses `clients_notebooks` to populate the flow layout with buttons for each notebook and stores permission levels.
- **`open_notebook(name)` → `None`**: Fetches notebook content from the server, constructs a `NotebookArea`, shows it, and hides the main window.

### Class name: `NotebookArea` (`src/clnt/notebook_area.py`)
**Description**: Hosts the interactive view of a single notebook, including drawing tools, page navigation controls, and background selection. It also runs a background thread that polls the server for updates and applies them live across pages.
**Variables**:
- **Class**: `notebook_update_signal` (Qt signal carrying updates and a page index).
- **Instance**: `name` (notebook identifier), `notebook_widget` (`Notebook` instance), `current_page` (current page index), `id` (user id string), `client` (`Client`), `main_window` (parent `MainWindow`), `running` (bool for update loop), `main_toolbar`, `sub_toolbars` (list of toolbars), `perm` (permission code), `button_layout`, `scroll_area`, and references to toolbar widgets such as `page_toolbar`, `pen_toolbar`, `marker_toolbar`, `eraser_toolbar`, `select_toolbar`, and their size/color controls.
**Methods**:
- **`__init__(mainwindow, id, client, notebook, name, perm)` → `None`**: Initializes the window, builds the central layout and toolbars, constructs or creates a `Notebook`, sets permission behavior, starts the background polling thread, and connects the update signal.
- **`loop()` → `None`**: Runs in a thread, repeatedly sending `check_updates` with the notebook name and last change time; on receiving non-empty updates, parses them and emits `notebook_update_signal`.
- **`create_toolbars(central_layout, perm)` → `None`**: Creates the main toolbar and sub-toolbars for page, pen, marker, eraser, and select tools, then lays out page navigation controls and content.
- **`save_notebook()` → `None`**: Sends an `add_notebook` request to persist the current notebook state on the server.
- **`clear_page(page_id)` → `None`**: Sends a `clear` command for the specified page to the server.
- **`change_background(type, page_id)` → `None`**: Sends a `change_background` command to set the background type for a page on the server.
- **`add_stroke(stroke, id_page, id)` → `str`**: Serializes a `Stroke` object and sends an `add_stroke` command; returns the stroke id allocated by the server.
- **`add_page(id_page, page)` → `None`**: Sends an `add_page` command with the serialized `DrawingCanvas` state to create a new page.
- **`delete_stroke(id_page, id)` → `None`**: Sends a `delete_stroke` command for the given page and stroke id.
- **`add_to_central_layout(central_layout, perm)` → `None`**: Configures and inserts the scroll area and bottom buttons into the central layout.
- **`create_central_layout()` → `tuple[QVBoxLayout, QWidget]`**: Creates and returns the central layout and associated widget.
- **`show_sub_toolbar(index)` → `None`**: Toggles visibility for sub-toolbars based on which tool button is pressed and sets the current drawing tool accordingly.
- **`set_tool_and_size_and_color(i, toolbar)` → `None`**: Sets the active tool, brush size, and color according to the selected toolbar type.
- **`tool_size_and_color(tool, size, color)` → `None`**: Helper that sets the tool, then size and color for the current canvas.
- **`create_buttons(perm)` → `None`**: Adds toolbar buttons such as clear, back, and (for admins) access management.
- **`create_buttons_layout(perm)` → `None`**: Creates the bottom navigation layout with previous, next, and optionally add-page buttons.
- **`create_sub_toolbars(central_layout)` → `None`**: Initializes all sub-toolbars and corresponding toggle buttons.
- **`create_sub_toolbar_page/pen/marker/eraser/select(...)` → `None`**: Build each sub-toolbar, add its controls, and wire it to the main toolbar.
- **`set_checked(i, toolbar, is_visible)` → `None`**: Manages the checked state and visibility of toolbar buttons when switching tools.
- **`toolbar_button(button, index)` → `None`**: Wires a toolbar button to show the appropriate sub-toolbar.
- **`clear_current_page()` → `None`**: Clears the current page’s strokes via the active `DrawingCanvas`.
- **`back_current_page()` → `None`**: Undoes the last stroke on the current page.
- **`set_tool_for_current(tool_name)` → `None`**: Applies a tool name (pen, marker, eraser, select, page) to the current canvas.
- **`no_tool_for_all()` → `None`**: Disables tools on all pages (used for view-only permissions).
- **`set_size_for_current(size)` → `None`**: Adjusts pen size on the current canvas.
- **`set_color_for_current(color)` → `None`**: Adjusts pen/marker color on the current canvas.
- **`set_background_for_current(background)` → `None`**: Changes the background type of the current page and persists it.
- **`toolbar_features(toolbar)` → `None`**: Applies shared style and behavior to a sub-toolbar and tracks it.
- **`main_toolbar_button(button, func)` → `None`**: Styles a main toolbar button and connects it to its handler.
- **`create_page_buttons()` → `tuple[QPushButton, QPushButton, QPushButton]`**: Builds the blank, lines, and grid background selection buttons.
- **`create_page_toolbar()` → `QToolBar`**: Creates the page background selection toolbar.
- **`create_select_toolbar()` → `QToolBar`**: Creates the (currently empty) selection toolbar.
- **`create_pen_toolbar_and_size_and_color()` → `tuple[QToolBar, QSpinBox, QComboBox]`**: Constructs the pen toolbar with size and color controls.
- **`create_marker_toolbar_and_size_and_color()` → `tuple[QToolBar, QSpinBox, QComboBox]`**: Constructs the marker toolbar with width and color selectors.
- **`create_eraser_toolbar_and_size()` → `tuple[QToolBar, QSpinBox]`**: Builds the eraser toolbar with size selection.
- **`create_size_button(size_range, start_value, size_step)` → `QSpinBox`**: Creates a spin box configured for choosing pen/marker/eraser size.
- **`create_color_button(colors)` → `QComboBox`**: Creates a drop-down with the provided color names and wires it to color changes.
- **`closeEvent(event)` → `None`**: Restores the parent main window, stops the update loop, and accepts the close event.
- **`parse_users_access_response(resp)` → `list[tuple[str, int]]`**: Parses the server’s `all_users` response into a list of `(username, permission_int)`.
- **`apply_access_changes(access_data)` → `None`**: Sends `change_access` requests for each user in the access data mapping.
- **`open_access_dialog()` → `None`**: Fetches current access levels, opens the `AccessDialog`, and applies user changes on acceptance.
- **`reload_notebook(data, current_page)` → `None`**: Applies a list of server updates to the notebook widget, repaints pages, restores the current page, and re-applies view-only restrictions if needed.

### Class name: `Notebook` (`src/clnt/notebook.py`)
**Description**: Client-side container for a notebook’s set of drawing pages, implemented as a stacked widget. It manages page creation, navigation, zooming, and applying server-side update events to the individual canvases.
**Variables**:
- **Instance**: `notebook_area` (parent area), `pages` (`QStackedWidget`), `pages_list` (list of `DrawingCanvas` instances), `global_scale_factor`, `main_layout`, `last_change` (timestamp).
**Methods**:
- **`__init__(pages, last_change, notebook_area)` → `None`**: Initializes a notebook with existing page data or creates the first blank page, sets up the stacked widget layout, and links back to the owning `NotebookArea`.
- **`__dict__()` → `dict`**: Serializes the notebook into a dict with `pages` and `last_change`, with each page serialized via its canvas `__dict__`.
- **`current_canvas()` → `DrawingCanvas | None`**: Returns the currently visible `DrawingCanvas` page.
- **`add_page(page, notify_server=True)` → `None`**: Adds an existing or new page canvas to the stacked widget, optionally informs the server of the new page, and updates the current page index.
- **`prev_page()` → `None`**: Navigates to the previous page if possible and updates the `NotebookArea`’s current page index.
- **`next_page()` → `None`**: Navigates to the next page if not already at the last, updating the current page index accordingly.
- **`zoom_in()` → `None`**: Increases the global zoom factor within min/max bounds and applies it to all pages.
- **`zoom_out()` → `None`**: Decreases the global zoom factor within bounds and applies it to all pages.
- **`apply_zoom_to_all()` → `None`**: Resizes and repaints every page canvas according to the current global zoom.
- **`update_notebook(ts, type, page, data)` → `None`**: Applies a server update by either adding a new page (`ADD_PAGE`) or forwarding commands (e.g., `ADD_STROKE`, `DELETE_STROKE`, `CLEAR`, `CHANGE_BACKGROUND`) to the correct page; updates `last_change`.
- **`delete_old_data()` → `None`**: Clears all page widgets and resets the stack, used when reloading notebook data from scratch.

### Class name: `DrawingCanvas` (`src/clnt/canvas.py`)
**Description**: A custom drawing widget that allows pen and marker strokes, erasing, selecting and moving strokes, and zooming via pinch and scroll gestures. It maintains a rendered background (blank, lined, or grid) and communicates stroke changes back to the server through its owning `NotebookArea`.
**Variables**:
- **Instance**: `background_layer` (pixmap for background), `strokes` (list of `Stroke`), `current_stroke_points`, `current_stroke_times`, `selected_stroke`, `drawing` (bool), `history` (list of previous strokes), `last_point`, `first_point`, `pen_color`, `pen_size`, `tool` (string), `page_type` (background type), `is_gesturing` (bool), `scale_factor`, `base_width`, `base_height`, `notebook_area` (parent), `id` (page id), `stroke_id` (next local stroke id).
**Methods**:
- **`__init__(width, height, strokes, page_type, notebook_area, stroke_id, id)` → `None`**: Initializes background, restoring strokes (if any), history and pen state, zoom parameters, parent reference, and stroke id counters.
- **`_handle_eraser_click(pos)` → `None`**: Removes the first stroke that intersects the hit point with eraser tolerance and notifies the `NotebookArea` to delete the stroke on the server.
- **`__dict__()` → `dict`**: Serializes the canvas state including dimensions, serialized strokes, page type, current stroke id, and page id.
- **`create_background_layer(width, height)` → `None`**: Sets a fixed size and creates the initial white background pixmap.
- **`create_strokes_params(strokes)` → `None`**: Initializes the strokes list from serialized data and sets up transient stroke-drawing state.
- **`create_history_params()` → `None`**: Initializes undo/history-related attributes and last/first point placeholders.
- **`create_pen_params(page_type)` → `None`**: Sets the default pen color, size, tool type, and applies the initial page background style.
- **`create_zoom_in_params(width, height)` → `None`**: Enables pinch gestures and records base width/height and scale factor.
- **`paintEvent(event)` → `None`**: Renders the background, all existing strokes, and the currently drawn stroke with proper scaling and anti-aliasing.
- **`draw_strokes(painter)` → `None`**: Iterates through all stored strokes, drawing them and highlighting selected ones.
- **`draw_background(painter)` → `None`**: Fills the widget with the surrounding color and draws the scaled background pixmap.
- **`draw_current_stroke(painter)` → `None`**: Draws the in-progress stroke using the current pen parameters.
- **`draw_stroke(stroke, painter)` → `None`**: Renders a single stroke as a polyline.
- **`mousePressEvent(event)` → `None`**: Handles left-button presses to start drawing (pen/marker), select strokes, or erase strokes depending on the active tool.
- **`check_which_selected(pos)` → `None`**: Walks strokes from last to first, marking as selected the first stroke that contains the click point.
- **`create_pen(pen_size, pen_color)` → `QtGui.QPen`**: Creates and returns a configured pen for drawing.
- **`mouseMoveEvent(event)` → `None`**: While dragging, either moves the selected stroke or adds points to the current drawing stroke.
- **`move_selected_stroke(e, pos)` → `bool`**: Shifts the selected stroke by the pointer delta and returns `True` if a move was performed.
- **`distance(point1, point2)` → `float`**: Static helper computing Euclidean distance between two points.
- **`_are_last_points_close(point_list, time_list, close_points_distance, close_points_time)` → `bool`**: Determines whether a drawn stroke should be treated as a straight line based on spatial and temporal thresholds.
- **`mouseReleaseEvent(event)` → `None`**: Finalizes a stroke or a selection move; may send new or updated strokes to the server via `NotebookArea`.
- **`add_new_stroke()` → `Stroke | None`**: Creates either a straight-line stroke or a freehand stroke from accumulated points, increments the stroke id, and returns the new stroke.
- **`create_straight_line()` → `Stroke`**: Builds and appends a new `Stroke` using only the first and last points, clearing the in-progress state.
- **`end_stroke()` → `Stroke`**: Converts the current stroke point list into a `Stroke`, appends it, clears the buffers, and returns it.
- **`clear_canvas()` → `None`**: Clears all strokes and notifies the `NotebookArea` to clear the corresponding page on the server.
- **`draw_all_canvas()` → `QtGui.QPixmap`**: Renders the entire canvas (background and strokes) to an off-screen pixmap and returns it.
- **`set_tool(tool_type)` → `None`**: Sets the current drawing tool (pen, marker, eraser, select, page, no).
- **`change_pen_size(size)` → `None`**: Adjusts the pen or eraser size based on the active tool.
- **`change_pen_color(i)` → `None`**: Sets pen or marker color using palette indices and appropriate alpha levels.
- **`back()` → `None`**: Removes the most recently drawn stroke, and if a `NotebookArea` is present, instructs the server to delete it.
- **`zoom_in()` / `zoom_out()` → `None`**: Adjusts the `scale_factor` within bounds and updates the widget size.
- **`_update_size()` → `None`**: Recomputes fixed size from base dimensions and scale factor, then repaints.
- **`event(event)` → `bool`**: Intercepts gesture events and delegates pinch gestures to `gesture_event`.
- **`gesture_event(event)` → `bool`**: Handles pinch gestures by toggling `is_gesturing` and relaying to `handle_pinch`.
- **`handle_pinch(pinch)` → `None`**: Updates the scale factor based on pinch scaling and resizes/redraws accordingly.
- **`blank()` → `None`**: Sets a blank white background for the page.
- **`lines()` → `None`**: Draws ruled lines and margins on the background pixmap.
- **`_draw_grid_background()` → `None`**: Draws a grid pattern on the background pixmap.
- **`grid()` → `None`**: Sets the page type to grid and applies the grid background.
- **`ADD_STROKE(data)` → `None`**: Applies a stroke insertion update from the server, replacing any stroke with the same id.
- **`DELETE_STROKE(id)` → `None`**: Processes a server-side delete stroke update by removing the stroke with the matching id.
- **`CHANGE_BACKGROUND(data)` → `None`**: Applies a background change update from the server.
- **`CLEAR(data)` → `None`**: Clears strokes as a result of a server-side clear update.

### Class name: `CanvasContainer` (`src/clnt/canvas_container.py`)
**Description**: A simple container widget that centers its child (typically the drawing canvas) within a vertically and horizontally stretched layout and paints a unified background color behind it.
**Variables**:
- **Instance**: `child_widget` (wrapped canvas), plus its internal vertical and horizontal layouts managed by Qt.
**Methods**:
- **`__init__(child_widget)` → `None`**: Configures nested layouts to center the child widget with stretch spacers.
- **`paintEvent(event)` → `None`**: Fills the widget’s rectangle with the configured background color on repaint.

### Class name: `CenteredScrollArea` (`src/clnt/scroll_area.py`)
**Description**: A scroll area specialized for hosting the notebook widget; it centers the notebook inside an inner widget and supports Ctrl+mouse-wheel zooming by invoking the notebook’s zoom methods.
**Variables**:
- **Instance**: `notebook` (the hosted `Notebook` or notebook widget), plus the inner center widget and layout.
**Methods**:
- **`__init__(notebook_widget)` → `None`**: Sets up a resizable scroll area with an inner widget that centers the given notebook widget.
- **`wheelEvent(event)` → `None`**: When Ctrl is pressed, converts wheel movements to zoom-in or zoom-out calls on the notebook; otherwise passes the event to the default scroll behavior.

### Class name: `Stroke` (`src/clnt/stroke.py`)
**Description**: Represents a single drawn stroke as a sequence of points with corresponding timestamps, a pen color, and a pen size. It supports hit-testing for selection and serializes itself for storage or transmission.
**Variables**:
- **Instance**: `points` (list of `QPoint`), `times` (list of timestamps), `pen_color` (`QColor`), `pen_size` (numeric width), `selected` (bool), `id` (integer identifier).
**Methods**:
- **`__init__(points, times, pen_color, pen_size, id)` → `None`**: Normalizes the list of input points to `QPoint` objects, sets times, color, size, and id, and initializes `selected=False`.
- **`contains_point(pt, tolerance)` → `bool`**: Returns `True` if the given point is within a specified distance of any segment of the stroke.
- **`point_line_distance(p, a, b)` → `float`**: Static helper computing the minimal distance between a point and a line segment.
- **`__dict__()` → `dict`**: Serializes points as coordinate tuples, and includes times, pen color hex string, pen size, and id.

### Class name: `AccessDialog` (`src/clnt/access.py`)
**Description**: A modal dialog for managing per-user access levels to a notebook. It builds a row of username labels and permission combo boxes for existing access entries and exposes the updated mapping to callers.
**Variables**:
- **Instance**: `access_levels` (list of label strings), `user_boxes` (dict mapping usernames to `QComboBox` widgets).
**Methods**:
- **`__init__(users_with_access, parent=None)` → `None`**: Builds the dialog UI with one row per user, pre-selecting the combo box based on the user’s current access level and adding Save and Cancel buttons.
- **`get_access_data()` → `dict[str, str]`**: Returns a mapping from each username to the selected access level string (e.g., `"Admin"`, `"Edit"`).

### Class name: `FlowLayout` (`src/clnt/flow_layout.py`)
**Description**: Custom `QLayout` implementation that arranges child widgets in a flowing, word-wrap–style manner. Used to lay out notebook tiles in the main window, automatically wrapping them as the available width changes.
**Variables**:
- **Instance**: `itemList` (list of layout items).
**Methods**:
- **`__init__(parent=None)` → `None`**: Initializes the layout with no items, default margins, and spacing.
- **`addItem(item)` → `None`**: Adds a layout item to the internal list.
- **`count()` → `int`**: Returns the number of items in the layout.
- **`itemAt(index)` → `QLayoutItem | None`**: Retrieves the item at the given index or `None` if out of range.
- **`takeAt(index)` → `QLayoutItem | None`**: Removes and returns the item at the given index or `None` if invalid.
- **`expandingDirections()` → `Qt.Orientation`**: Indicates that the layout does not expand in any orientation on its own.
- **`hasHeightForWidth()` → `bool`**: Signals that the layout’s height depends on its width.
- **`heightForWidth(width)` → `int`**: Computes the required height for a given width by running the layout in test mode.
- **`setGeometry(rect)` → `None`**: Applies geometry and physically positions child items according to the flow rules.
- **`sizeHint()` → `QSize`**: Returns a general recommended size based on the minimum size.
- **`minimumSize()` → `QSize`**: Computes the smallest bounding size that can contain all items.
- **`do_layout(rect, test_only)` → `int`**: Core layout routine that either computes or applies positions for all items, returning the total height used.
- **`process_item(item, rect, x, y, line_height, spacing_x, spacing_y, test_only)` → `tuple[int, int, int]`**: Places a single item, handling wrapping to new rows as needed, and returns updated coordinates and line height.
- **`clear(delete_widgets=True)` → `None`**: Removes all items; optionally schedules their associated widgets for deletion.
- **`reset_items(new_widgets=None)` → `None`**: Clears current items and optionally adds a new list of widgets as children.

### Class name: `ToolbarsEnum` (`src/clnt/style.py`)
**Description**: Enum defining indices for the various drawing toolbars (page, pen, marker, eraser, select). It allows the `NotebookArea` logic to refer to toolbars via clear symbolic names rather than raw integers.
**Variables**:
- **Enum members**: `PAGE`, `PEN`, `MARKER`, `ERASER`, `SELECT` (each mapped to an integer index).
**Methods**:
- **Enum standard methods** inherited from `Enum` (no custom methods).

### Class name: `Reg` (`src/clnt/winreg_file.py`)
**Description**: Thin wrapper around the Windows registry that reads the server IP and port configuration from a specific key. Used during client startup to locate the server dynamically.
**Variables**:
- **Class**: (relies on module-level `VALUES_COUNT` and imported `IP`, `PORT` constants).
**Methods**:
- **`read_reg()` → `tuple[str, int]`**: Opens the `HKEY_LOCAL_MACHINE\SOFTWARE\Technition Server` key, iterates values to override default IP and port if present, prints the discovered values, and returns `(ip, port)`.

### Class name: `Protocol` (`src/clnt/protocol.py`)
**Description**: Client-side mirror of the server protocol that handles length-prefixed text and binary messages with optional AES encryption. It provides an identical interface to the server’s `Protocol` so that shared key exchange logic can run on both ends.
**Variables**:
- **Class**: `STOP_RECV`, `KEY`, `SOCK` (same semantics as server side).
**Methods**:
- **`send(conn, data)` → `None`**: Sends a string payload with length prefix and optional encryption.
- **`send_bin(conn, data_bit)` → `None`**: Sends raw bytes in length-prefixed form, optionally encrypted.
- **`recv(conn)` → `str`**: Receives and decrypts a payload, returning the decoded string.
- **`recv_bin(conn)` → `bytes`**: Receives and decrypts a payload, returning raw bytes.

### Class name: `KeyExchange` (`src/clnt/key_exchange.py`)
**Description**: Client-side counterpart to the server’s key exchange logic, providing the same static methods and using the client `Protocol` module. It encapsulates the send-first and receive-first ECDH handshake flows.
**Variables**:
- **None (all stateless static methods).**
**Methods**:
- **`send_recv_key(conn)` → `bytes`**: Sends the client’s ECDH public key, receives the server’s public key, and returns the derived shared key.
- **`recv_send_key(conn)` → `bytes`**: Receives the peer’s key, sends the client’s key, and derives the shared key (used where the client plays the “server-like” role).

### Class name: `AESCipher` (`src/clnt/aes_cipher.py`)
**Description**: Client-side AES-CBC cipher implementation; functionally identical to the server version but scoped to client modules. It encrypts/decrypts bytes and can generate random symmetric keys.
**Variables**:
- **Class**: `KEY_RANDOM_BYTES`, `NO_OVER` (same meaning as server).
**Methods**:
- **`encrypt(key, raw)` → `bytes`**: Pads and encrypts raw bytes, returning base64-encoded IV + ciphertext.
- **`decrypt(key, enc)` → `bytes`**: Decrypts base64-encoded content and strips padding, returning cleartext bytes.
- **`_pad(s)` → `bytes`**: Applies PKCS7-style padding.
- **`_unpad(s)` → `bytes`**: Removes PKCS7-style padding.
- **`generate_key()` → `bytes`**: Generates a random 256-bit key using SHA-256 over random bytes.

### Class name: `DiffieHellman` (`src/clnt/diffie_hellman.py`)
**Description**: Client-side ECDH helper identical in behavior to the server’s `DiffieHellman` class. It manages keypair creation, public key serialization, and shared key derivation.
**Variables**:
- **Instance**: `diffieHellman` (private key), `public_key` (public key).
**Methods**:
- **`__init__()` → `None`**: Creates a new EC keypair on SECP384R1.
- **`serialize_public_key()` → `bytes`**: Serializes the public key to PEM.
- **`deserialize_public_key(data)` → public key object**: Parses a PEM-encoded public key.
- **`get_key(public_key)` → `bytes`**: Runs ECDH and HKDF-SHA256 to produce a shared key.

### Class name: `Hasha256` (`src/clnt/my_sha256.py`)
**Description**: Client-side SHA-256 utility class that mirrors the server’s implementation. It is primarily used for test tooling or local hashing needs on the client.
**Variables**:
- **None (static utility).**
**Methods**:
- **`get_hash(st)` → `bytes`**: Returns the raw SHA-256 digest of a string.
- **`get_hash_hex(st)` → `str`**: Returns the hex digest of a string’s SHA-256 hash.

