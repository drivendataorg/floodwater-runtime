FROM nvidia/cuda:11.0-base-ubuntu20.04
# adapated from build file for pangeo images
# https://github.com/pangeo-data/pangeo-docker-images

ARG CPU_OR_GPU=gpu

ENV CONDA_VERSION=4.10.3-2 \
    CONDA_ENV=condaenv \
    NB_USER=appuser \
    NB_UID=1000 \
    SHELL=/bin/bash \
    LANG=C.UTF-8  \
    LC_ALL=C.UTF-8 \
    CONDA_DIR=/srv/conda \
    DEBIAN_FRONTEND=noninteractive

ENV NB_PYTHON_PREFIX=${CONDA_DIR}/envs/${CONDA_ENV} \
    DASK_ROOT_CONFIG=${CONDA_DIR}/etc \
    CPU_OR_GPU=${CPU_OR_GPU} \
    HOME=/home/${NB_USER} \
    PATH=${CONDA_DIR}/bin:${PATH}

# ======================== root ========================
# initialize paths we will use
RUN mkdir -p /codeexecution

# Create appuser user, permissions, add conda init to startup script
RUN echo "Creating ${NB_USER} user..." \
    && groupadd --gid ${NB_UID} ${NB_USER}  \
    && useradd --create-home --gid ${NB_UID} --no-log-init --uid ${NB_UID} ${NB_USER} \
    && echo ". ${CONDA_DIR}/etc/profile.d/conda.sh ; conda activate ${CONDA_ENV}" > /etc/profile.d/init_conda.sh \
    && chown -R ${NB_USER}:${NB_USER} /srv /codeexecution

# Install base packages
ARG DEBIAN_FRONTEND=noninteractive
COPY ./apt.txt /home/${NB_USER}
RUN echo "Installing base packages..." \
    && apt-get update --fix-missing \
    && apt-get install -y apt-utils 2> /dev/null \
    && apt-get install -y wget zip tzdata \
    && xargs -a /home/${NB_USER}/apt.txt apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /home/${NB_USER}/apt.txt
# ======================================================

# ======================== user ========================
USER ${NB_USER}

# Install conda
RUN echo "Installing Miniforge..." \
    && URL="https://github.com/conda-forge/miniforge/releases/download/${CONDA_VERSION}/Miniforge3-${CONDA_VERSION}-Linux-x86_64.sh" \
    && wget --quiet ${URL} -O /home/${NB_USER}/miniconda.sh \
    && /bin/bash /home/${NB_USER}/miniconda.sh -u -b -p ${CONDA_DIR} \
    && rm /home/${NB_USER}/miniconda.sh \
    && conda install -y -c conda-forge mamba \
    && mamba clean -afy \
    && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete

# Switch back to root for installing conda packages
COPY environment-${CPU_OR_GPU}.yml /home/${NB_USER}/environment.yml
RUN mamba env create --name ${CONDA_ENV} -f /home/${NB_USER}/environment.yml  \
    && mamba clean -afy \
    && rm /home/${NB_USER}/environment.yml \
    && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete

# Copy run script into working dir and set it as the working doie
WORKDIR /codeexecution
COPY --chown=appuser:appuser scripts /codeexecution/scripts
COPY --chown=appuser:appuser tests /codeexecution/tests
COPY --chown=appuser:appuser data /codeexecution/data
COPY --chown=appuser:appuser entrypoint.sh /codeexecution/entrypoint.sh
CMD ["/bin/bash", "/codeexecution/entrypoint.sh"]