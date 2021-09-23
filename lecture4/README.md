# Bootcamp 4 examples

This folder contains examples for bootcamp 4.
Many of the examples in this folder are designed to work both on GCP and on Greene.
As previously, we make use of singularity.
In order to avoid duplication, we reuse the base overlay, but as we will install slightly
different packages (e.g. we will use `optuna` and `xgboost`), we have provided another
script `scripts/create_package_overlay.sh` to construct a different package overlay.

To use the base overlay you have previously built, you may copy it into the current directory,
or create a symbolic link:
```{bash}
ln -s ../lecture2/overlay-base.ext3 overlay-base.ext3
```

## SLURM scripts

The `slurm/` folder contains a few SLURM scripts which may be run using `sbatch`
from the current folder.
