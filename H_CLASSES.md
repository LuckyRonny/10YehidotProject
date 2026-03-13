## מחלקות בצד השרת

### Server (`src/srvr/server.py`)

**תיאור**: אחראית על מחזור החיים של שרת ה־TCP, כולל ערוץ הפקודות הראשי וערוץ עדכונים נפרד. מקבלת חיבורים נכנסים, מבצעת החלפת מפתחות מבוססת Diffie–Hellman לכל חיבור, ומריצה חוטי ביצוע המטפלים בבקשות רגילות ועדכונים דרך שכבת הפרוטוקול והניתוב.

**משתנים עיקריים**  
- מופעיים: `server_socket` (שקע האזנה ראשי), `update_socket` (שקע האזנה לעדכונים).

**מתודות עיקריות**  
- `__init__(ip, port)` → `None`: יוצר שקעים, קושר אותם ל־IP/פורט, מתחיל האזנה לשני הערוצים, ומסיים את התהליך במקרה כישלון.  
- `handle_clients()` → `None`: לולאת קבלה ללקוחות בערוץ הראשי; עבור כל חיבור חדש מבצע החלפת מפתחות, עוטף את השקע בצמד (שקע, מפתח) ופותח חוט חדש ל־`handle_single_client`, יחד עם חוט רקע ל־`accept_updates`.  
- `accept_updates()` → `None`: לולאת קבלה ללקוחות בערוץ העדכונים; עבור כל חיבור מבצע החלפת מפתחות ומריץ חוט חדש ל־`handle_update_client`.  
- `handle_single_client(conn, address)` → `bool`: לולאת טיפול בלקוח בודד המקבלת בקשות, מעבירה אותן ל־`Methods`, שולחת תגובות ומפסיקה במקרה שגיאה; מחזירה `False` בסיום.  
- `handle_update_client(conn_updates, address)` → `None`: לולאת טיפול בערוץ עדכונים; משרתת רק בקשות `CHECK_UPDATES` ועונה `"NO"` לבקשות אחרות, ומפסיקה בשגיאות.  
- `receive_client_request(conn)` → `tuple[str | None, list[str] | None]`: קוראת הודעה אחת מהלקוח, מפצלת לשם בקשה ורשימת פרמטרים ומחזירה אותן באותיות רישיות; במקרה קלט ריק מחזירה `(None, None)`.  
- `handle_client_request(request, params)` → `str`: מזהה את מתודת היעד במחלקת `Methods` לפי `params[REQUEST_TYPE]`, מפעיל אותה ומחזיר את התשובה כמחרוזת.  
- `send_response_to_client(response, conn)` → `None`: שולחת מחרוזת תשובה ללקוח דרך מחלקת `Protocol`.

---

### UserManager (`src/srvr/user_manager.py`)

**תיאור**: מרכז את כל הפעולות הקשורות למשתמשים על בסיס מסד הנתונים `NotebookDB.db` ב־SQLite. מטפל בהתחברות, הרשמה ושליפת רשימת משתמשים והרשאותיהם למחברת נתונה.

**משתנים עיקריים**  
- מחלקתיים: `NAME_OF_USER` (אינדקס לשם התצוגה בשורת משתמש), `LOGIN_FAIL_RESPONSE` (מחרוזת לכישלון התחברות), `DEFAULT_PERMISSION` (הרשאה ברירת מחדל למחברות), `ALL_USERS_PARAMS_NOTEBOOK_INDEX`, `PERMISSION`, `ID`.

**מתודות עיקריות**  
- `LOGIN(params)` → `str`: בודקת שם משתמש וסיסמה מול טבלת `Users` בעזרת גיבוב SHA‑256 של הסיסמה; מחזירה `"id!name"` במקרה הצלחה או `"False"` אם אין התאמה.  
- `SIGNUP(params)` → `str`: יוצרת רשומת משתמש חדשה בטבלה עם שם משתמש, סיסמה מגובבת ושם תצוגה; מחזירה את המזהה שנוצר כמחרוזת או `"False"` במקרה שם משתמש כפול או שגיאת מסד.  
- `ALL_USERS(params)` → `str`: מחזירה מחרוזת `!`‑מופרדת של `"username,permission"` לכל המשתמשים למעט משתמש אחד, כאשר ההרשאות נלקחות מטבלת `UsersNotebooks` או מה־`DEFAULT_PERMISSION` אם אין רשומה.  
- `get_id_permission(excluded_user, notebook)` → `tuple[list[tuple], list[tuple]]`: שולפת מרשמי המסד זוגות `(user_name, id)` לכל המשתמשים למעט אחד, וכן זוגות `(user, permission)` למחברת מסוימת, ומחזירה את שתי הרשימות.

---

### UserNotebookManager (`src/srvr/user_notebook_manager.py`)

**תיאור**: מחברת בין טבלאות `Users`, `Notebooks` ו־`UsersNotebooks` לצורך שיוך מחברות למשתמשים והגדרת רמות גישה. מנהלת יצירת מחברות חדשות במסד, שליפת מחברות למשתמשים ושינוי הרשאות.

**משתנים עיקריים**  
- מחלקתיים: `PERMISSION`, `CHANGE_ACCESS_PARAMS_ACCESS_INDEX`, `CHANGE_ACCESS_PARAMS_NOTEBOOK_NAME_INDEX`, `NOTEBOOK_ID_ROW_INDEX`, `USER_ID_ROW_INDEX`, `PERMISSION_ROW_INDEX`, `EXIST`, `FIRST`, `PERMISSIONS_ROW`.

