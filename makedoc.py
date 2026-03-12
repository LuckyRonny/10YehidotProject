import ast, os, re, json, pathlib, textwrap
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

base='/mnt/data'
pyfiles=[os.path.join(base,f) for f in os.listdir(base) if f.endswith('.py')]

def extract_classes(file):
    src=open(file,'r',encoding='utf-8').read()
    tree=ast.parse(src)
    classes=[]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            info={'file':os.path.basename(file),'name':node.name,'bases':[ast.unparse(b) for b in node.bases],'methods':[]}
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef):
                    info['methods'].append({
                        'name':stmt.name,
                        'args':[a.arg for a in stmt.args.args],
                        'doc':ast.get_docstring(stmt)
                    })
            classes.append(info)
    return classes

all_classes=[]
for f in pyfiles:
    all_classes.extend(extract_classes(f))
classes_by_name={c['name']:c for c in all_classes}

class_roles = {
    'AESCipher': 'ביצוע הצפנה ופענוח של מטענים בינאריים בתקשורת המאובטחת בין הלקוח לשרת באמצעות AES במצב CBC.',
    'AccessDialog': 'הצגת חלון ניהול הרשאות למשתמשים במחברת, ובחירת רמת הגישה של כל משתמש.',
    'DrawingCanvas': 'ניהול דף ציור יחיד במחברת: ציור, מחיקה, בחירה, הזזה, זום, רקע שורות/רשת וסנכרון שינויים מול רכיב המחברת.',
    'CanvasContainer': 'עטיפת רכיב ציור בתוך מיכל ממורכז עם רקע גרפי אחיד.',
    'Client': 'ניהול התקשורת של צד הלקוח עם השרת, כולל פתיחת חיבורים, החלפת מפתחות, שליחת פקודות וקבלת תגובות.',
    'DiffieHellman': 'יצירת והחלפת מפתחות באמצעות ECDH לצורך הפקת מפתח משותף מוצפן לתקשורת.',
    'LoginWindow': 'הצגת חלון ההתחברות הראשי, קבלת פרטי משתמש ופתיחת חלון העבודה לאחר אימות.',
    'FlowLayout': 'מימוש פריסת Flow מותאמת אישית המסדרת ווידג׳טים בשורות עם גלישה אוטומטית.',
    'KeyExchange': 'ביצוע פרוטוקול החלפת המפתחות מעל אובייקט חיבור, באמצעות מחלקת DiffieHellman ופרוטוקול ההעברה.',
    'Hasha256': 'חישוב גיבובי SHA-256 במבנה בינארי או טקסטואלי.',
    'MainWindow': 'ניהול חלון הבית של המשתמש לאחר ההתחברות, כולל טעינת מחברות, פתיחת מחברת ויצירת מחברת חדשה.',
    'Notebook': 'ייצוג מחברת אחת המורכבת ממספר דפי ציור, כולל ניווט בין דפים, זום וסנכרון עדכונים.',
    'Protocol': 'מימוש פרוטוקול התקשורת האפליקטיבי: מסגור הודעות לפי אורך, שליחה וקבלה של טקסט או בתים, עם הצפנה אופציונלית.',
    'NotebookArea': 'ניהול חלון העריכה של מחברת בודדת, כולל סרגלי כלים, פעולות על הדף, סנכרון בזמן אמת והרשאות גישה.',
    'SignupWindow': 'הצגת חלון ההרשמה, שליחת בקשת יצירת משתמש חדש ופתיחת חלון הבית לאחר הצלחה.',
    'Stroke': 'ייצוג לוגי של קו/משיכת עט בודדת, כולל נקודות, זמני ציור, צבע, עובי ובדיקת פגיעה.',
    'CenteredScrollArea': 'הצגת המחברת בתוך אזור גלילה ממורכז עם תמיכה בזום באמצעות Ctrl + גלגלת.',
    'ToolbarsEnum': 'הגדרת מזהים קבועים עבור סוגי סרגלי הכלים בחלון העריכה.',
    'Reg': 'קריאת פרטי חיבור לשרת מתוך Windows Registry, עם ערכי ברירת מחדל מהקבועים.',
}

selected_attrs = {
    'AESCipher': [('אין מאפייני מופע', 'המחלקה ממומשת באמצעות פעולות סטטיות בלבד.')],
    'AccessDialog': [('access_levels','רשימת רמות ההרשאה שניתן לבחור עבור כל משתמש.'),
                     ('user_boxes','מילון הממפה בין שם משתמש לבין תיבת הבחירה של רמת ההרשאה שלו.')],
    'DrawingCanvas': [('background_layer','שכבת הרקע שעליה מצויר הדף והמבנה הגרפי שלו.'),
                      ('strokes','רשימת הקווים הקיימים בדף.'),
                      ('history','היסטוריית קווים שניתן להשתמש בה לצורך פעולת חזרה.'),
                      ('current_stroke_points','אוסף הנקודות של הקו הנוכחי בזמן הציור.'),
                      ('current_stroke_times','זמני הדגימה של נקודות הקו הנוכחי.'),
                      ('selected_stroke','הקו שנבחר כרגע לצורך הזזה או סימון.'),
                      ('tool','שם הכלי הפעיל: עט, מרקר, מחק, בחירה וכדומה.'),
                      ('pen_color','צבע כלי הכתיבה הפעיל.'),
                      ('pen_size','עובי כלי הכתיבה הפעיל.'),
                      ('page_type','סוג הרקע של הדף: חלק, שורות או רשת.'),
                      ('scale_factor','מקדם הזום המקומי של הדף.'),
                      ('notebook_area','הפניה לחלון המחברת שמנהל את הקנבס.'),
                      ('stroke_id','מונה/מזהה לקווים חדשים בדף.'),
                      ('id','מזהה ייחודי של הדף בתוך המחברת.')],
    'CanvasContainer': [('child_widget','הווידג׳ט המוכל שאותו המיכל מציג וממרכז.')],
    'Client': [('my_socket','שקע התקשורת הראשי של הלקוח.'),
               ('check_socket','שקע ייעודי לבדיקת עדכונים שוטפים מהשרת.'),
               ('connection','טפל חיבור ראשי הכולל Socket ומפתח הצפנה.'),
               ('connection_check','טפל חיבור לבדיקות עדכון הכולל Socket ומפתח הצפנה.')],
    'DiffieHellman': [('diffieHellman','המפתח הפרטי/אובייקט ההחלפה שבו משתמשים ליצירת סוד משותף.'),
                      ('public_key','המפתח הציבורי שנגזר מהמפתח הפרטי ונשלח לצד השני.')],
    'LoginWindow': [('username_line_edit','שדה קלט לשם המשתמש.'),
                    ('password_line_edit','שדה קלט לסיסמה.'),
                    ('error_label','תווית להצגת שגיאות למשתמש.'),
                    ('client','מופע של מחלקת Client לביצוע פניות לשרת.'),
                    ('signup_window','חלון ההרשמה שמוצג מתוך חלון ההתחברות.'),
                    ('main_window','חלון הבית שנ')
                    ]
}