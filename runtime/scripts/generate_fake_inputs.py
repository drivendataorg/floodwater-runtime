from pathlib import Path

import typer
import numpy as np
from tifffile import imwrite


def get_flood_id():
    return "".join(np.random.choice(list("abcdefg"), size=3))


def main(
    output_dir: Path,
    n_floods: int = 3,
    n_per_flood: int = 10,
    width: int = 512,
    height: int = 512,
    percent_missing: float = 0.05,
    seed: int = 42,
):
    np.random.seed(seed)
    floods = [get_flood_id() for _ in range(n_floods)]
    for flood in floods:
        for i in range(n_per_flood):
            chip_id = f"{flood}{i:02d}"
            for polarity in "vh":
                filename = f"{chip_id}_v{polarity}.tif"
                output_path = output_dir / filename
                arr = np.random.random(size=(height, width)).round().astype(np.uint8)
                na_mask = np.random.random(size=(height, width)) > (1 - percent_missing)
                arr[na_mask] = 255
                imwrite(output_path, arr, dtype=np.uint8)


if __name__ == "__main__":
    typer.run(main)
