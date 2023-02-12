import sys

if sys.version_info < (3, 9):
    __all__ = ["curry"]
else:
    __all__ = ["curry", "decorator"]
    from ._decorator import decorator

if sys.version_info < (3, 8):
    from ._curry_3_7 import curry
elif sys.version_info < (3, 11):
    from ._curry_3_8 import curry
else:
    from ._curry_3_11 import curry
