import os

def left_right_print(left: str, right:str, same_line: bool=True):
    width: int = int(os.popen('stty size', 'r').read().split()[1])
    left_max: int = int(width * 4/5)
    left: str = (left[:left_max - 3] + '...') if len(left) > left_max else left
    right_adjust: int = width - left_max - 4
    line: str = '{}{}'.format(left.ljust(left_max), right.rjust(right_adjust))
    if same_line:
        print(line, end='\r')
    else:
        print(line, end='\n')
