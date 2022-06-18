from __future__ import annotations
import enum
import typing as t


class Axis(enum.Enum):
    X = enum.auto()
    Y = enum.auto()
    Z = enum.auto()


class Fragment:

    def __init__(self, coords, name):
        self.coords = coords
        self.name = name


def rotate(fragment: Fragment, rotates) -> Fragment:
    ...


def generate_cube(size, deep=None):
    if deep is None:
        deep = size
    if deep == 0:
        return None
    ret = []
    for _ in range(size):
        ret.append(generate_cube(size, deep - 1))
    return ret


class Cube:

    def __init__(self, size):
        self.size = size
        self.cube = generate_cube(size)

    def __getitem__(self, item):
        return self.cube[item]

    def __str__(self):
        pass


class AddFragmentError(Exception):
    pass


def add_fragment(cube: Cube, figure: Fragment, positions) -> Cube:
    pass


class Assembly:
    def __init__(self, positions, rotates):
        self.positions = positions
        self.rotates = rotates


Assemblies = t.List[Assembly]


def generate_assembly(fragment_count) -> t.List[Assemblies]:
    pass
