import json

with open("C:\\Users\97258\PycharmProjects\\10YehidotProject\src\srvr\\notebook_DB.json", "r") as f:
    notebook = json.load(f)
    notebook["abc"] = 1
with open("C:\\Users\97258\PycharmProjects\\10YehidotProject\src\srvr\\notebook_DB.json", "w") as f:
    json.dump(notebook, f)

with open("C:\\Users\97258\PycharmProjects\\10YehidotProject\src\srvr\\notebook_DB.json", "r") as f:
    notebook = json.load(f)
    notebook1 = notebook["abc"]
print(notebook)
print(notebook1)
