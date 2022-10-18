import sys
import time
import typing as t
from dataclasses import dataclass
from functools import reduce
from operator import mul
from enum import Enum, auto
from solver import (
    Cube, rotate, generate_cube, CubeAddError,
    get_all_cubes, get_all_rotates, cube_rotation, print_c
)
from data import figures as figures_


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


def calculate(figures, consumer):

    def send(msg_type, msg):
        msg = Msg(msg_type, msg)
        consumer(msg)

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

    send(MsgTypes.VARIANTS, all_solutions)

    tasks = [(e_cube, cube, 0) for cube in cubes_set[0]]
    while tasks:
        cube, new_cube, pos = tasks.pop()

        try:
            pos += 1
            cube = cube + new_cube
            time.sleep(0.001)
            if pos == len(figures):
                send(MsgTypes.FOUNDED, cube)
                count += 1
                continue
            tasks.extend((cube, new_cube, pos) for new_cube in cubes_set[pos])
            send(MsgTypes.PROGRESS, count)
        except CubeAddError:
            count += sols_c[pos]

    send(MsgTypes.PROGRESS, count)
    send(MsgTypes.TOTAL, time.time() - common_time)
    send(MsgTypes.END, None)


def consumer_():
    count_variants = None
    results = []
    while True:
        msgtype, value = yield
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
        cons = consumer_()
        next(cons)
        calculate(figures_, cons.send)
    except StopIteration:
        pass


if __name__ == '__main__':
    main()
