#! /bin/bash
#SBATCH --time 1:00:00
#SBATCH -c 4
#SBATCH --mem 6GB
#SBATCH --gres=gpu:1


IMAGE=${IMAGE:-/scratch/wz2247/singularity/images/pytorch_21.06-py3.sif}

# We make use of the multirun functionality of hydra to run the training script
# with batch size from 64 to 4096 in increments of powers of two.

# Note that compared to the `start_singularity` script in lecture2,
# I am only using the overlays containing the packages here (and also not loading the data overlays),
# to keep my dependencies minimal.

singularity exec --no-home -B $HOME/.ssh -B /scratch -B $PWD --nv \
    --cleanenv \
    --overlay overlay-base.ext3:ro \
    --overlay overlay-packages.ext3:ro \
    $IMAGE /bin/bash << 'EOF'
source ~/.bashrc
conda activate /ext3/conda/bootcamp
python -um bootcamp.train_lr --multirun batch_size=64,128,256,512,1024,2048,4096
EOF

