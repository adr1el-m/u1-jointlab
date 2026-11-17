"""Generate aligned PETG and TPU meshes for two JointLab specimen designs."""
from pathlib import Path
from struct import pack

OUTPUT = Path(__file__).parent / "models"
HEIGHT = 4
FOOTPRINT = {
    (x, y)
    for x in range(-30, 30)
    for y in range(-8, 8)
    if x < -18 or x >= 18 or -6 <= y < 6
}


def material_footprints(keyed):
    petg = {cell for cell in FOOTPRINT if cell[0] < 0}
    if keyed:
        # The wider end of each key resists withdrawal in the pull direction.
        for center in (-3, 3):
            petg.update((x, y) for x in range(2) for y in range(center - 1, center + 1))
            petg.update((x, y) for x in range(2, 4) for y in range(center - 2, center + 2))
    return petg, FOOTPRINT - petg


def write_stl(filename, cells):
    facets = []

    def quad(normal, a, b, c, d):
        for points in ((a, b, c), (a, c, d)):
            facets.append(pack("<12fH", *normal, *(v for point in points for v in point), 0))

    for x, y in sorted(cells):
        lower = ((x, y, 0), (x + 1, y, 0), (x + 1, y + 1, 0), (x, y + 1, 0))
        a, b, c, d = lower
        top = tuple((px, py, HEIGHT) for px, py, _ in lower)
        e, f, g, h = top
        quad((0, 0, -1), a, d, c, b)
        quad((0, 0, 1), e, f, g, h)
        if (x, y - 1) not in cells:
            quad((0, -1, 0), a, b, f, e)
        if (x + 1, y) not in cells:
            quad((1, 0, 0), b, c, g, f)
        if (x, y + 1) not in cells:
            quad((0, 1, 0), c, d, h, g)
        if (x - 1, y) not in cells:
            quad((-1, 0, 0), d, a, e, h)

    filename.write_bytes(b"JointLab specimen".ljust(80) + pack("<I", len(facets)) + b"".join(facets))


def main():
    OUTPUT.mkdir(exist_ok=True)
    for variant in ("plain", "keyed"):
        petg, tpu = material_footprints(keyed=variant == "keyed")
        write_stl(OUTPUT / f"{variant}-petg.stl", petg)
        write_stl(OUTPUT / f"{variant}-tpu.stl", tpu)


if __name__ == "__main__":
    main()
