# Working on NYU GCP Bursting

This folder contains documentation for working on NYU GCP Bursting, using a VSCode-based remote development setup.
Note that as this service offered by NYU is very new, the documentation is in flux.
Please ask questions on the brightspace forum if you encounter any issue.


## Connecting to GCP bursting

The GCP bursting system is controlled from the `burst` server, which must be accessed through the `greene.hpc.nyu.edu`
login nodes.
We have access to four types of GCP instances, please choose them judiciously depending on your needs

| Partition    | CPUs | Memory   | GPUs   |
|--------------|------|----------|--------|
| interactive  |    2 |  1.5 GB  | N/A    |
| c2s16p       |   16 |  64 GB   | N/A    |
| n1s8-v100-1  |    8 |  29 GB   | 1 V100 |
| n1s16-v100-2 |   16 |  59 GB   | 2 V100 |

These nodes should be allocated through SLURM, e.g.:
```{bash}
srun --account=ds_ga_1006_001 --partition=n1s8-v100-1 --gres=gpu:v100:1 --time=8:00:00 --pty /bin/bash
```
As these nodes are backed by virtual machines, they may take a little while (~1-2 minutes) to start up.
Note that you should run this command through Tmux / Screen instance to avoid the machine being
deallocated if you disconnect.

Once the node is started, you can connect additional shells through ssh.
E.g. if the node is called `b-3-1`, simply run `ssh b-3-1` from the `burst` server.
To connect from your laptop, it is easiest to setup appropriate aliases in your `~/.ssh/config` file.
An example such file is provided ass [ssh_config](../lecture2/examples/ssh_config).