**מתודות עיקריות**  
- `ADD_NOTEBOOK_TO_DB(params)` → `str`: מוסיפה מחברת לטבלת `Notebooks` ויוצרת קשר ב־`UsersNotebooks` עם הרשאה נתונה; לאחר מכן קוראת ל־`NotebookManager.ADD_NOTEBOOK`. מחזירה `"ok"` או מחרוזת שגיאה ממסד הנתונים.  
- `add_to_db(notebook_name, user_id, per)` → `None`: מוסיפה את שם המחברת לטבלת `Notebooks` ואת השיוך למשתמש בטבלת `UsersNotebooks` בתוך טרנזקציה; מעלה חריגה במקרה כפילות.  
- `CLIENTS_NOTEBOOKS(params)` → `str`: מחזירה מחרוזת `!`‑מופרדת של `"name,permission"` לכל המחברות של משתמש עם הרשאה שונה מ־3 (אין גישה).  
- `get_all_notebooks(id, cursor, notebooks_names)` → `str`: מתודת עזר הפותרת מזהה מחברת לשמה מטבלת `Notebooks`.  
- `_resolve_user_id(cursor, user_name)` → `int | None`: מחזירה את מזהה המשתמש לפי שם משתמש מהטבלה `Users` או `None` אם לא נמצא.  
- `_resolve_notebook_id(cursor, notebook_name)` → `int | None`: מחזירה את מזהה המחברת לפי השם מטבלת `Notebooks` או `None`.  
- `_user_notebook_exists(cursor, user_id, notebook_id)` → `bool`: בודקת האם קיים קשר משתמש–מחברת בטבלת `UsersNotebooks`.  
- `CHANGE_ACCESS(params)` → `str`: מעדכנת או יוצרת רשומת `UsersNotebooks` עבור שם משתמש, מחברת ורמת גישה; אם לא ניתן לפתור משתמש או מחברת מחזירה `"ok"` ללא שינוי.

---

### NotebookManager (`src/srvr/notebook_manager.py`)

**תיאור**: מנהלת את שמירת המחברות והעדכונים בצד השרת כקובצי JSON, ומספקת פעולות ליצירה, עדכון ומעקב אחרי עמודים ומשיכות. משתמשת במנעול כדי להגן על גישה מקבילית ומייצרת זרם עדכונים שכל לקוח יכול למשוך.

**משתנים עיקריים**  
- מחלקתיים: `lock` (אובייקט `threading.Lock` משותף לכל פעולות המחברות).

**מתודות עיקריות**  
- `_notebook_path(name)` → `str`: מחזירה את נתיב הקובץ שבו נשמרת המחברת המתאימה לשם הנתון.  
- `_updates_path(name)` → `str`: מחזירה את נתיב קובץ ה־JSON שבו נשמר יומן העדכונים עבור אותה מחברת.  
- `_atomic_write(path, data)` → `None`: כותבת את תוכן ה־JSON לקובץ זמני ומחליפה את הקובץ הקיים באופן אטומי כדי למנוע שחיתות.  
- `_load(path, default=None)` → `dict | list | Any`: טוענת JSON מהדיסק אם הקובץ קיים, אחרת מחזירה את ברירת המחדל שסופקה או מילון ריק.  
- `_parse_param(param)` → `dict | Any`: אם הפרמטר הוא מחרוזת – מפענחת אותו לדיקט בעזרת `ast.literal_eval`, אחרת מחזירה אותו כמות שהוא.  
- `GET_NOTEBOOK(params)` → `str`: קוראת את קובץ המחברת עבור שם נתון ומחזירה את הייצוג שלה כמחרוזת (`repr`).  
- `ADD_NOTEBOOK(params)` → `str`: שומרת מחברת מלאה לשם הנתון ויוצרת קובץ עדכונים ריק אם אינו קיים; מחזירה `"ok"`.  
- `ADD_STROKE(params)` → `str`: מוסיפה משיכה לעמוד מסוים, מקצה מזהה חדש אם נדרש, מעדכנת את `last_change`, שומרת את קובץ המחברת ומוסיפה רשומת `"ADD_STROKE"` ליומן העדכונים; מחזירה את מזהה המשיכה כמחרוזת.  
- `DELETE_STROKE(params)` → `str`: מוחקת משיכה מעמוד לפי מזהה, מעדכנת `last_change`, שומרת את המחברת ומוסיפה רשומת `"DELETE_STROKE"`; מחזירה `"ok"` או הודעת שגיאה אם העמוד/המשיכה לא נמצאו.  
- `ADD_PAGE(params)` → `str`: מוסיפה עמוד חדש למחברת (כולל שדות ברירת מחדל ל־`stroke_id` ו־`strokes`), מעדכנת `last_change`, שומרת את המחברת ומוסיפה `"ADD_PAGE"` ליומן; מחזירה `"ok"`.  
- `CLEAR(params)` → `str`: מנקה את כל המשיכות מעמוד מסוים, מעדכנת `last_change`, שומרת את המחברת ומוסיפה `"CLEAR"`; מחזירה `"ok"` או `"page_not_found"`.  
- `CHANGE_BACKGROUND(params)` → `str`: משנה את סוג הרקע (`page_type`) של העמוד, מעדכנת `last_change`, שומרת את המחברת ומוסיפה `"CHANGE_BACKGROUND"`; מחזירה `"ok"` או `"page_not_found"`.  
- `CHECK_UPDATES(params)` → `str`: מסננת את רשימת העדכונים למחברת לפי חותמת זמן, ומחזירה רשימת עדכונים חדשים כמחרוזת.  
- `create_update(notebook_name, ts, type, id_page, data)` → `None`: יוצרת רשומת עדכון (סוג, זמן, עמוד, נתונים), מוסיפה אותה ליומן העדכונים, מקצרת את הרשימה אם חרגה מהגודל המקסימלי ושומרת לדיסק.

---

### Protocol (`src/srvr/protocol.py`)

**תיאור**: מממשת את פרוטוקול התקשורת בצד השרת לשליחה וקבלה של הודעות עם כותרת אורך קבועה. תומכת במטעני טקסט ובינאריים, ובמידת הצורך מצפינה/מפענחת בעזרת AES על בסיס מפתח משותף בצמד החיבור.

**משתנים עיקריים**  
- מחלקתיים: `STOP_RECV` (ערך עצירה ללולאות קריאה), `KEY` (אינדקס המפתח בצמד החיבור), `SOCK` (אינדקס השקע בצמד החיבור).

**מתודות עיקריות**  
- `send(conn, data)` → `None`: מקבלת מחרוזת, מקודדת לבתים, מצפינה אם קיים מפתח, מוסיפה כותרת אורך אפס–מרופדת ושולחת את הנתונים.  
- `send_bin(conn, data_bit)` → `None`: שולחת בתים גולמיים באותו פורמט של כותרת אורך והצפנה כמו `send`.  
- `recv(conn)` → `str`: קוראת את כותרת האורך, לאחר מכן את כל המטען, מפענחת אם יש מפתח ומחזירה את המחרוזת.  
- `recv_bin(conn)` → `bytes`: קוראת כותרת ומטען, מפענחת אם צריך ומחזירה את הבתים הגולמיים.

---

### AESCipher (`src/srvr/aes_cipher.py`)

