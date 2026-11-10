"""Compare regenerated exact results, allowing only tiny display-rounding drift."""
import json
import math
from pathlib import Path
import sys


def compare(left, right, path='root'):
    if isinstance(left, dict):
        if left.keys() != right.keys():
            raise ValueError('changed result fields at ' + path)
        for key in left:
            compare(left[key], right[key], path + '.' + key)
    elif isinstance(left, list):
        if len(left) != len(right):
            raise ValueError('changed result length at ' + path)
        for i, (a, b) in enumerate(zip(left, right)):
            compare(a, b, path + '[' + str(i) + ']')
    elif isinstance(left, float):
        if not isinstance(right, (int, float)) or not math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-10):
            raise ValueError('changed numerical display at ' + path)
    elif left != right:
        raise ValueError('changed exact result at ' + path)


if __name__ == '__main__':
    compare(json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text()))
    print('All exact results match; floating displays agree within 1e-10.')
