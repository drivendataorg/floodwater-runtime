# STAC Overflow: Map Floodwater from Radar Imagery

![Python 3.8](https://img.shields.io/badge/Python-3.8-blue) [![GPU Docker Image](https://img.shields.io/badge/Docker%20image-gpu--latest-green)](https://hub.docker.com/r/drivendata/floodwater-competition/tags?page=1&name=gpu-latest) [![CPU Docker Image](https://img.shields.io/badge/Docker%20image-cpu--latest-lightgrey)](https://hub.docker.com/r/drivendata/floodwater-competition/tags?page=1&name=cpu-latest) 

Welcome to the runtime repository for the [STAC Overflow: Map Floodwater from Radar Imagery Challenge](https://www.drivendata.org/competitions/81/detect-flood-water/). This repository contains the definition of the environment where your code submissions will run. It specifies both the operating system and the software packages that will be available to your solution.

This repository has three primary uses for competitors:

- **Useful examples for developing your solutions**: You can find here some helpful materials as you build and test your solution:

    * A properly formatted [sample submission](https://github.com/drivendataorg/floodwater-runtime/tree/main/runtime/data/submission_format);
    * A [baseline solution](https://github.com/drivendataorg/floodwater-runtime/tree/master/benchmark) `main.py` which does not do very much but will run in the runtime environment and outputs a proper submission;
    * An implementation of the [scoring metric](https://github.com/drivendataorg/floodwater-runtime/blob/master/runtime/scripts/metric.py) for local testing

- **Testing your code submission**: It lets you test your `submission.zip` file with a locally running version of the container so you don't have to wait for it to process on the competition site to find programming errors.

- **Requesting new packages in the official runtime**: It lets you test adding additional packages to the official runtime [CPU](https://github.com/drivendataorg/floodwater-runtime/blob/main/runtime/environment-cpu.yml) and [GPU](https://github.com/drivendataorg/floodwater-runtime/blob/main/runtime/environment-gpu.yml) environments. The official runtime uses **Python 3.9.6** environments managed by [Anaconda](https://docs.conda.io/en/latest/). You can then submit a PR to request compatible packages be included in the official container image.

 ----

### [Getting started](#0-getting-started)
 - [Prerequisites](#prerequisites)
 - [Quickstart](#quickstart)
### [Testing your submission locally](#1-testing-your-submission-locally)
 - [Implement your solution](#implement-your-solution)
 - [Example benchmark submission](#example-benchmark-submission)
 - [Making a submission](#making-a-submission)
 - [Reviewing the logs](#reviewing-the-logs)
### [Updating the runtime packages](#2-updating-the-runtime-packages)
 - [Adding new Python packages](#adding-new-python-package)
 - [Adding new R packages](#adding-new-r-packages)
 - [Testing new dependencies](#testing-new-dependencies)
 - [Opening a pull request](#opening-a-pull-request)
### [Useful scripts for local testing](#3-useful-scripts-for-local-testing)

----

## (0) Getting started

### Prerequisites

Make sure you have the prerequisites installed.

 - A clone or fork of this repository
 - [Docker](https://docs.docker.com/get-docker/)
 - At least ~10GB of free space for both the training images and the Docker container images
 - GNU make (optional, but useful for using the commands in the Makefile)

Additional requirements to run with GPU:

 - [NVIDIA drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#package-manager-installation) with **CUDA 11**
 - [NVIDIA Docker container runtime](https://nvidia.github.io/nvidia-container-runtime/)

### Quickstart

To test out the full execution pipeline, run the following commands in order in the terminal. These will get the Docker images, zip up an example submission script, and run the submission on your locally running version of the container.  The `make` commands will try to select the CPU or GPU image automatically by setting the `CPU_OR_GPU` variable based on whether `make` detects `nvidia-smi`.

**Note:** On machines with `nvidia-smi` but a CUDA version other than 11, `make` will automatically select the GPU image, which will fail. In this case, you will have to set `CPU_OR_GPU=cpu` manually in the commands, e.g., `CPU_OR_GPU=cpu make pull`, `CPU_OR_GPU=cpu make test-submission`. If you want to try using the GPU image on your machine but you don't have a GPU device that can be recognized, you can use `SKIP_GPU=true` which will invoke `docker` without the `--gpus all` argument.

Download the [training images](https://www.drivendata.org/competitions/81/detect-flood-water/data/) from the competition and put all the `.tif` files from `training_features` into `runtime/data/test_features` so that you can test locally by pretending your training data is the actual test data expected by the execution environment but which you don't have locally.

```bash
make pull
make pack-benchmark
make test-submission
```

You should see output like this in the end (and find the same logs in the folder `submission/log.txt`):

```
$ make pack-benchmark
cd benchmark; zip -r ../submission/submission.zip ./*
  adding: main.py (deflated 57%)

$ SKIP_GPU=true make test-submission
chmod -R 0777 submission/
docker run \
	-it \
	 \
	--network none \
	--mount type=bind,source="/tmp/floodwater-runtime"/runtime/data,target=/codeexecution/data,readonly \
	--mount type=bind,source="/tmp/floodwater-runtime"/runtime/tests,target=/codeexecution/tests,readonly \
	--mount type=bind,source="/tmp/floodwater-runtime"/runtime/entrypoint.sh,target=/codeexecution/entrypoint.sh \
	--mount type=bind,source="/tmp/floodwater-runtime"/submission,target=/codeexecution/submission \
	--shm-size 8g \
	eec6a1f567e5
+ cd /codeexecution
+ echo 'Unpacking submission...'
Unpacking submission...
+ unzip ./submission/submission.zip -d ./
Archive:  ./submission/submission.zip
  inflating: ./main.py               
+ ls -alh
total 48K
drwxr-xr-x 1 appuser appuser 4.0K Aug  3 18:18 .
drwxr-xr-x 1 root    root    4.0K Aug  3 18:18 ..
drwxrwxr-x 3 appuser appuser 4.0K Aug  3 17:52 data
-rw-rw-r-- 1 appuser appuser  926 Aug  3 18:14 entrypoint.sh
-rw-rw-r-- 1 appuser appuser 2.3K Aug  3 17:42 main.py
drwxr-xr-x 2 appuser appuser 4.0K Jul 31 20:01 scripts
drwxrwxrwx 2 appuser appuser  20K Aug  3 18:13 submission
drwxrwxr-x 3 appuser appuser 4.0K Aug  3 17:59 tests
+ '[' -f main.py ']'
+ echo 'Running submission with Python'
Running submission with Python
+ conda run --no-capture-output -n condaenv python main.py
2021-08-03 18:18:15.302 | INFO     | __main__:main:50 - found 542 expected image ids; generating predictions for each ...

  0%|          | 0/542 [00:00<?, ?it/s]
  5%|▍         | 25/542 [00:00<00:08, 61.74it/s]
  9%|▉         | 50/542 [00:01<00:11, 42.44it/s]
 14%|█▍        | 75/542 [00:01<00:12, 36.70it/s]
 <... snip ...>
 92%|█████████▏| 500/542 [00:15<00:01, 35.03it/s]
 97%|█████████▋| 525/542 [00:17<00:00, 20.64it/s]
100%|██████████| 542/542 [00:20<00:00, 26.82it/s]
2021-08-03 18:18:35.529 | SUCCESS  | __main__:main:57 - ... done
+ echo 'Testing that submission is valid'
Testing that submission is valid
+ conda run -n condaenv pytest -v tests/test_submission.py
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.4, py-1.10.0, pluggy-0.13.1 -- /srv/conda/envs/condaenv/bin/python
cachedir: .pytest_cache
rootdir: /codeexecution
plugins: anyio-3.3.0
collecting ... collected 3 items

tests/test_submission.py::test_all_files_in_format_have_corresponding_submission_file PASSED [ 33%]
tests/test_submission.py::test_no_unexpected_tif_files_in_submission PASSED [ 66%]
tests/test_submission.py::test_file_sizes_are_within_limit PASSED        [100%]

============================== 3 passed in 17.07s ==============================

+ echo 'Compressing files in a gzipped tar archive for submission'
Compressing files in a gzipped tar archive for submission
+ cd ./submission
+ tar czf ./submisson.tar.gz *.tif
+ cd ..
+ echo '... finished'
... finished
+ du -h submission/submisson.tar.gz
620K	submission/submisson.tar.gz
+ echo '================ END ================'
================ END ================
```

## (1) Testing your submission locally

Your submission will run inside a Docker container, a virtual operating system that allows for a consistent software environment across machines. This means that if your submission successfully runs in the container on your local machine, you can be pretty sure it will successfully run when you make an official submission to the DrivenData site.

In Docker parlance, your computer is the "host" that runs the container. The container is isolated from your host machine, with the exception of the following directories:

 - the `data` directory on the host machine is mounted in the container as a read-only directory `/codeexecution/data`
 - the `submission` directory on the host machine is mounted in the container as `/codeexecution/submission`

When you make a submission, the code execution platform will unzip your submission assets to the `/codeexecution` folder. This must result in a `main.py` in the top level `/codeexecution` working directory. (Hint: make sure your `main.py` is compressed at the top level of your `tar`'ed submission and not nested into a directory.)

On the official code execution platform, we will take care of mounting the data―you can assume your submission will have access to `/codeexecution/data/test_features`. You are responsible for creating the submission script that will read from `/codeexecution/data` and write out `.tif`s to `/codeexecution/submission/`. Once your code finishes, some sanity checking tests run and then the script will zip up all the `.tif`s into an archive to be scored on the platform side.

Keep in mind that your submission will not have access to the internet, so everything it needs to run must be provided in the `submission.zip` you create. (You _are_ permitted to write intermediate files to `/codeexecution/submission`, but if they are `.tif` files you will want to clean them up before your script finishes so they aren't considered part of your submission.)

### Implement your solution

In order to test your code submission, you will need a code submission! Implement your solution as a Python script named `main.py`. Next, create a `submission.zip` file containing your code and model assets.

**Note: You will implement all of your training and experiments on your machine. It is highly recommended that you use the same package versions that are in the runtime conda environments ([Python (CPU)](runtime/environment-cpu.yml), [Python (GPU)](runtime/environment-gpu.yml). If you don't wish to use Docker these exact packages can be installed with `conda`.**

The [submission format page](https://www.drivendata.org/competitions/81/detect-flood-water/page/389/) contains the detailed information you need to prepare your code submission.

### Example benchmark submission

We wrote a benchmark in Python to serve as a concrete example of a submission. Use `make pack-benchmark` to create the benchmark submission from the source code. The command zips everything in the `benchmark` folder and saves the zip archive to `submission/submission.zip`. To prevent losing your work, this command will not overwrite an existing submission. To generate a new submission, you will first need to remove the existing `submission/submission.zip`.

### Running your submission

Now you can make sure your submission runs locally prior to submitting it to the platform. Make sure you have the [prerequisites](#prerequisites) installed, and have copied the `train_features` images into the `runtime/test_features` directory. Then, run the following command to download the official image:

```bash
make pull
```

Again, make sure you have packed up your solution in `submission/submission.zip` (or generated the sample submission with `make pack-benchmark`), then try running it:

```bash
make test-submission
```

This will start the container, mount the local data and submission folders as folders within the container, and follow the same steps that will run on the platform to unpack your submission and run your code.

### Reviewing the logs

When you run `make test-submission` the logs will be printed to the terminal. They will also be written to the `submission` folder as `log.txt`. You can always review that file and copy any versions of it that you want from the `submission` folder. The errors there will help you to determine what changes you need to make sure your code executes successfully.

## (2) Updating the runtime packages

We accept contributions to add dependencies to the runtime environment. To do so, follow these steps:

1. Fork this repository
2. Make your changes
3. Test them and commit using git
3. Open a pull request to this repository

If you're new to the GitHub contribution workflow, check out [this guide by GitHub](https://guides.github.com/activities/forking/).

### Adding new Python packages

We use [conda](https://docs.conda.io/en/latest/) to manage Python dependencies. Add your new dependencies to both `runtime/environment-cpu.yml` and `runtime/environment-gpu.yml`.

Your new dependency should follow the format in the yml.

### Opening a pull request

After making and testing your changes, commit your changes and push to your fork. Then, when viewing the repository on github.com, you will see a banner that lets you open the pull request. For more detailed instructions, check out [GitHub's help page](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).

Once you open the pull request, Github Actions will automatically try building the Docker images with your changes and run the tests in `runtime/tests`. These tests can take up to 30 minutes to run through, and may take longer if your build is queued behind others. You will see a section on the pull request page that shows the status of the tests and links to the logs.

You may be asked to submit revisions to your pull request if the tests fail, or if a DrivenData team member asks for revisions. Pull requests won't be merged until all tests pass and the team has reviewed and approved the changes.

---

## Good luck; have fun!

Thanks for reading! Enjoy the competition, and [hit up the forums](https://community.drivendata.org/) if you have any questions!