**תיאור**: מספקת מימוש AES במצב CBC לצורך הצפנה ופענוח של נתונים בערוץ מאובטח, כולל ריווח PKCS7, שימוש בוקטור אתחול אקראי וקידוד Base64 של תוצאת ההצפנה. כוללת גם יצירת מפתח סימטרי אקראי.

**משתנים עיקריים**  
- מחלקתיים: `KEY_RANDOM_BYTES` (גודל הקלט האקראי ליצירת מפתח), `NO_OVER` (קבוע המשמש להסרת ריווח).

**מתודות עיקריות**  
- `encrypt(key, raw)` → `bytes`: מרפדת את הבתים, מגרילה וקטור אתחול, מצפינה עם המפתח הנתון, ומחזירה את ה־IV והצופן כמחרוזת Base64.  
- `decrypt(key, enc)` → `bytes`: מבצעת decode ל־Base64, מפרידה את ה־IV, מפענחת את הצופן ומחזירה את התוכן לאחר הסרת ריווח.  
- `_pad(s)` → `bytes`: מוסיפה ריווח בסגנון PKCS7 כדי ליישר לאורך בלוק AES.  
- `_unpad(s)` → `bytes`: מסירה את הריווח מהתוכן המפוענח לפי הבייט האחרון.  
- `generate_key()` → `bytes`: יוצר בתים אקראיים באורך `KEY_RANDOM_BYTES`, מגבה אותם עם SHA‑256 ומחזיר מפתח באורך 32 בתים.

---

### DiffieHellman (`src/srvr/diffie_hellman.py`)

**תיאור**: עוטפת החלפת מפתחות ECDH על עקום SECP384R1, כולל יצירת מפתח פרטי וציבורי, סיריאליזציה של המפתח הציבורי וגזירת מפתח משותף בעזרת HKDF‑SHA256. משמשת הן בצד השרת והן בצד הלקוח.

**משתנים עיקריים**  
- מופעיים: `diffieHellman` (מפתח פרטי אליפטי), `public_key` (המפתח הציבורי התואם).

**מתודות עיקריות**  
- `__init__()` → `None`: יוצר מפתח פרטי חדש על העקום SECP384R1 ומפיק ממנו מפתח ציבורי.  
- `serialize_public_key()` → `bytes`: מסרללת את המפתח הציבורי לפורמט PEM (SubjectPublicKeyInfo).  
- `deserialize_public_key(data)` → public key: דסיריאליזציה של מפתח ציבורי מתוך נתוני PEM.  
- `get_key(public_key)` → `bytes`: מפעילה ECDH מול מפתח ציבורי של צד שני, ולאחר מכן HKDF‑SHA256 להפקת מפתח משותף באורך קבוע.

---

### KeyExchange (`src/srvr/key_exchange.py`)

**תיאור**: שכבת לוגיקה המשתמשת ב־`DiffieHellman` וב־`Protocol` כדי לבצע החלפת מפתחות מלאה בין שני צדדים, כולל שליחת וקבלת מפתחות ציבוריים וגזירת מפתח סימטרי משותף.

**משתנים עיקריים**  
- אין מצב פנימי; כל המתודות סטטיות.

**מתודות עיקריות**  
- `send_recv_key(conn)` → `bytes`: יוצר מופע `DiffieHellman`, שולח את המפתח הציבורי המקומי, מקבל את מפתח הצד השני ומחזיר את המפתח המשותף שנגזר.  
- `recv_send_key(conn)` → `bytes`: מקבל קודם את המפתח הציבורי מהלקוח, יוצר מפתח מקומי, שולח את המפתח הציבורי של השרת ומחזיר את המפתח המשותף.

---

### Methods (`src/srvr/methods.py`)

**תיאור**: שכבת ניתוב לוגית שממפה בקשות לקבוצות עיקריות (`USERS`,‏ `NOTEBOOKS`,‏ `USERS_NOTEBOOKS`) ומאצילה את הביצוע למחלקות ניהול מתאימות. מאפשרת לשרת הראשי להישאר כללי ואינו תלוי בפרטי המימוש של כל תחום.

**משתנים עיקריים**  
- מחלקתיים: `USER_MANAGER_CLASS_NAME`, `NOTEBOOK_MANAGER_CLASS_NAME`, `USER_NOTEBOOK_MANAGER_CLASS_NAME` (שמות מחלקה לשימוש עם `getattr`).

**מתודות עיקריות**  
- `USERS(request, params)` → `str`: מעבירה בקשה הקשורה למשתמשים למתודה המתאימה במחלקת `UserManager` ומחזירה את תשובתה.  
- `NOTEBOOKS(request, params)` → `str`: מעבירה בקשה הקשורה לתוכן מחברות ל־`NotebookManager`.  
- `USERS_NOTEBOOKS(request, params)` → `str`: מעבירה בקשות הקשורות לשיתוף והרשאות ל־`UserNotebookManager`.

---

### Hasha256 (`src/srvr/my_sha256.py`)

**תיאור**: מחלקת עזר סטטית לחישוב גיבובי SHA‑256 וייצוגם כמערך בתים או מחרוזת הקסה. משמשת בעיקר לגיבוב סיסמאות משתמשים וחלקים רגישים אחרים.

**משתנים עיקריים**  
- אין מצב פנימי; כל המתודות סטטיות.

**מתודות עיקריות**  
- `get_hash(st)` → `bytes`: מקבלת מחרוזת, מקודדת ל־UTF‑8 ומחזירה את הגיבוב הגולמי כבתים.  
- `get_hash_hex(st)` → `str`: מקבלת מחרוזת, מקודדת ל־UTF‑8 ומחזירה את הגיבוב כמחרוזת הקסה.

---

## מחלקות בצד הלקוח

### Client (`src/clnt/client.py`)

**תיאור**: מנהלת את חיבורי ה־TCP של הלקוח לשרת, כולל ערוץ הפקודות הראשי וערוץ עדכונים נפרד. מבצעת החלפת מפתחות לכל חיבור ומספקת מתודות נוחות לוולידציה ושליחת בקשות בפורמט הפרוטוקול, עם טיפול מיוחד ב־`check_updates`.

**משתנים עיקריים**  
- מופעיים: `my_socket` (שקע ראשי), `connection` (צמד `(socket, key)` לערוץ הראשי), `check_socket` (שקע עדכונים), `connection_check` (צמד לערוץ העדכונים).

