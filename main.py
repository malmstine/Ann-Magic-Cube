import sys
import time
import typing as t
from dataclasses import dataclass
from functools import reduce
from operator import mul
from enum import Enum, auto
from solver import (
    Cube, rotate, generate_cube, CubeAddError,
    get_all_cubes, get_all_rotates, cube_rotation, print_c, Fragment
)
from data import figures as figures_


def to_fragment(name, fragment_coords):
    base, *others = fragment_coords
    mx, my, mz = base
    return Fragment(
        name=name,
        coords=tuple((x - mx, y - my, z - mz) for x, y, z in others)
    )


class MsgTypes(Enum):
    VARIANTS = auto()
    PROGRESS = auto()
    FOUNDED = auto()
    END = auto()
    TOTAL = auto()


@dataclass
class Msg:
    type: MsgTypes
    payload: t.Any | None

    def __iter__(self):
        return iter((self.type, self.payload))


def calculate(figures):

    def send(msg_type, msg):
        return Msg(msg_type, msg)

    base, *others = figures

    e_cube = Cube(generate_cube(3))
    base_cubes = list(get_all_cubes(e_cube, base))

    base_cubes_ = []
    cbs = set()
    for base_c in base_cubes:
        if base_c in cbs:
            continue
        base_cubes_.append(base_c)
        for rotations in get_all_rotates():
            rotated = cube_rotation(base_c, rotations)
            cbs.add(rotated)

    cubes_set = []
    for fig in others:
        current_set = set()
        for rotations in get_all_rotates():
            rotated = rotate(fig, rotations)
            for c in get_all_cubes(e_cube, rotated):
                current_set.add(c)

        cubes_set.append(current_set)

    common_time = time.time()
    cubes_set.insert(0, base_cubes_)

    count = 0
    counts = [len(c_set) for c_set in cubes_set] + [1]
    all_solutions = reduce(mul, counts)
    sols_c = [reduce(mul, counts[cp:]) for cp in range(len(counts))]

    yield send(MsgTypes.VARIANTS, all_solutions)

    tasks = [(e_cube, cube, 0) for cube in cubes_set[0]]
    while tasks:
        cube, new_cube, pos = tasks.pop()
        try:
            pos += 1
            cube = cube + new_cube
            if pos == len(figures):
                yield send(MsgTypes.FOUNDED, cube)
                count += 1
                continue
            tasks.extend((cube, new_cube, pos) for new_cube in cubes_set[pos])
            yield send(MsgTypes.PROGRESS, count)
        except CubeAddError:
            count += sols_c[pos]

    yield send(MsgTypes.PROGRESS, count)
    yield send(MsgTypes.TOTAL, time.time() - common_time)
    yield send(MsgTypes.END, None)


colors = [
    "#fcb33d", "#ffe7bf", "#fadaa4", "#ffd58f", "#fac670", "#ffbd52",
]
colors = colors * 10


def consumer_(gen):
    count_variants = None
    results = []
    for msgtype, value in gen:
        match msgtype:
            case MsgTypes.VARIANTS:
                count_variants = value
                print(f'Всего вариантов: {value}')
                continue

            case MsgTypes.PROGRESS:
                progress = int(value / count_variants * 50)
                sys.stdout.write(f"\rПрогресс: ·{'>' * progress}{' ' * (50 - progress)}·")
                sys.stdout.flush()
                continue

            case MsgTypes.FOUNDED:
                results.append(value)
                continue

            case MsgTypes.TOTAL:
                print(f'\nЗатрачено {value:.3} sec')
                continue

            case MsgTypes.END:
                for res in results:
                    print("\nНайдено решение:\n")
                    print_c(res)
                return


def main():
    try:
        consumer_(
            calculate(figures_)
        )
    except StopIteration:
        pass


if __name__ == '__main__':
    main()
