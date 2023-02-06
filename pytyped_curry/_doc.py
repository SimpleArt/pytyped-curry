from collections.abc import Callable
from contextlib import redirect_stdout
from functools import partial
from io import StringIO
from typing import Any


class Curry:
    """Helper function for currying functions with documentation."""
    n: int

    def __init__(self, *args: type[partial]) -> None:
        self.n = len(args)

    def __call__(
        self, func: Callable[..., Any], /, *args: Any, **kwargs: Any
    ) -> Callable[..., Any]:
        result = Curried(self.n, func, *args, **kwargs)
        if hasattr(func, "__annotations__"):
            result.__annotations__ = func.__annotations__
        result.__doc__ = getattr(func, "__doc__", None)
        if hasattr(func, "__module__"):
            result.__module__ = func.__module__
        if hasattr(func, "__name__"):
            result.__name__ = func.__name__
        if hasattr(func, "__qualname__"):
            result.__qualname__ = func.__qualname__
        result.__wrapped__ = func
        return result


class Curried:
    """
    Helper class for providing a `__repr__` that appears cleanly in
    `help(...)`.
    """
    n: int
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __init__(self, n: int, *args: Any, **kwargs: Any) -> None:
        self.n = n
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.n == 1:
            return partial(*[partial] * self.n)(
                *self.args, **self.kwargs
            )(*args, **kwargs)
        result = type(self)(self.n - 1, *self.args, *args, **self.kwargs, **kwargs)
        if "__annotations__" in vars(self):
            result.__annotations__ = self.__annotations__
        result.__doc__ = self.__doc__
        if "__module__" in vars(self):
            result.__module__ = self.__module__
        if "__name__" in vars(self):
            result.__name__ = self.__name__
        if "__qualname__" in vars(self):
            result.__qualname__ = self.__qualname__
        if "__wrapped__" in vars(self):
            result.__wrapped__ = self.__wrapped__
        if (
            len(self.args) + len(self.kwargs) + len(args) + len(kwargs) == 1
            or "__name__" not in vars(self)
                and "__qualname__" not in vars(self)
        ):
            return result
        elif len(self.args) + len(args) > 1:
            params = ", ".join([
                f"{arg!r}"
                for a in (self.args[1:], args)
                for arg in a
            ])
            if self.kwargs or kwargs:
                params += "".join([
                    f", {key!r}={value!r}"
                    for k in (self.kwargs, kwargs)
                    for key, value in k.items()
                ])
        else:
            params = ", ".join([
                f"{key!r}={value!r}"
                for k in (self.kwargs, kwargs)
                for key, value in k.items()
            ])
        params = f"({params})"
        if "__name__" in vars(self):
            result.__name__ += params
        if "__qualname__" in vars(self):
            result.__qualname__ += params
        return result

    def __repr__(self) -> str:
        args = iter(self.args)
        with redirect_stdout(StringIO()) as doc:
            help(next(args))
        signature = doc.getvalue().splitlines()[2]
        if len(self.args) > 1:
            signature += "".join([f", {arg!r}" for arg in args])
        if len(self.kwargs) > 1:
            signature += "".join([
                f", {key!r}={value!r}"
                for key, value in self.kwargs.items()
            ])
        return f"curry({self.n})({signature})"
