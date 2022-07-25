from __future__ import annotations
import enum
import math
import typing as t
from itertools import permutations, product, combinations_with_replacement

from utils import ReadOnly


class Axis(enum.Enum):
    X = enum.auto()
    Y = enum.auto()
    Z = enum.auto()


class AxisSection(enum.Enum):
    ONE = enum.auto()
    TWO = enum.auto()
    FREE = enum.auto()
    FOUR = enum.auto()


SECTION_COUNT = 4


class Fragment:

    coords = ReadOnly()
    name = ReadOnly()

    def __init__(self, coords, name):
        self._coords = coords
        self._name = name


def z_90_rotate(coord):
    x, y, z = coord
    return -y, x, z


def y_90_rotate(coord):
    x, y, z = coord
    return z, y, -x


def x_90_rotate(coord):
    x, y, z = coord
    return x, -z, y


def get_rotator(axis: Axis):
    if axis == Axis.X:
        return x_90_rotate
    if axis == Axis.Y:
        return y_90_rotate
    if axis == Axis.Z:
        return z_90_rotate
    raise RuntimeError


def axis_90_rotate(fragment: Fragment, axis: Axis) -> Fragment:
    rotator = get_rotator(axis)
    return Fragment(
        name=fragment.name,
        coords=tuple(map(rotator, fragment.coords))
    )


def axis_rotate(fragment: Fragment, axis: Axis, count) -> Fragment:
    if count <= 0:
        return fragment
    return axis_rotate(fragment, axis, count - 1)


def rotate(fragment: Fragment, rotates) -> Fragment:
    rotate_x, rotate_y, rotate_z = rotates
    fragment = axis_rotate(fragment, Axis.X, rotate_x)
    fragment = axis_rotate(fragment, Axis.Y, rotate_y)
    return axis_rotate(fragment, Axis.Z, rotate_z)


def generate_cube(size):
    return (None, ) * size ** 3


class Cube2dSlice:

    size = ReadOnly()
    cube = ReadOnly()

    def __init__(self, cube, size):
        self._cube = cube
        self._size = size

    def __getitem__(self, item):
        size = self._size
        return self._cube[size * item: size * item + size]


class Cube:

    size = ReadOnly()
    cube = ReadOnly()

    def __init__(self, cube):
        self._size = int(math.pow(len(cube), 1/3))
        self._cube = cube

    def __getitem__(self, item):
        size = self._size ** 2
        return Cube2dSlice(self._cube[item * size: item * size + size], size=self._size)

    def get_cube_coord(self, x, y, z):
        size = self._size
        return size ** 2 * x + size * y + z

    def __str__(self):
        pass


class AddFragmentError(Exception):
    pass


def add_fragment(cube: Cube, figure: Fragment, positions) -> Cube:

    cube_coords = []
    for coords in figure.coords:
        x, y, z = map(sum, zip(coords, positions))
        cb = cube.get_cube_coord(x, y, z)
        cube_coords.append(cb)
        try:
            target = cube[x][y][z]
            if target:
                raise AddFragmentError
        except IndexError:
            raise AddFragmentError

    return Cube(tuple(
        c if i not in cube_coords else figure.name for i, c in enumerate(cube.cube)
    ))


class Assembly:
    def __init__(self, positions, rotates):
        self.positions = positions
        self.rotates = rotates


Assemblies = t.List[Assembly]


def get_pos_(raw_pos, size):
    x = int(math.ceil(raw_pos / size ** 2))
    raw_pos -= x
    y = int(math.ceil(raw_pos / size))
    return x, y, raw_pos - y


def get_rotations():
    rotations = tuple(range(4))
    return product(rotations, rotations, rotations)


def generate_assembly(fragment_count, size) -> t.List[Assemblies]:
    get_rotations_ = list(get_rotations())
    all_positions = tuple(range(size ** 3))
    for pos in permutations(all_positions, fragment_count):
        for rots in combinations_with_replacement(get_rotations_, fragment_count):
            yield (Assembly(get_pos_(res_pos, size), res_rot) for res_pos, res_rot in zip(pos, rots))
