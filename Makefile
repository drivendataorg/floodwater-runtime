.PHONY: build debug-container export-requirements pack-benchmark pull resolve-requirements test-container test-submission unpin-requirements

# ================================================================================================
# Settings
# ================================================================================================

ifeq (, $(shell which nvidia-smi))
CPU_OR_GPU ?= cpu
else
CPU_OR_GPU ?= gpu
endif

ifeq (${CPU_OR_GPU}, gpu)
GPU_ARGS = --gpus all
endif

SKIP_GPU ?= false
ifeq (${SKIP_GPU}, true)
GPU_ARGS =
endif

REPO = drivendata/floodwater-competition

TAG = ${CPU_OR_GPU}-latest
LOCAL_TAG = ${CPU_OR_GPU}-local

IMAGE = ${REPO}:${TAG}
LOCAL_IMAGE = ${REPO}:${LOCAL_TAG}

# if not TTY (for example GithubActions CI) no interactive tty commands for docker
ifneq (true, ${GITHUB_ACTIONS_NO_TTY})
TTY_ARGS = -it
endif

# To run a submission, use local version if that exists; otherwise, use official version
# setting SUBMISSION_IMAGE as an environment variable will override the image
SUBMISSION_IMAGE ?= $(shell docker images -q ${LOCAL_IMAGE})
ifeq (,${SUBMISSION_IMAGE})
SUBMISSION_IMAGE := $(shell docker images -q ${IMAGE})
endif

# Give write access to the submission folder to everyone so Docker user can write when mounted
_submission_write_perms:
	chmod -R 0777 submission/

# ================================================================================================
# Commands for building the container if you are changing the requirements
# ================================================================================================

## Builds the container locally, tagging it with cpu-local or gpu-local
build:
	docker build --build-arg CPU_OR_GPU=${CPU_OR_GPU} -t ${LOCAL_IMAGE} runtime

# ================================================================================================
# Commands for testing that your submission.zip will execute
# ================================================================================================

## Pulls the official container tagged cpu-latest or gpu-latest from Docker hub
pull:
	docker pull ${IMAGE}

## Creates a submission/submission.zip file from whatever is in the "benchmark" folder
pack-benchmark:
# Don't overwrite so no work is lost accidentally
ifneq (,$(wildcard ./submission/submission.zip))
	$(error You already have a submission/submission.zip file. Rename or remove that file (e.g., rm submission/submission.zip).)
endif
	cd benchmark; zip -r ../submission/submission.zip ./*


## Runs container with submission/submission.zip as your submission and data as the data to work with
test-submission: _submission_write_perms

# if submission file does not exist
ifeq (,$(wildcard ./submission/submission.zip))
	$(error To test your submission, you must first put a "submission.zip" file in the "submission" folder. \
	  If you want to use the benchmark, you can run `make pack-benchmark` first)
endif

# if container does not exists, error and tell user to pull or build
ifeq (${SUBMISSION_IMAGE},)
	$(error To test your submission, you must first run `make pull` (to get official container) or `make build` \
		(to build a local version if you have changes).)
endif
	docker run \
		${TTY_ARGS} \
		${GPU_ARGS} \
		--network none \
		--mount type=bind,source="$(shell pwd)"/runtime/data,target=/codeexecution/data,readonly \
		--mount type=bind,source="$(shell pwd)"/runtime/tests,target=/codeexecution/tests,readonly \
		--mount type=bind,source="$(shell pwd)"/runtime/entrypoint.sh,target=/codeexecution/entrypoint.sh \
		--mount type=bind,source="$(shell pwd)"/submission,target=/codeexecution/submission \
		--shm-size 8g \
		${SUBMISSION_IMAGE}


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help
.PHONY: help

define PRINT_HELP_PYSCRIPT
import re, sys

pattern = re.compile(r'^## (.*)\n(.+):', re.MULTILINE)
text = "".join(line for line in sys.stdin)
for match in pattern.finditer(text):
    help, target = match.groups()
    print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)