**מתודות עיקריות**  
- `__init__()` → `None`: קוראת IP ופורט מהרישום, יוצרת שני שקעים, מתחברת לשרת, מבצעת החלפת מפתחות עבור כל ערוץ ושומרת את הצמדים; מסיימת את התהליך במקרה כישלון בהתחברות.  
- `handle_user_input()` → `None`: לולאת בדיקה אינטראקטיבית דרך קלט מהמשתמש, המאמתת בקשות ידניות, שולחת אותן ומדפיסה תגובות עד לקבלת `EXIT`/`QUIT`.  
- `valid_request(req_and_prms)` → `bool`: מתודה סטטית הבודקת האם סוג הבקשה ומספר הפרמטרים תואמים לפורמט המצופה.  
- `login_check(req_and_prms)` → `bool`: בודקת האם בקשת login תקינה, כולל סינון תווים חשודים לצמצום סיכון להזרקת SQL.  
- `signup_check(req_and_prms)` → `bool`: בודקת תקינות בקשת signup באותו אופן.  
- `funcs_check(req_and_prms)` → `bool`: בודקת בקשות הקשורות למחברות (add_stroke, delete_stroke, change_background, clear, add_page, check_updates) ומוודאת שהיא מכילה את מספר הפרמטרים הנכון.  
- `send_request_to_server(con, request)` → `None`: שולחת מחרוזת בקשה דרך מחלקת `Protocol` על גבי צמד החיבור הנתון.  
- `handle_server_response(con)` → `str`: קוראת ומחזירה את תגובת השרת מהחיבור הנתון.  
- `send_command(request)` → `str`: נקודת הגישה העיקרית לרכיבי ה־GUI; מפצלת את מחרוזת הבקשה, מאמתת אותה, ואז שולחת אותה לערוץ המתאים (עדכונים או ראשי) ומחזירה את תגובת השרת, או `"ILLEGAL REQUEST"` אם הפורמט לא חוקי.

---

### LoginWindow (`src/clnt/log_in.py`)

**תיאור**: חלון PyQt6 ראשוני המאפשר למשתמש להזין שם משתמש וסיסמה. מחזיק מופע `Client`, מפעיל בקשות התחברות, מציג שגיאות ופותח את `MainWindow` במקרה התחברות מוצלחת.

**משתנים עיקריים**  
- מופעיים: `client` (מופע משותף של `Client`), `username_line_edit`, `password_line_edit`, `error_label`, יחד עם וידג'טים ופריסות Qt נוספים.

**מתודות עיקריות**  
- `__init__()` → `None`: מגדירה כותרת וסגנון לחלון, קובעת גודל מינימלי, בונה את הווידג'טים המרכזיים ומאתחלת את הלקוח.  
- `create_central_widget()` → `None`: בונה את הווידג'ט המרכזי, פריסות אופקיות לשדות קלט, שורת שגיאה ופריסת כפתורים.  
- `create_central_layout(central_layout, username_layout, password_layout, button_layout, error_layout)` → `None`: מסדרת את הפריסות האנכיות עם מרווחים ו־stretch.  
- `create_layout(layout, name)` → `QtWidgets.QLineEdit`: מוסיפה תווית ושדה קלט לפריסה אופקית ומחזירה את שדה הקלט.  
- `create_error_layout(layout)` → `QLabel`: יוצרת תווית שגיאה ממורכזת ומחזירה אותה.  
- `create_button_layout(button_layout)` → `None`: מוסיפה כפתורי Login ו־Sign up לפריסת הכפתורים.  
- `create_button(name, func)` → `QPushButton`: בונה כפתור מעוצב המחובר לפונקציית callback מתאימה.  
- `login_button_clicked()` → `None`: קוראת את נתוני המשתמש, בונה בקשת login, שולחת אותה דרך `Client`, מציגה שגיאה במקרה כישלון או פותחת `MainWindow` ומסתירה את חלון ההתחברות במקרה הצלחה.  
- `signin_button_clicked()` → `None`: פותחת את חלון `SignupWindow` ומסתירה את חלון ההתחברות לצורך מעבר לזרימת הרשמה.

---

### SignupWindow (`src/clnt/sign_up.py`)

**תיאור**: חלון הרשמה ב־PyQt6 ליצירת משתמש חדש. מציג שדות שם משתמש, שם תצוגה וסיסמה, ופותח `MainWindow` במקרה הרשמה מוצלחת, תוך שמירה על קישור לחלון ההתחברות המקורי.

**משתנים עיקריים**  
- מופעיים: `username_line_edit`, `name_line_edit`, `password_line_edit`, `error_label`, `client` (מופע `Client` נפרד), `login` (הפניה ל־`LoginWindow` היוצר).

**מתודות עיקריות**  
- `__init__(login)` → `None`: בונה את הפריסה המרכזית עם שדות הקלט, שורת השגיאה וכפתור ההרשמה, מאתחלת את הלקוח ושומרת את ההפניה לחלון ההתחברות.  
- `create_central_layout(...)` → `None`: מגדירה מרווחים וסדר אנכי של שורות השדות והכפתור.  
- `create_layout(layout, name)` → `QtWidgets.QLineEdit`: יוצרת שורת תווית–שדה קלט ומחזירה את שדה הקלט.  
- `create_error_layout(layout)` → `QLabel`: יוצרת תווית שגיאה וכותבת אותה בפריסה.  
- `create_button_layout(button_layout)` → `None`: מוסיפה את כפתור Sign up ומחברת אותו למטפל.  
- `signup_button_clicked()` → `None`: בונה בקשת signup, שולחת אותה דרך `Client`, מציגה שגיאות ספציפיות (פרמטרים לא חוקיים/שם משתמש קיים) או פותחת `MainWindow` וסוגרת את חלון ההרשמה כשנוצר משתמש חדש.

---

### MainWindow (`src/clnt/main_window.py`)

**תיאור**: חלון היישום הראשי לאחר התחברות. מציג סרגל כלים עם שם המשתמש וכפתורי יציאה ורענון, כפתור להוספת מחברת, פריסת זרימה של מחברות ותיבה צפה ליצירת מחברת חדשה.

**משתנים עיקריים**  
- מופעיים: `login_window` (הפניה לחלון ההתחברות), `central_widget`, `layout` (פריסה אנכית ראשית), `main_toolbar`, `box` (מסגרת צפה ליצירת מחברת), `box_margin_right`, `box_margin_top`, `client`, `notebooks_layout` (`FlowLayout`), `id` (מזהה משתמש), `notebooks_dict` (מילון מחברת→כפתור), `names_perms` (מילון מחברת→הרשאה).

