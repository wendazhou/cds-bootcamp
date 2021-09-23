#! /bin/bash
#SBATCH --time 1:00:00
#SBATCH -c 4
#SBATCH --mem 6GB
#SBATCH --gres=gpu:1


# Set this to the path of the singularity image you wish to use if different from default
IMAGE=${IMAGE:-/scratch/wz2247/singularity/images/pytorch_21.06-py3.sif}
# Set this to the directory containing your package overlays, by default we are using the directory
# from lecture 2
OVERLAY_DIR=${OVERLAY_DIR:-../lecture2}

# Here, we manually set a "low" value for the number of open files (this value is the default!)
ulimit -Sn 1024

singularity exec --no-home -B $HOME/.ssh -B /scratch -B $PWD --nv \
    --cleanenv \
    --overlay $OVERLAY_DIR/overlay-base.ext3:ro \
    --overlay $OVERLAY_DIR/overlay-packages.ext3:ro \
    $IMAGE /bin/bash << 'EOF'
source ~/.bashrc
conda activate /ext3/conda/bootcamp
python -um torch_dataloader_ulimit
EOF

