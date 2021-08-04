from pathlib import Path

from skimage.io import imread

SUBMISSION_DIR = Path("submission")
INPUT_IMAGES_DIR = Path("data/test_features")
MAX_FILE_SIZE = 512 * 512 * 2  # 2x fudge factor over one byte (uint8) per pixel


def get_expected_image_ids():
    """
    Use the submission format directory to see which images are expected
    """
    paths = INPUT_IMAGES_DIR.glob("*.tif")
    # images are named something like abc12.tif, we only want the abc12 part
    ids = list(sorted(set(path.stem.split("_")[0] for path in paths)))
    return ids


def test_all_files_in_format_have_corresponding_submission_file():
    for image_id in get_expected_image_ids():
        filename = f"{image_id}.tif"
        submission_path = SUBMISSION_DIR / filename
        assert submission_path.exists(), f"File {filename} missing from your submission"

        input_path = INPUT_IMAGES_DIR / f"{image_id}_vv.tif"
        input_arr = imread(input_path)
        output_arr = imread(submission_path)
        expected_shape = input_arr.shape
        assert (
            output_arr.shape == expected_shape
        ), f"{filename} shape={output_arr.shape}, expected {expected_shape}"

        mask = (output_arr == 0) | (output_arr == 1)
        assert mask.ravel().all(), "All values in file must be either 0 or 1"


def test_no_unexpected_tif_files_in_submission():
    for submission_path in SUBMISSION_DIR.glob("*.tif"):
        filename = submission_path.name
        image_id = filename.split(".")[0]
        input_path = INPUT_IMAGES_DIR / f"{image_id}_vv.tif"
        assert input_path.exists(), f"Found unexpected file {filename} in submission"


def test_file_sizes_are_within_limit():
    for submission_path in SUBMISSION_DIR.glob("*.tif"):
        size_bytes = submission_path.stat().st_size
        err_msg = f"{submission_path} is {size_bytes:,} bytes; over limit of {MAX_FILE_SIZE:,} bytes"
        assert size_bytes <= MAX_FILE_SIZE, err_msg
