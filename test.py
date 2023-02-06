from pytyped_curry import curry

@curry(3)
def add(x: int, y: int, z: int) -> int:
    """Returns add(x)(y)(z) -> x + y + z."""
    return x + y + z

help(add)
print("-" * 70)
help(add(1))
print("-" * 70)
help(add(1)(2))
print("-" * 70)

print(add(1)(2)(3))