**מתודות עיקריות**  
- `__init__(client, id, login_window, name)` → `None`: בונה את החלון, סרגל הכלים, התיבה הצפה ופריסת המחברות, מאחסן את מזהה המשתמש וחלון ההתחברות, וטוענת את מחברות המשתמש.  
- `create_flow_layout()` → `None`: יוצר `FlowLayout` ומכניס אותו לווידג'ט עוטף ואל הפריסה הראשית.  
- `create_toolbar(name)` → `None`: בונה סרגל כלים עם תווית שם המשתמש, כפתורי יציאה ורענון וכפתור הוספת מחברת.  
- `create_add_button()` → `QPushButton`: יוצר כפתור עם אייקון פלוס לפתיחת/סגירת התיבה הצפה.  
- `create_log_out_button()` → `None`: מוסיף כפתור יציאה לסרגל ומחבר אותו ל־`log_out`.  
- `create_refresh_button()` → `None`: מוסיף כפתור רענון לסרגל ומחבר אותו ל־`refresh`.  
- `refresh()` → `None`: מנקה את פריסת המחברות וטוען מחדש את רשימת המחברות מהשרת.  
- `log_out()` → `None`: מנקה את שדות ההתחברות ב־`LoginWindow`, מציג אותו מחדש וסוגר את החלון הראשי.  
- `create_add_frame()` / `create_box()` / `create_button(line_edit)` → `None`/`QPushButton`: בונות את המסגרת הצפה (label + line edit + כפתור יצירה) וממקמות אותה בצד ימין–עליון.  
- `create_new_notebook_frame()` → `None`: מחליפה את נראות המסגרת הצפה ומעלה אותה קדימה כאשר מוצגת.  
- `create_new_notebook(id, notebook_name)` → `None`: יוצר אובייקט `Notebook` ריק, מסרלל אותו, שולח `add_notebook_to_db` לשרת, ובמקרה `"ok"` מוסיף כפתור מחברת חדש לפריסה.  
- `resizeEvent(event)` / `reposition_box()` → `None`: מתאימים את מיקום המסגרת הצפה בשינוי גודל החלון.  
- `create_notebook_button(name)` → `QPushButton`: יוצר כפתור בגודל קבוע המייצג מחברת.  
- `load_notebooks_for_user(user_id)` → `None`: שולח `clients_notebooks`, מפרש את התוצאה, יוצר כפתורים לכל מחברת ושומר הרשאות למילון.  
- `open_notebook(name)` → `None`: שולח `get_notebook` לשרת, בונה `NotebookArea` ומציג אותו, תוך הסתרת החלון הראשי.

---

### NotebookArea (`src/clnt/notebook_area.py`)

**תיאור**: חלון עבודה למחברת יחידה. מכיל את וידג'ט המחברת (`Notebook`), סרגל כלים ראשי, סרגלי משנה לכלי ציור, כפתורי ניווט בין עמודים, כפתורי ניקוי ושמירה, ודיאלוג ניהול הרשאות. מריץ חוט רקע הקורא `check_updates` ומחיל עדכונים חיים על המחברת.

**משתנים עיקריים**  
- מחלקתיים: `notebook_update_signal` (אות Qt שמעביר רשימת עדכונים ואינדקס עמוד).  
- מופעיים: `name` (שם המחברת), `notebook_widget` (מופע `Notebook`), `current_page`, `id` (מזהה משתמש), `client`, `main_window`, `running` (דגל לחוט העדכונים), `main_toolbar`, `sub_toolbars` (רשימת סרגלי משנה), `perm` (קוד הרשאה), `button_layout`, `scroll_area` ועוד הפניות לכלי UI שונים.

**מתודות עיקריות**  
- `__init__(mainwindow, id, client, notebook, name, perm)` → `None`: מאתחלת את החלון, יוצרת את הפריסה והסרגלים, בונה או יוצרת מחברת חדשה, מגדירה התנהגות לפי רמת ההרשאה, מריצה את חוט העדכונים ומחברת את האות לעדכון המחברת.  
- `loop()` → `None`: לולאת רקע ששולחת `check_updates` עם שם המחברת ו־`last_change`, מפרשת תגובות לא ריקות, ומעבירה את רשימת העדכונים דרך האות ל־UI.  
- `create_toolbars(central_layout, perm)` → `None`: בונה את הסרגל הראשי, סרגלי המשנה לכלי הציור, וקובע נראות בהתאם להרשאה (למשל הסתרה במצב צפייה בלבד).  
- `save_notebook()` / `clear_page(page_id)` / `change_background(type, page_id)` / `add_stroke(stroke, id_page, id)` / `add_page(id_page, page)` / `delete_stroke(id_page, id)` → `None` או `str`: שולחות בקשות מתאימות לשרת לשמירת מחברת, ניקוי עמודים, שינוי רקע, הוספת/מחיקת משיכות ועמודים.  
- `add_to_central_layout(central_layout, perm)` / `create_central_layout()` → פריסת המרכז ואזור הגלילה.  
- `show_sub_toolbar(index)` / `set_tool_and_size_and_color(i, toolbar)` / `tool_size_and_color(tool, size, color)` → `None`: מנהלות את הצגת סרגלי המשנה והגדרת כלי, צבע וגודל עבור העמוד הנוכחי.  
- `create_buttons(perm)` / `create_buttons_layout(perm)` / `create_sub_toolbars(...)` ועוד: בונות את כפתורי הניקוי, חזרה, ניווט ו־Access, ואת סרגלי הכלים לכלים השונים.  
- `clear_current_page()` / `back_current_page()` / `set_tool_for_current(tool_name)` / `no_tool_for_all()` / `set_size_for_current(size)` / `set_color_for_current(color)` / `set_background_for_current(background)` → `None`: מפעילות את הפעולות המתאימות על הקנבס הנוכחי (או על כל הקנבסים במצב צפייה בלבד).  
- `toolbar_features(toolbar)` / `main_toolbar_button(button, func)` / `create_page_buttons()` / `create_page_toolbar()` / `create_select_toolbar()` / `create_pen_toolbar_and_size_and_color()` / `create_marker_toolbar_and_size_and_color()` / `create_eraser_toolbar_and_size()` / `create_size_button(...)` / `create_color_button(colors)` → מתודות בנייה וסטיילינג של סרגלי הכלים והבקרים.  
- `closeEvent(event)` → `None`: מחזירה את חלון `MainWindow`, מפסיקה את חוט העדכונים ומקבלת את אירוע הסגירה.  
- `parse_users_access_response(resp)` → `list[tuple[str, int]]`: מפרשת תגובת `all_users` לרשימת זוגות (שם משתמש, קוד הרשאה).  
- `apply_access_changes(access_data)` → `None`: שולחת פקודות `change_access` לפי מילון רמות גישה שהתקבל מדיאלוג ההרשאות.  
- `open_access_dialog()` → `None`: פותחת את דיאלוג `AccessDialog` עם הרשאות נוכחיות, ומיישמת את השינויים שבחר המשתמש.  
- `reload_notebook(data, current_page)` → `None`: מחילה רשימת עדכונים על המחברת, מרעננת את העמודים, מחזירה את האינדקס המקורי ומבטיחה שמצב צפייה בלבד יישמר.

