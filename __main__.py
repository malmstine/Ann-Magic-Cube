from __future__ import annotations

from solver import generate_assembly, Cube, rotate, add_fragment, AddFragmentError

SIZE = 0
figures = []


if __name__ == '__main__':
    for assemblies in generate_assembly(len(figures)):
        cube = Cube(SIZE)
        for asm, figure in zip(assemblies, figures):
            figure = rotate(figure, asm.rotates)
            try:
                cube = add_fragment(cube, figure, asm.positions)
            except AddFragmentError:
                continue
