from pathlib import Path
from typing import List

from loguru import logger
import numpy as np
import typer
from tifffile import imwrite, imread
from tqdm import tqdm

ROOT_DIRECTORY = Path("/codeexecution")
SUBMISSION_DIRECTORY = ROOT_DIRECTORY / "submission"
DATA_DIRECTORY = ROOT_DIRECTORY / "data"
INPUT_IMAGES_DIRECTORY = DATA_DIRECTORY / "test_features"


def make_predictions(image_id: str):
    """
    Given an image ID, read in the appropriate files and predict a mask of all ones or zeros
    """
    try:
        arr_vh = imread(INPUT_IMAGES_DIRECTORY / f"{image_id}_vh.tif")
        arr_vv = imread(INPUT_IMAGES_DIRECTORY / f"{image_id}_vv.tif")
        # TODO: this is the main work! it is your job to implement this
        same_mask = (arr_vv > 0) | (arr_vh > 1)  # this is nonsense but will be boolean
        output_prediction = same_mask.astype(np.uint8)
    except:
        logger.warning(
            f"test_features not found for {image_id}, predicting all zeros; did you download your"
            f"training data into `runtime/data/test_features` so you can test your code?"
        )
        output_prediction = np.zeros(shape=(512, 512), dtype=np.uint8)
    return output_prediction


def get_expected_image_ids():
    """
    Use the submission format directory to see which images are expected
    """
    paths = INPUT_IMAGES_DIRECTORY.glob("*.tif")
    # images are named something like abc12.tif, we only want the abc12 part
    ids = list(sorted(set(path.stem.split("_")[0] for path in paths)))
    return ids


def main():
    """
    for each input file, make a corresponding output file using the `make_predictions` function
    """
    image_ids = get_expected_image_ids()
    logger.info(f"found {len(image_ids)} expected image ids; generating predictions for each ...")
    for image_id in tqdm(image_ids, miniters=25):
        # figure out where this prediction data should go
        output_path = SUBMISSION_DIRECTORY / f"{image_id}.tif"
        # make our predictions! (you should edit `make_predictions` to do something useful)
        output_data = make_predictions(image_id)
        imwrite(output_path, output_data, dtype=np.uint8)
    logger.success(f"... done")


if __name__ == "__main__":
    typer.run(main)