---

### Notebook (`src/clnt/notebook.py`)

**תיאור**: מעטפת בצד הלקוח המנהלת אוסף עמודי ציור כווידג'טים מוערמים (`QStackedWidget`). אחראית על יצירת עמודים, ניווט ביניהם, זום גלובלי והחלת עדכונים שמגיעים מהשרת לכל עמוד.

**משתנים עיקריים**  
- מופעיים: `notebook_area`, `pages` (מחסנית עמודים), `pages_list` (רשימת `DrawingCanvas`), `global_scale_factor`, `main_layout`, `last_change`.

**מתודות עיקריות**  
- `__init__(pages, last_change, notebook_area)` → `None`: בונה מחברת עם עמודים קיימים או יוצרת עמוד ראשון ריק, בונה את המחסנית ואת הפריסה, וקושרת חזרה אל `NotebookArea`.  
- `__dict__()` → `dict`: מסרללת את המחברת למבנה מילון הכולל `pages` ו־`last_change`, כאשר כל עמוד מסרלל באמצעות `__dict__` של הקנבס.  
- `current_canvas()` → `DrawingCanvas | None`: מחזירה את הקנבס של העמוד הנוכחי.  
- `add_page(page, notify_server=True)` → `None`: מוסיפה עמוד קיים או חדש למחסנית, מעתיקה פקטור זום מעמוד קודם, ומדווחת לשרת על עמוד חדש אם `notify_server` מוגדר.  
- `prev_page()` / `next_page()` → `None`: מנווטות לעמוד הקודם או הבא ומעדכנות את אינדקס העמוד ב־`NotebookArea`.  
- `zoom_in()` / `zoom_out()` → `None`: מגדילות או מקטינות את פקטור הזום הגלובלי ומחילות אותו על כל העמודים.  
- `apply_zoom_to_all()` → `None`: מעדכנת את גודל העמודים ומרעננת את התצוגה לפי פקטור הזום.  
- `update_notebook(ts, type, page, data)` → `None`: מחילה עדכון מהשרת – הוספת עמוד (`ADD_PAGE`) או קריאה למתודה המתאימה בקנבס של העמוד הרלוונטי (ADD_STROKE, DELETE_STROKE, CLEAR, CHANGE_BACKGROUND) ומעדכנת את `last_change`.  
- `delete_old_data()` → `None`: מסירה את כל הווידג'טים של העמודים מהמחסנית ומאפסת את הרשימה, לשימוש בעת טעינה מחדש של תוכן מחברת.

---

### DrawingCanvas (`src/clnt/canvas.py`)

**תיאור**: וידג'ט ציור מותאם אישית המאפשר ציור בעזרת עט או מדגיש, מחיקה, בחירה והזזה של משיכות, וזום בעזרת מחוות pinch וגלגלת. שומר שכבת רקע (ריק, שורות או משבצות) ומדווח על שינויים במשיכות לשרת דרך `NotebookArea`.

**משתנים עיקריים**  
- מופעיים: `background_layer` (Pixmap של רקע), `strokes` (רשימת `Stroke`), `current_stroke_points`, `current_stroke_times`, `selected_stroke`, `drawing`, `history`, `last_point`, `first_point`, `pen_color`, `pen_size`, `tool`, `page_type`, `is_gesturing`, `scale_factor`, `base_width`, `base_height`, `notebook_area`, `id` (מזהה עמוד), `stroke_id`.

**מתודות עיקריות**  
- `__init__(width, height, strokes, page_type, notebook_area, stroke_id, id)` → `None`: בונה את שכבת הרקע, משחזרת משיכות אם קיימות, מאתחלת היסטוריה, עט, רקע וזום, ושומרת הפניה ל־`NotebookArea` ולמזהים.  
- `_handle_eraser_click(pos)` → `None`: מאתרת את המשיכה הראשונה הכוללת את הנקודה `(pos)` לפי סף מחיקה, מסירה אותה מהרשימה ומדווחת ל־`NotebookArea` על מחיקת המשיכה מהשרת.  
- `__dict__()` → `dict`: מסרללת את מצב הקנבס (רוחב, גובה, משיכות, סוג עמוד, מזהה משיכה, מזהה עמוד) למילון.  
- `create_background_layer(width, height)` / `create_strokes_params(strokes)` / `create_history_params()` / `create_pen_params(page_type)` / `create_zoom_in_params(width, height)` → `None`: מתודות אתחול לבניית שכבת הרקע, רשימת המשיכות, ההיסטוריה, פרטי העט והזום.  
- `paintEvent(event)` / `draw_strokes(painter)` / `draw_background(painter)` / `draw_current_stroke(painter)` / `draw_stroke(stroke, painter)` → `None`: מציירות את הרקע, המשיכות ואת המשיכה המתבצעת כעת עם אנטי־אליאסינג ותמיכה בזום.  
- `mousePressEvent(event)` / `mouseMoveEvent(event)` / `mouseReleaseEvent(event)` → `None`: מטפלות באירועי עכבר – התחלת משיכה, הוספת נקודות, בחירה/הזזה של משיכה, מחיקה, וסיום משיכה תוך שליחת נתונים לשרת דרך `NotebookArea`.  
- `check_which_selected(pos)` / `create_pen(pen_size, pen_color)` / `move_selected_stroke(e, pos)` → `None`/`bool`: לוגיקת בחירה והזזה של משיכות.  
- `distance(point1, point2)` / `_are_last_points_close(...)` → `float`/`bool`: פונקציות עזר לזיהוי משיכות שניתן ליישר לקו ישר.  
- `add_new_stroke()` / `create_straight_line()` / `end_stroke()` → `Stroke | None`: בונות משיכה חדשה (ישרה או חופשית), מוסיפות אותה לרשימה ומחזירות את האובייקט.  
- `clear_canvas()` → `None`: מנקה את כל המשיכות ומדווח ל־`NotebookArea` לנקות את העמוד בשרת.  
- `draw_all_canvas()` → `QtGui.QPixmap`: מרנדרת את כל הרקע והמשיכות לתמונת Pixmap ומחזירה אותה.  
- `set_tool(tool_type)` / `change_pen_size(size)` / `change_pen_color(i)` / `back()` → `None`: קובעות את סוג הכלי, גודל וצבע, ומאפשרות ביטול המשיכה האחרונה תוך מחיקתה גם בצד השרת.  
- `zoom_in()` / `zoom_out()` / `_update_size()` → `None`: מנהלות את פקטור הזום והגודל הפיזי של הקנבס.  
- `event(event)` / `gesture_event(event)` / `handle_pinch(pinch)` → `bool`/`None`: מטפלות במחוות pinch לשינוי זום.  
- `blank()` / `lines()` / `_draw_grid_background()` / `grid()` → `None`: מגדירות ובונות רקע ריק, משורטט או מרובע.  
- `ADD_STROKE(data)` / `DELETE_STROKE(id)` / `CHANGE_BACKGROUND(data)` / `CLEAR(data)` → `None`: מחילות עדכוני שרת על הקנבס – הוספה/מחיקה של משיכה, שינוי רקע או ניקוי מלא.

