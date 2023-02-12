import pydoc
import sys
from collections.abc import Callable
from dataclasses import dataclass
from types import FunctionType, MethodType
from typing import Any

if sys.version_info < (3, 9):
    from typing import Dict, List
else:
    from builtins import dict as Dict, list as List

contexts: List[Dict[str, Any]] = []


@dataclass(unsafe_hash=True, frozen=True)
class curry:
    '''
    Functional tool for currying a function. Currying a function makes
    the function callable multiple times before the function is actually
    ran. Use `curry(n)(func)` or `@curry(n)` to transform a function into
    a curried function which takes `n` calls before running.

    Example
    -------
        >>> # Transform the function into a curried function that takes
        >>> # two function calls before running.
        >>> @curry(2)
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        ... 
        >>> # Add needs to be called twice to be ran.
        >>> add(2)(3)
        5
        >>> # Partial evaluation is easy.
        >>> increment = add(1)
        >>> increment(5)
        6
        >>> # The two arguments accept multiple forms.
        >>> add(x=2)(y=3)
        5
        >>> add(y=3)(x=2)
        5
        >>> add(2, 3)()
        5
        >>> add()(2, 3)
        5
    
    For Decorators
    --------------
    Often times writing decorators requires writing several nested functions.
    This is often a hassle, and in many cases completely unnecessary due to
    currying.

    Note: `reveal_type` is ran using `mypy`.
    
        >>> T = typing.TypeVar("T")
        >>> RT = typing.TypeVar("RT")
        >>> 
        >>> @curry(2, ...)
        ... def decorator(func: Callable[[T], RT], x: T) -> RT:
        ...     print("Start")
        ...     y = func(x)
        ...     print("Finished")
        ...     return y
        ... 
        >>> reveal_type(decorator)
        def (def (T`-1) -> RT`-2) -> def (T`-1) -> RT`-2
        >>> 
        >>> @decorator
        >>> def increment(x: int) -> int:
        ...     return x + 1
        ... 
        >>> reveal_type(increment)
        def (builtins.int) -> builtins.int
        >>> 
        >>> @curry(3, ...)
        ... def rate_limit(timeout: float, func: Callable[[T], RT], x: T) -> RT:
        ...     time.sleep(timeout)
        ...     return func(x)
        ... 
        >>> reveal_type(rate_limit)
        def (builtins.float) -> (def (T`-1) -> RT`-2) -> def (T`-1) -> RT`-2
        >>> 
        >>> @rate_limit(5)
        ... def request_data(name: str) -> int:
        ...     return len(name)
        ... 
        >>> reveal_type(request_data)
        def (builtins.str) -> builtins.int

    Documentation
    -------------
    *New in Python 3.9*

    Doc-strings can be applied to arbitrary objects at runtime for runtime use
    with the `help(...)` function. A few additional pieces of metadata are also
    accessible at runtime to provide clearer documentation, such as the name of
    the result.

        >>> @curry(3)
        ... def add(x: int, y: int, z: int) -> int:
        ...     """Returns add(x)(y)(z) = x + y + z."""
        ...     return x + y + z
        ... 
        >>> help(add)
        Help on Curried in module __main__:
        
        add = curry(3)(add(x: int, y: int, z: int) -> int)
            Returns add(x)(y)(z) = x + y + z.
        
        >>> help(add(1))
        Help on Curried in module __main__:
        
        add(1) = curry(2)(add(x: int, y: int, z: int) -> int, 1)
            Returns add(x)(y)(z) -> x + y + z.
        
        >>> help(add(1)(2))
        Help on Curried in module __main__:
        
        add(1, 2) = curry(1)(add(x: int, y: int, z: int) -> int, 1, 2)
            Returns add(x)(y)(z) -> x + y + z.
        
        >>> add(1)(2)(3)
        6

    Type-Hinting
    ------------
    *New in Python 3.8*

    Type-hints for curried functions are nigh impossible in the general case, as
    can be seen by the last example. However, this doesn't stop us from enabling
    typing in many common use-cases. Curried functions are hinted as functions
    which take any arguments but take `n` calls, up to `n = 3` for Python <
    (3, 11) and up to `n = 4` otherwise. Although the arguments are not
    preserved, the final return type is.

    Note: `reveal_type` is ran using `mypy`.
    
        >>> @curry(2)
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        ... 
        >>> reveal_type(add)
        def (*Any, **Any) -> def (*Any, **Any) -> builtins.int
    
    For Python < (3, 11), one can also use `curry(n, ...)` to hint the curried
    function as taking exactly `1` positional argument per call, up to `n = 3`.
    
        >>> @curry(2, ...)
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        ... 
        >>> reveal_type(add)
        def (builtins.int) -> def (builtins.int) -> builtins.int
    
    For Python >= (3, 11), one can also use `curry(n, ...)` to hint the curried
    function as taking exactly `1` positional argument per call, up to `n = 3`,
    except for the last call. Notice that the `y` parameter is preserved as a
    positional-or-keyword parameter.
    
        >>> @curry(2, ...)
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        ... 
        >>> reveal_type(add)
        def (builtins.int) -> def (y: builtins.int) -> builtins.int
    
    For more precise hinting, one must use `typing.cast` around the currying
    function.
    
        >>> class AddEmpty(typing.Protocol):
        ...     def __call__(self) -> int:
        ...         ...
        ... 
        >>> class AddX(typing.Protocol):
        ...     def __call__(self, x: int) -> int:
        ...         ...
        ... 
        >>> class AddY(typing.Protocol):
        ...     def __call__(self, y: int) -> int:
        ...         ...
        ... 
        >>> class Add(typing.Protocol):
        ...     @typing.overload
        ...     def __call__(self, x: int, y: int) -> AddEmpty:
        ...         ...
        ...     @typing.overload
        ...     def __call__(self, x: int) -> AddY:
        ...         ...
        ...     @typing.overload
        ...     def __call__(self, *, y: int) -> AddX:
        ...         ...
        ...     def __call__(self, x, y):
        ...         ...
        ... 
        >>> @typing.cast(Add, curry(2))
        >>> def add(x: int, y: int) -> int:
        ...     return x + y
        ... 
        >>> reveal_type(add)
        __main__.Add
    '''
    n: int

    def __call__(
        self, func: Callable[..., Any], /, *args: Any, **kwargs: Any
    ) -> Callable[..., Any]:
        if not callable(func):
            raise TypeError("the first argument must be callable")
        result = Curried(self.n, func, *args, **kwargs)
        if hasattr(func, "__annotations__"):
            result.__annotations__ = func.__annotations__
        result.__doc__ = getattr(func, "__doc__", None)
        if result.__doc__ is None or result.__doc__.strip() == "":
            result.__doc__ = "Anonymous curried function."
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
    _wrapped_index: int

    def __init__(self, n: int, *args: Any, **kwargs: Any) -> None:
        self.n = n
        self.args = args
        self.kwargs = kwargs
        self._wrapped_index = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.n == 1:
            return self.args[0](
                *self.args[1:], *args, **self.kwargs, **kwargs
            )
        result = type(self)(
            self.n - 1, *self.args, *args, **self.kwargs, **kwargs
        )
        is_decorator = len(contexts) > 0
        is_decorator &= len(args) == 1
        is_decorator &= len(kwargs) == 0
        is_decorator &= callable(args[0])
        if is_decorator:
            func = args[0]
            result._wrapped_index = len(self.args)
        if is_decorator and isinstance(contexts[-1].get("annotations"), dict):
            result.__annotations__ = contexts[-1]["annotations"]
        elif is_decorator and hasattr(func, "__annotations__"):
            result.__annotations__ = func.__annotations__
        elif "__annotations__" in vars(self):
            result.__annotations__ = self.__annotations__
        if is_decorator and isinstance(contexts[-1].get("doc"), str):
            result.__doc__ = contexts[-1]["doc"]
        elif is_decorator and hasattr(func, "__doc__"):
            result.__doc__ = func.__doc__
        else:
            result.__doc__ = self.__doc__
        if is_decorator and isinstance(contexts[-1].get("module"), str):
            result.__module__ = contexts[-1]["module"]
        elif is_decorator and hasattr(func, "__module__"):
            result.__module__ = func.__module__
        elif "__module__" in vars(self):
            result.__module__ = self.__module__
        result.__wrapped__ = func if is_decorator else self
        if is_decorator and isinstance(contexts[-1].get("name"), str):
            result.__name__ = contexts[-1]["name"]
        elif is_decorator and hasattr(func, "__name__"):
            result.__name__ = func.__name__
        elif "__name__" in vars(self):
            result.__name__ = self.args[0].__name__
        if is_decorator and isinstance(contexts[-1].get("qualname"), str):
            result.__qualname__ = contexts[-1]["qualname"]
        elif is_decorator and isinstance(contexts[-1].get("name"), str):
            result.__qualname__ = result.__module__ + "." + contexts[-1]["name"]
        elif is_decorator and hasattr(func, "__qualname__"):
            result.__qualname__ = func.__qualname__
        elif "__qualname__" in vars(self):
            result.__qualname__ = self.args[0].__qualname__
        if (
            len(self.args) + len(self.kwargs) + len(args) + len(kwargs) == 1
            or "__name__" not in vars(result)
                and "__qualname__" not in vars(result)
            or is_decorator
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
        if (
            is_decorator and hasattr(func, "__name__")
            or "__name__" in vars(self)
        ):
            result.__name__ += params
        if (
            is_decorator and hasattr(func, "__qualname__")
            or "__qualname__" in vars(self)
        ):
            result.__qualname__ += params
        return result

    def __repr__(self) -> str:
        if len(self.args) == 1 and len(self.kwargs) == 0:
            r = as_repr(self.args[0], is_annotated=True)
            return f"curry({self.n})({r})"
        signature = ", ".join([
                as_repr(arg, i == self._wrapped_index)
                for i, arg in enumerate(self.args)
            ])
        if self.kwargs:
            signature += ", "
            signature += ", ".join([
                f"{key}={as_repr(value)}"
                for key, value in self.kwargs.items()
            ])
        return f"curry({self.n})({signature})"


def as_repr(x: Any, is_annotated: bool) -> str:
    if not isinstance(x, (FunctionType, MethodType)):
        return repr(x)
    elif not is_annotated:
        if isinstance(x, MethodType):
            return f"{x.__self__!r}.{x.__name__}"
        elif x.__module__ == "__main__":
            return x.__name__ or "<lambda>"
        else:
            return x.__qualname__ or "<lambda>"
    result = pydoc.text.document(x).split("\n", 1)[0]
    return result
