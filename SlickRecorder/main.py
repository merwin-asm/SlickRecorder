import os
def current_path():
    x = os.path.abspath(__file__).split('/')
    x.pop()
    return "/".join(x)

def main():
    os.system(f"python3 {current_path()}/gui.py")
if __name__ == "__main__":
    main()

