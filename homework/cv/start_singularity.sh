#! /bin/bash


# This script is a utility script to help start singularity with the expected binds and overlays.
# It is intended to be used in conjuction with the `scripts/create_base_overlay.sh` and `scripts/create_package_overlay.sh`
# scripts which create the required overlays.

# The behavior of this script may be configured to manage where the dataset overlay is loaded from
# and where the temporary overlay is placed.


set -e

# The DATA_DIRECTORY variable defines the directory containing
# the places365.squashfs file. By default, it accesses that file directly
# from the NFS. However, this can be slow, and hence it is often better
# to first copy that file into a local temporary directory (e.g. /tmp),
# and access the file from that local directory.
DATA_DIRECTORY=${DATA_DIRECTORY:-/scratch/wz2247/data/}

IMAGE=${IMAGE:-/scratch/wz2247/singularity/images/pytorch_22.08-py3.sif}


# This script starts singularity with all the expected binds in place.
# The following binds / overlays are defined

# --containall --no-home Ensures that the container is well isolated
# -B $HOME/.ssh: binds the ssh directory to ensure that ssh authorized keys are propagated
# -B /scratch: binds the entire /scratch filesystem
# -B $PWD: binds the current working directory
# --nv: enables CUDA integration for the container to pass-through GPUs
# --overlay overlay-base.ext3: overlay with the base packages, created by scripts/create_base_overlay.sh
# --overlay overlay-packages.ext3: overlay with our installed packages, created by scripts/create_package_overlay.sh
# --overlay $DATA_DIRECTORY/places365.squashfs: overlay containing the places365 dataset

singularity exec --containall --no-home -B $HOME/.ssh -B /scratch -B $PWD --nv \
    --overlay overlay-base.ext3:ro \
    --overlay overlay-packages.ext3:ro \
    --overlay $DATA_DIRECTORY/places365.squashfs:ro \
    --writable-tmpfs \
    --pwd $PWD \
    $IMAGE "$@"
    
