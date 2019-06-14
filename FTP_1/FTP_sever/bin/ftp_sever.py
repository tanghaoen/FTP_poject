import os, sys

Path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Path)
from core import main



if __name__ == '__main__':
    main.Argvhandler()
