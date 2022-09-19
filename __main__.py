import time
from itertools import product

from solver import (
    Cube, rotate, generate_cube, CubeAddError,
    get_all_cubes, get_all_rotates, cube_rotation, print_c
)
from data import figures


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

        print(len(current_set))
        cubes_set.append(current_set)

    for i, cs in enumerate(cubes_set):
        msg = f"""
Итерация {i} из {len(cubes_set)}
    Получено вариантов: {len(base_cubes)}
    Дополнительные варианты: {len(cs)}
    Ожидается вариантов {len(base_cubes) * len(cs)}"""
        print(msg)

        t = time.time()
        new_bases_cube = []
        for base, c in product(base_cubes, cs):
            try:
                new_bases_cube.append(base + c)
            except CubeAddError:
                pass
        base_cubes = new_bases_cube
        print("\tЗатрачено: ", time.time() - t, 'sec')

    print("\nНайдено решение:\n")
    [res] = base_cubes
    print_c(res)
