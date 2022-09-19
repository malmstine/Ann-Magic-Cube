from __future__ import annotations
import enum
import math
import typing as t
from itertools import product, starmap
from operator import sub, add

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

    def __hash__(self):
        return self.name, hash(frozenset(self._coords))

    def __eq__(self, other: Fragment):
        return self.name == other.name and set(self._coords) == set(other._coords)


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
    fragment = axis_90_rotate(fragment, axis)
    return axis_rotate(fragment, axis, count - 1)


def rotate(fragment: Fragment, rotates) -> Fragment:
    rotate_x, rotate_y, rotate_z = rotates
    fragment = axis_rotate(fragment, Axis.X, rotate_x)
    fragment = axis_rotate(fragment, Axis.Y, rotate_y)
    return axis_rotate(fragment, Axis.Z, rotate_z)


def generate_cube(size):
    return (0, ) * size ** 3


class Cube2dSlice:

    size = ReadOnly()
    cube = ReadOnly()

    def __init__(self, cube, size):
        self._cube = cube
        self._size = size

    def __getitem__(self, item):
        size = self._size
        return self._cube[size * item: size * item + size]

    def __iter__(self):
        for s in range(self._size):
            yield self[s]


class CubeAddError(Exception):
    pass


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
        return size ** 2 * z + size * y + x

    def get_coords(self, cell):
        base = self._size
        digits = []
        while cell:
            digits.append(cell % base)
            cell = cell // base
        digits += [0] * base
        return digits[:3]

    @property
    def catsisland(self):
        return enumerate(self._cube)

    def __str__(self):
        pass

    def __iter__(self):
        for s in range(self._size):
            yield self[s]

    def __hash__(self):
        return hash(self._cube)

    def __eq__(self, other):
        return self._cube == self._cube

    def __add__(self, other: Cube):
        if self._size != other._size:
            raise CubeAddError

        new_cells = []
        for sc, oc in zip(self._cube, other._cube):
            if sc and oc:
                raise CubeAddError
            new_cells.append(sc or oc)
        return Cube(tuple(new_cells))


class AddFragmentError(Exception):
    pass


def add_fragment(cube: Cube, figure: Fragment, positions) -> Cube:

    cube_coords = []
    for coords in figure.coords + ((0, 0, 0), ):
        x, y, z = map(sum, zip(coords, positions))
        cb = cube.get_cube_coord(x, y, z)
        cube_coords.append(cb)
        if min(x, y, z) < 0:
            raise AddFragmentError
        try:
            target = cube[x][y][z]
            if target:
                raise AddFragmentError
        except IndexError:
            raise AddFragmentError

    return Cube(tuple(
        c if i not in cube_coords else figure.name for i, c in enumerate(cube.cube)
    ))


def get_pos_(raw_pos, size):
    x = int(math.ceil(raw_pos / size ** 2))
    raw_pos -= x
    y = int(math.ceil(raw_pos / size))
    return x, y, raw_pos - y


def get_rotations():
    rotations = tuple(range(4))
    return product(rotations, rotations, rotations)


def get_figure(cube, cells, name) -> Fragment:
    coords = []
    for c in cells:
        coords.append(cube.get_coords(c))

    first, *others = coords
    x, y, z = first
    return Fragment(
        name=name,
        coords=tuple(
            (xx - x, yy - y, zz - z) for xx, yy, zz in others
        )
    )


def get_free_cells(cube: Cube) -> t.List:
    for cell_num, cell in cube.catsisland:
        if not cell:
            yield cell_num


def compare(normalized: Fragment, figure: Fragment) -> bool:
    for rotates in product(range(4), repeat=3):
        rotated = rotate(figure, rotates)
        rotated_coords = tuple(sorted(rotated.coords + ((0, 0, 0), )))
        base_coords = tuple(sorted(normalized.coords + ((0, 0, 0), )))
        dx, dy, dz = starmap(sub, zip(base_coords[0], rotated_coords[0]))
        rotated_coords = tuple(
            (x + dx, y + dy, z + dz) for x, y, z in rotated_coords
        )
        if rotated_coords == base_coords:
            return True
    return False


def get_all_rotates():
    return product(range(4), repeat=3)


def get_all_cubes(cube: Cube, figure: Fragment):
    for cell_number, cell in cube.catsisland:
        coords = cube.get_coords(cell_number)
        try:
            yield add_fragment(cube, figure, coords)
        except AddFragmentError:
            pass


def mod(num):
    return -num if num < 0 else num


class CubeRotationException(Exception):
    pass


def cube_rotation(cube: Cube, rotations):
    try:
        [fragment_name] = set(c for c in cube.cube if c)
    except ValueError:
        raise CubeRotationException

    sw = (cube.size, cube.size, cube.size)
    # noinspection PyTypeChecker
    fragment = Fragment(
        coords=tuple(
            cube.get_coords(cell_num) for cell_num, cell in cube.catsisland if cell
        ) + (sw, ),
        name=None
    )

    size = cube.size - 1
    fragment = rotate(fragment, rotations)
    [new_sw] = (coord for coord in fragment.coords if tuple(map(mod, coord)) == sw)
    delta = [size if s < 0 else 0 for s in new_sw]

    cube_coords = tuple(
        cube.get_cube_coord(*starmap(add, zip(delta, coord)))
        for coord in fragment.coords if tuple(map(mod, coord)) != sw
    )

    return Cube(tuple(
        fragment_name if i in cube_coords else 0 for i, c in enumerate(cube.cube)
    ))


def print_c(c):
    for plot in c:
        for row in plot:
            print(*row, sep='  ')
        print("")
