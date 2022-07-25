from __future__ import annotations

from solver import generate_assembly, Cube, rotate, add_fragment, AddFragmentError
from data import figures

SIZE = 3

if __name__ == '__main__':
    import time
    for assemblies in generate_assembly(len(figures), SIZE):
        cube = Cube((None, ) * SIZE ** 3)

        t = time.time()
        for asm, figure in zip(assemblies, figures):
            figure = rotate(figure, asm.rotates)
            try:
                cube = add_fragment(cube, figure, asm.positions)

            except AddFragmentError:
                print(time.time() - t)
                t = time.time()
                continue

