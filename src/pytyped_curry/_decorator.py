from contextlib import contextmanager
from typing import Any

from ._doc import contexts

@contextmanager
def decorator(**kwargs: Any) -> None:
    contexts.append(kwargs)
    try:
        yield
    finally:
        del contexts[-1]
