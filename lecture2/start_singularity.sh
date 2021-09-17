#! /bin/bash


# This script is a utility script to help start singularity with the expected binds and overlays.
# It is intended to be used in conjuction with the `scripts/create_base_overlay.sh` and `scripts/create_package_overlay.sh`
# scripts which create the required overlays.

# The behavior of this script may be configured to manage where the dataset overlay is loaded from
# and where the temporary overlay is placed.


set -e

# Note: on GCP the overlay directory does not exist
OVERLAY_DIRECTORY=/scratch/work/public/overlay-fs-ext3/
if [[ ! -d $OVERLAY_DIRECTORY ]]; then
OVERLAY_DIRECTORY=/scratch/wz2247/singularity/overlays/
fi

TMP_OVERLAY_SOURCE=overlay-0.5GB-200K.ext3

# Set temporary directory in case it is not set
TMPDIR=${TMPDIR:-/tmp}

# This is the name of the temporary writable overlay to use. 
# By default, it is defined as overlay-temp.ext3, but you may
# re-define it to some other value by setting an environment variable
# before calling this script.
TMP_OVERLAY=${TMP_OVERLAY:-overlay-temp.ext3}

# The DATA_DIRECTORY variable defines the directory containing
# the places365.squashfs file. By default, it accesses that file directly
# from the NFS. However, this can be slow, and hence it is often better
# to first copy that file into a local temporary directory (e.g. /tmp),
# and access the file from that local directory.
DATA_DIRECTORY=${DATA_DIRECTORY:-/scratch/wz2247/data/}

IMAGE=${IMAGE:-/scratch/wz2247/singularity/images/pytorch_21.06-py3.sif}

# First, check that the temp overlay exists. Otherwise grap it from the overlays.

if [[ ! -f $TMP_OVERLAY ]]; then

echo "Temporary overlay not found, automatically creating a new one."
cp "$OVERLAY_DIRECTORY/$TMP_OVERLAY_SOURCE.gz" "$TMPDIR"
gunzip "$TMPDIR/$TMP_OVERLAY_SOURCE.gz"
mv "$TMPDIR/$TMP_OVERLAY_SOURCE" "$TMP_OVERLAY"

fi


# This script starts singularity with all the expected binds in place.
# The following binds / overlays are defined

# -B $HOME/.ssh: binds the ssh directory to ensure that ssh authorized keys are propagated
# -B /scratch: binds the entire /scratch filesystem
# -B $PWD: binds the current working directory
# --nv: enables CUDA integration for the container to pass-through GPUs
# --cleanenv: do not propagate environment variables into the container
# --overlay $TMP_OVERLAY: temporary writable ext3 overlay
# --overlay overlay-base.ext3: overlay with the base packages, created by scripts/create_base_overlay.sh
# --overlay overlay-packages.ext3: overlay with our installed packages, created by scripts/create_package_overlay.sh
# --overlay $DATA_DIRECTORY/places365.squashfs: overlay containing the places365 dataset


singularity exec --no-home -B $HOME/.ssh -B /scratch -B $PWD --nv \
    --cleanenv \
    --overlay $TMP_OVERLAY \
    --overlay overlay-base.ext3:ro \
    --overlay overlay-packages.ext3:ro \
    --overlay $DATA_DIRECTORY/places365.squashfs:ro \
    $IMAGE /bin/bash
    
