#! /bin/bash

set -e

# Note: on GCP the overlay directory does not exist
OVERLAY_DIRECTORY=/scratch/work/public/overlay-fs-ext3/
if [[ ! -d $OVERLAY_DIRECTORY ]]; then
OVERLAY_DIRECTORY=/scratch/wz2247/singularity/overlays/
fi

TMP_OVERLAY=overlay-0.5GB-200K.ext3

DATA_DIRECTORY=${DATA_DIRECTORY:-/scratch/wz2247/data/}
IMAGE=${IMAGE:-/scratch/wz2247/singularity/images/pytorch_21.06-py3.sif}

# First, check that the temp overlay exists. Otherwise grap it from the overlays.

if [[ ! -f overlay-temp.ext3 ]]; then

echo "Temporary overlay not found, automatically creating a new one."
cp $OVERLAY_DIRECTORY/$TMP_OVERLAY.gz .
gunzip $TMP_OVERLAY.gz
mv $TMP_OVERLAY overlay-temp.ext3

fi


# This script starts singularity with all the expected binds in place.
# The following binds / overlays are defined

# -B $HOME/.ssh: binds the ssh directory to ensure that ssh authorized keys are propagated
# -B /scratch: binds the entire /scratch filesystem
# --overlay overlay-temp.ext3: temporary writable ext3 overlay
# --overlay overlay-base.ext3: overlay with the base packages, created by scripts/create_base_overlay.sh
# --overlay overlay-packages.ext3: overlay with our installed packages, created by scripts/create_package_overlay.sh
# --overlay $DATA_DIRECTORY/places365.squashfs: overlay containing the places365 dataset


singularity exec --no-home -B $HOME/.ssh -B /scratch -B $PWD --nv \
    --overlay overlay-temp.ext3 \
    --overlay overlay-base.ext3:ro \
    --overlay overlay-packages.ext3:ro \
    --overlay $DATA_DIRECTORY/places365.squashfs:ro \
    $IMAGE /bin/bash
    