---

### CanvasContainer (`src/clnt/canvas_container.py`)

**תיאור**: מעטפת גרפית שממרכזת את הקנבס בתוך פריסה אנכית ואופקית, עם מרווחי מתיחה, ומציירת רקע אחיד בצבע כחול בהיר מאחורי המחברת.

**משתנים עיקריים**  
- מופעיים: `child_widget` (הווידג'ט העוטף את המחברת), יחד עם פריסות אנכיות ואופקיות.

**מתודות עיקריות**  
- `__init__(child_widget)` → `None`: בונה פריסה אנכית עם פריסת משנה אופקית, מוסיפה מתיחות משני הצדדים וממרכזת את הווידג'ט הילד.  
- `paintEvent(event)` → `None`: ממלאת את מלבן הווידג'ט בצבע רקע קבוע.

---

### CenteredScrollArea (`src/clnt/scroll_area.py`)

**תיאור**: אזור גלילה מותאם עבור וידג'ט המחברת; מרכז את המחברת בתוך וידג'ט פנימי ותומך בזום עם Ctrl+גלגלת על ידי קריאה ל־`zoom_in`/`zoom_out` של המחברת.

**משתנים עיקריים**  
- מופעיים: `notebook` (הווידג'ט של המחברת), וידג'ט מרכזי ופריסה אנכית פנימית.

**מתודות עיקריות**  
- `__init__(notebook_widget)` → `None`: קובע שהתוכן ניתן לשינוי גודל, יוצר וידג'ט מרכזי עם פריסה ממורכזת ומכניס אליו את המחברת.  
- `wheelEvent(event)` → `None`: אם מקש Ctrl לחוץ – מפעיל זום פנימה/החוצה פי כיוון הגלגלת על המחברת; אחרת מעביר את האירוע למימוש ברירת המחדל.

---

### Stroke (`src/clnt/stroke.py`)

**תיאור**: מייצגת משיכת קו בודדת כאוסף נקודות עם זמני דגימה, צבע עט, רוחב עט, דגל בחירה ומזהה. מספקת לוגיקת בדיקת פגיעה לנקודה וסריאליזציה למבנה מילון.

**משתנים עיקריים**  
- מופעיים: `points` (רשימת `QPoint`), `times` (רשימת חותמות זמן), `pen_color` (`QColor`), `pen_size` (רוחב קו), `selected` (דגל בחירה), `id` (מזהה מספרי).

**מתודות עיקריות**  
- `__init__(points, times, pen_color, pen_size, id)` → `None`: ממיר את רשימת הנקודות לאובייקטי `QPoint` במידת הצורך, שומר את זמני הדגימה, את צבע העט, רוחב הקו ומזהה המשיכה, ומאתחל את דגל הבחירה כ־False.  
- `contains_point(pt, tolerance)` → `bool`: עובר על כל מקטעי המשיכה, מחשב את המרחק המינימלי מהנקודה למקטע ומחזיר `True` אם המרחק קטן מסף נתון.  
- `point_line_distance(p, a, b)` → `float`: מתודת עזר סטטית לחישוב מרחק מנקודה למקטע קו.  
- `__dict__()` → `dict`: מסרללת את המשיכה למילון הכולל נקודות כזוגות `(x, y)`, זמני דגימה, צבע כהקסה, רוחב ומזהה.

---

### AccessDialog (`src/clnt/access.py`)

**תיאור**: דיאלוג מודאלי לניהול רמות גישה למשתמשים עבור מחברת מסוימת. בונה שורה לכל משתמש עם תווית שם ומשבצת בחירה לרמת גישה, ומאפשר להחזיר מפה מעודכנת של רמות הגישה.

**משתנים עיקריים**  
- מופעיים: `access_levels` (רשימת מחרוזות רמות הגישה), `user_boxes` (מילון שם משתמש→`QComboBox`).

**מתודות עיקריות**  
- `__init__(users_with_access, parent=None)` → `None`: בונה את ה־UI של הדיאלוג, יוצרת שורה עבור כל משתמש ורמת הגישה הנוכחית שלו, מוסיפה כפתורי שמירה וביטול ומאתחלת את המילון `user_boxes`.  
- `get_access_data()` → `dict[str, str]`: מחזירה מילון שממפה שם משתמש לרמת הגישה שנבחרה כטקסט (למשל `"Admin"`, `"Edit"`).

---

### FlowLayout (`src/clnt/flow_layout.py`)

**תיאור**: מימוש מותאם של `QLayout` שמסדר וידג'טים בפריסה זורמת: משמאל לימין עד הקצה, ואז עובר לשורה חדשה. משמש להצגת כפתורי מחברות במסך הראשי תוך התאמת הפריסה לרוחב החלון.

**משתנים עיקריים**  
- מופעיים: `itemList` (רשימת פריטי פריסה המייצגת את הילדים).

**מתודות עיקריות**  
- `__init__(parent=None)` → `None`: מאתחלת פריסה ללא פריטים, עם מרווחי ברירת מחדל וריווח קבוע.  
- `addItem(item)` → `None`: מוסיפה פריט פריסה לרשימה.  
- `count()` → `int`: מחזירה את מספר הפריטים.  
- `itemAt(index)` / `takeAt(index)` → `QLayoutItem | None`: מחזירות או מסירות פריט לפי אינדקס.  
- `expandingDirections()` → `Qt.Orientation`: מציינת שהפריסה אינה מתרחבת באופן עצמאי.  
- `hasHeightForWidth()` / `heightForWidth(width)` → `bool`/`int`: מציינות שהגובה תלוי ברוחב ומחשבות את הגובה הנדרש לרוחב נתון.  
- `setGeometry(rect)` → `None`: מציבה בפועל את כל הפריטים בתוך המלבן הנתון.  
- `sizeHint()` / `minimumSize()` → `QSize`: מחשבות גדלי המלצה ומינימום בהתאם לפריטים.  
- `do_layout(rect, test_only)` / `process_item(...)` → `int`/`tuple[int, int, int]`: מממשות את ליבת חישוב המיקום והמעבר לשורה חדשה.  
- `clear(delete_widgets=True)` / `reset_items(new_widgets=None)` → `None`: מנקות את כל הפריטים, ובמידת הצורך גם מוחקות את הווידג'טים או מוסיפות אוסף חדש.

---

### ToolbarsEnum (`src/clnt/style.py`)

**תיאור**: `Enum` שמגדיר אינדקסים לסרגלי הכלים השונים של הציור (עמוד, עט, מדגיש, מחק, בחירה). מאפשר לוגיקה ברורה ב־`NotebookArea` בבחירת סרגל המשנה המתאים.

**משתנים עיקריים**  
- חברי enum: `PAGE`, `PEN`, `MARKER`, `ERASER`, `SELECT` (כל אחד ממופה לערך מספרי).

**מתודות עיקריות**  
- משתמש במתודות ברירת המחדל של `Enum` ללא הרחבות מיוחדות.

---

### Reg (`src/clnt/winreg_file.py`)

**תיאור**: מעטפת סביב רישום Windows שקוראת את כתובת ה־IP והפורט של השרת ממפתח ייעודי. משמשת את הלקוח בעת ההפעלה כדי למצוא את השרת ללא תלות בקידוד כתובת בקוד.

**משתנים עיקריים**  
- מחלקתיים/מודוליים: מסתמכת על `VALUES_COUNT` ועל הקבועים `IP`, `PORT` המיובאים.

**מתודות עיקריות**  
- `read_reg()` → `tuple[str, int]`: פותחת את המפתח `HKEY_LOCAL_MACHINE\SOFTWARE\Technition Server`, עוברת על הערכים, מעדכנת את ה־IP ואת הפורט אם נמצאו ערכים מתאימים, מדפיסה מידע לצורך דיבוג ומחזירה `(ip, port)`.

---

### Protocol (`src/clnt/protocol.py`)

**תיאור**: מימוש צד לקוח של פרוטוקול ההודעות מבוסס כותרת אורך. מתנהג זהה למימוש בצד השרת, כך שניתן להשתמש באותה לוגיקה של החלפת מפתחות ותקשורת בשני הצדדים.

**משתנים עיקריים**  
- מחלקתיים: `STOP_RECV`, `KEY`, `SOCK` (כמו בצד השרת).

**מתודות עיקריות**  
- `send(conn, data)` / `send_bin(conn, data_bit)` → `None`: שולחות מחרוזת או בתים עם כותרת אורך והצפנה אופציונלית.  
- `recv(conn)` → `str` / `recv_bin(conn)` → `bytes`: קוראות הודעה שלמה, מפענחות אם יש מפתח ומחזירות מחרוזת או בתים גולמיים.

---

### KeyExchange (`src/clnt/key_exchange.py`)

**תיאור**: צד לקוח של תהליך החלפת המפתחות, זהה מבחינת הממשק לגרסת השרת, אך משתמש במודול `protocol` בצד הלקוח. עוטף את זרימות השליחה–קבלה והקבלה–שליחה של מפתחות ECDH.

**משתנים עיקריים**  
- אין מצב פנימי; המתודות סטטיות.

**מתודות עיקריות**  
- `send_recv_key(conn)` / `recv_send_key(conn)` → `bytes`: מממשות את שני מסלולי ההחלפה – שליחת מפתח ציבורי מקומי, קבלת מפתח ציבורי מהשרת, וגזירת מפתח משותף.

---

### AESCipher (`src/clnt/aes_cipher.py`)

**תיאור**: מימוש AES בצד הלקוח, זהה לגרסת השרת, המשמש להצפנת ערוץ התקשורת ויצירת מפתח סימטרי. מטפל בריווח/הסרת ריווח ובקידוד Base64.

**משתנים עיקריים**  
- מחלקתיים: `KEY_RANDOM_BYTES`, `NO_OVER`.

**מתודות עיקריות**  
- `encrypt(key, raw)` / `decrypt(key, enc)` → `bytes`: מצפינות ומפענחות בתים ומחזירות את התוצאה המפוענחת או המקודדת.  
- `_pad(s)` / `_unpad(s)` → `bytes`: תומכות בלוגיקת הריווח.  
- `generate_key()` → `bytes`: יוצרות מפתח סימטרי אקראי מגובה ב־SHA‑256.

---

### DiffieHellman (`src/clnt/diffie_hellman.py`)

**תיאור**: מימוש ECDH בצד הלקוח, זהה לגרסת השרת, עבור יצירת מפתחות משותפים מול השרת או צדדים אחרים.

**משתנים עיקריים**  
- מופעיים: `diffieHellman`, `public_key`.

**מתודות עיקריות**  
- `__init__()` → `None`, `serialize_public_key()` → `bytes`, `deserialize_public_key(data)` → public key, `get_key(public_key)` → `bytes`: זהות למתודות בגרסת השרת.

---

### Hasha256 (`src/clnt/my_sha256.py`)

**תיאור**: כלי עזר סטטי ל־SHA‑256 בצד הלקוח, זהה לגרסת השרת, לשימוש בבדיקות ובחישובי גיבוב מקומיים.

**משתנים עיקריים**  
- אין מצב פנימי.

**מתודות עיקריות**  
- `get_hash(st)` → `bytes`, `get_hash_hex(st)` → `str`: מחזירות את הגיבוב כבתים או כמחרוזת הקסה עבור מחרוזת נתונה.

