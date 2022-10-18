import sys
import time
from functools import reduce
from operator import mul

from solver import (
    Cube, rotate, generate_cube, CubeAddError,
    get_all_cubes, get_all_rotates, cube_rotation, print_c
)
from data import figures


class TimeSplitter:
    def __init__(self, delta=0.01):
        self.time = time.time()
        self.delta = delta

    def __bool__(self):
        time_ = time.time()
        if time_ - self.time > self.delta:
            self.time = time_
            return True
        return False


if __name__ == '__main__':
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

    base_cubes = base_cubes_

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

    completed = []

    tasks = [(e_cube, cube, 0) for cube in cubes_set[0]]

    counts = [len(c_set) for c_set in cubes_set] + [1]
    print('Полученные размеры:', *counts)
    count = 0

    all_solutions = reduce(mul, counts)
    sols_c = [
      reduce(mul, counts[cp:]) for cp in range(len(counts))
    ]
    print('Всего вариантов: ', all_solutions)

    while tasks:
        cube, new_cube, pos = tasks.pop()

        try:
            pos += 1
            cube = cube + new_cube
            time.sleep(0.01)
            if pos == len(figures):
                completed.append(cube)
                count += 1
                continue
            tasks.extend((cube, new_cube, pos) for new_cube in cubes_set[pos])
            progress = int(count / all_solutions * 50)
            sys.stdout.write(f"\rПрогресс: ·{'>' * progress}{' ' * (50 - progress)}·")
            sys.stdout.flush()
        except CubeAddError:
            count += sols_c[pos]

    print(f"\rПрогресс: ·{'>' * 50}·")
    print(f'Затрачено {time.time() - common_time:.3} sec')
    print("\nНайдено решение:\n")
    for res in completed:
        print_c(res)
