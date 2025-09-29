"""
ronny getz and hilit shahar
secret massage
"""

CESAR = 3


def main():
    """decode the secret massage"""
    s = ""
    code = "khoor#p|#qdph#lv#lqljr#prqwr|d"
    for i in code:
        o = ord(i)
        s += chr(o-CESAR)
    print(s)


if __name__ == "__main__":
    main()
