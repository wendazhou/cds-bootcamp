#! /bin/bash
#SBATCH --time 1:00:00
#SBATCH -c 4
#SBATCH --mem 6GB
#SBATCH --gres=gpu:1


# Set this to the path of the singularity image you wish to use if different from default
IMAGE=${IMAGE:-/scratch/wz2247/singularity/images/pytorch_21.06-py3.sif}

# Here, we manually set the maximum value for the number of open files
ulimit -Sn $(ulimit -Hn)

singularity exec --no-home -B $HOME/.ssh -B /scratch -B $PWD --nv \
    --cleanenv \
    --overlay overlay-base.ext3:ro \
    --overlay overlay-packages.ext3:ro \
    $IMAGE /bin/bash << 'EOF'
source ~/.bashrc
conda activate /ext3/conda/bootcamp
python -um bootcamp.torch_dataloader_ulimit
EOF

