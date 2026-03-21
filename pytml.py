import sys
from pathlib import Path
import subprocess


def error(message: str, status_code: int = 1) -> None:
    print(f"Error: {message}")
    sys.exit(status_code)


def info(message: str) -> None:
    print(f"Info: {message}")


def install_module(name: str) -> None:
    try:
        __import__(name)
    except ImportError:
        info(f"Package '{name}' not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", name], check=True
            )
            info(f"Module '{name}' installed successfully.")
        except subprocess.CalledProcessError as e:
            error(f"Failed to install module '{name}'. Error: {e}")


install_module("markdown")
import markdown # noqa: E402
from markdown.extensions.codehilite import CodeHiliteExtension # noqa: E402
from markdown.extensions.fenced_code import FencedCodeExtension # noqa: E402

install_module("typelate")
from typelate import Template # noqa: E402

install_module("webbrowser")
import webbrowser # noqa: E402

# install_module("pygments")
# import pygments # noqa: E402

PYTHON_SUFFIX = ".py"
DEFUALT_THEME = """
.codehilite .hll { background-color: #ffffcc }
.codehilite  { background: #f8f8f8; }
.codehilite .c { color: #408080; font-style: italic } /* Comment */
.codehilite .err { border: 1px solid #FF0000 } /* Error */
.codehilite .k { color: #008000; font-weight: bold } /* Keyword */
.codehilite .o { color: #666666 } /* Operator */
.codehilite .ch { color: #408080; font-style: italic } /* Comment.Hashbang */
.codehilite .cm { color: #408080; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #BC7A00 } /* Comment.Preproc */
.codehilite .cpf { color: #408080; font-style: italic } /* Comment.PreprocFile */
.codehilite .c1 { color: #408080; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #408080; font-style: italic } /* Comment.Special */
.codehilite .gd { color: #A00000 } /* Generic.Deleted */
.codehilite .ge { font-style: italic } /* Generic.Emph */
.codehilite .gr { color: #FF0000 } /* Generic.Error */
.codehilite .gh { color: #000080; font-weight: bold } /* Generic.Heading */
.codehilite .gi { color: #00A000 } /* Generic.Inserted */
.codehilite .go { color: #888888 } /* Generic.Output */
.codehilite .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
.codehilite .gs { font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.codehilite .gt { color: #0044DD } /* Generic.Traceback */
.codehilite .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
.codehilite .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
.codehilite .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
.codehilite .kp { color: #008000 } /* Keyword.Pseudo */
.codehilite .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
.codehilite .kt { color: #B00040 } /* Keyword.Type */
.codehilite .m { color: #666666 } /* Literal.Number */
.codehilite .s { color: #BA2121 } /* Literal.String */
.codehilite .na { color: #7D9029 } /* Name.Attribute */
.codehilite .nb { color: #008000 } /* Name.Builtin */
.codehilite .nc { color: #0000FF; font-weight: bold } /* Name.Class */
.codehilite .no { color: #880000 } /* Name.Constant */
.codehilite .nd { color: #AA22FF } /* Name.Decorator */
.codehilite .ni { color: #999999; font-weight: bold } /* Name.Entity */
.codehilite .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
.codehilite .nf { color: #0000FF } /* Name.Function */
.codehilite .nl { color: #A0A000 } /* Name.Label */
.codehilite .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
.codehilite .nt { color: #008000; font-weight: bold } /* Name.Tag */
.codehilite .nv { color: #19177C } /* Name.Variable */
.codehilite .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
.codehilite .w { color: #bbbbbb } /* Text.Whitespace */
.codehilite .mb { color: #666666 } /* Literal.Number.Bin */
.codehilite .mf { color: #666666 } /* Literal.Number.Float */
.codehilite .mh { color: #666666 } /* Literal.Number.Hex */
.codehilite .mi { color: #666666 } /* Literal.Number.Integer */
.codehilite .mo { color: #666666 } /* Literal.Number.Oct */
.codehilite .sa { color: #BA2121 } /* Literal.String.Affix */
.codehilite .sb { color: #BA2121 } /* Literal.String.Backtick */
.codehilite .sc { color: #BA2121 } /* Literal.String.Char */
.codehilite .dl { color: #BA2121 } /* Literal.String.Delimiter */
.codehilite .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
.codehilite .s2 { color: #BA2121 } /* Literal.String.Double */
.codehilite .se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
.codehilite .sh { color: #BA2121 } /* Literal.String.Heredoc */
.codehilite .si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
.codehilite .sx { color: #008000 } /* Literal.String.Other */
.codehilite .sr { color: #BB6688 } /* Literal.String.Regex */
.codehilite .s1 { color: #BA2121 } /* Literal.String.Single */
.codehilite .ss { color: #19177C } /* Literal.String.Symbol */
.codehilite .bp { color: #008000 } /* Name.Builtin.Pseudo */
.codehilite .fm { color: #0000FF } /* Name.Function.Magic */
.codehilite .vc { color: #19177C } /* Name.Variable.Class */
.codehilite .vg { color: #19177C } /* Name.Variable.Global */
.codehilite .vi { color: #19177C } /* Name.Variable.Instance */
.codehilite .vm { color: #19177C } /* Name.Variable.Magic */
.codehilite .il { color: #666666 } /* Literal.Number.Integer.Long */
"""
HEADING_TEMPLATE = Template("<h2><code>{title: Path}</code></h2>")
MARKDOWN_TEMPLATE = Template("```python\n{code: str}\n```")
FILE_URL_TEMPLATE = Template("file://{path: Path}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python pytml.py <src>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        error(f"Invalid path, '{path}' does not exist")

    info(f"Found '{path}' path")
    html = f"<style>{DEFUALT_THEME}</style>"
    count = 0

    if path.is_dir():
        for file in path.glob(f"**/*{PYTHON_SUFFIX}"):
            html += parse(file)
            count += 1
    else:
        if path.suffix == PYTHON_SUFFIX:
            error("Path must be a python file or a folder.")
        html += parse(path)
        count += 1

    out = "output.html"

    with open("output.html", mode="w", encoding="utf-8") as file:
        file.write(html)

    out = Path(out).absolute()
    webbrowser.open(FILE_URL_TEMPLATE(path=out))
    info(f"Conversion completed ({count} files)")


def parse(path: Path, line_numbers: bool = True) -> str:
    info(f"Parsing {path}")
    code = path.read_text(encoding="utf-8")
    html = markdown.markdown(
        MARKDOWN_TEMPLATE(code=code),
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(linenums=line_numbers, use_pygments=True),
        ],
    )
    return HEADING_TEMPLATE(title=path) + html


if __name__ == "__main__":
    main()
