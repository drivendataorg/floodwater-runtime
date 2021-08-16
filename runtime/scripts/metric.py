from pathlib import Path
from loguru import logger
import numpy as np
from tifffile import imread
import typer
from tqdm import tqdm

NA_VALUE = 255


def iterate_through_mask_pairs(submission_dir: Path, actual_dir: Path):
    """
    For each tif in the actual directory, find the corresponding prediction tif, read
    them both in, and yield the (pred, actual) tuple
    """
    for actual_path in actual_dir.glob("*.tif"):
        filename = actual_path.name
        predicted_path = submission_dir / filename
        assert predicted_path.exists(), f"Could not find expected file: {filename}"
        actual = imread(actual_path)
        pred = imread(predicted_path)
        yield pred, actual


def intersection_over_union(array_pairs, total=None):
    """Calculate the actual metric"""
    intersection = 0
    union = 0
    for pred, actual in tqdm(array_pairs, total=total):
        invalid_mask = actual == NA_VALUE
        actual = np.ma.masked_array(actual, invalid_mask)
        pred = np.ma.masked_array(pred, invalid_mask)
        intersection += np.logical_and(actual, pred).sum()
        union += np.logical_or(actual, pred).sum()
    if union < 1:
        raise ValueError("At least one image must be in the actual data set")
    return intersection / union


def main(submission_dir: Path, actual_dir: Path):
    """
    Given a directory with the predicted mask files (all values in {0, 1}) and the actual
    mask files (all values in {0, 1, 255}), get the overall intersection-over-union score
    """
    n_expected = len(list(actual_dir.glob("*.tif")))
    array_pairs = iterate_through_mask_pairs(submission_dir, actual_dir)
    logger.info(f"calculating score for {n_expected} image pairs ...")
    score = intersection_over_union(array_pairs, total=n_expected)
    logger.success(f"overall score: {score}")


if __name__ == "__main__":
    typer.run(main)
