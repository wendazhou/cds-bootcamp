# Working on NYU GCP Bursting

This folder contains documentation for working on NYU GCP Bursting, using a VSCode-based remote development setup.
Note that as this service offered by NYU is very new, the documentation is in flux.
Please ask questions on the brightspace forum if you encounter any issue.


## Connecting to Greene

To access the GCP bursting system, we first need to go through the main NYU HPC cluster Greene.
NYU HPC provides instructions on how to access these systems [here](https://sites.google.com/a/nyu.edu/nyu-hpc/documentation/hpc-access).
To ensure that the following workflows function smoothly, you should set up key-based (passwordless)
authentication to Greene (note: you will still need to enter your password once for the gateway if you
are not using a VPN).
To set-up key-based authentication to Greene, simply use:
```{bash}
ssh-copy-id -i ~/.ssh/id_rsa greene
```
Assuming that you have set-up your `.ssh/config` file with the correct host aliases.


## Connecting to GCP bursting

The GCP bursting system is controlled from the `burst` server, which must be accessed through the `greene.hpc.nyu.edu`
login nodes.
We have access to four types of GCP instances, please choose them judiciously depending on your needs

| Partition       | CPUs | Memory   | GPUs   |
|-----------------|------|----------|--------|
| interactive     |    2 |  1.5 GB  | N/A    |
| c2s16p          |   16 |  64 GB   | N/A    |
| n1c10m64-v100-1 |   10 |  64 GB   | 1 V100 |
| n1c16m96-v100-2 |   16 |  96 GB   | 2 V100 |

These nodes should be allocated through SLURM, e.g.:
```{bash}
srun --account=ds_ga_1006_001 --partition=n1c10m64-v100-1 -c 10 --gres=gpu:v100:1 --time=8:00:00 --pty /bin/bash
```
As these nodes are backed by virtual machines, they may take a little while (~1-2 minutes) to start up.
Note that you should run this command through Tmux / Screen instance to avoid the machine being
deallocated if you disconnect.

Once the node is started, you can connect additional shells through ssh.
E.g. if the node is called `b-3-1`, simply run `ssh b-3-1` from the `burst` server.
To connect from your laptop, it is easiest to setup appropriate aliases in your `~/.ssh/config` file.
An example such file is provided ass [ssh_config](../lecture2/examples/ssh_config).


## GCP Bursting Instance information

The GCP bursting instances are equipped with access to the shared filesystem on GCP, which is persistent
between instances, and can be accessed through the `/scratch` and `/home` directories.
Additionally, each instance has a small local disk (20 GB) containing the operating system, and providing
about 15 GB of remaining free space in `/tmp`.
However, as this local disk is backed by [GCP block storage](https://cloud.google.com/persistent-disk),
it still presents sub-par random access performance.

For best random access performance, there is a ramdisk mounted in `/mnt/ram`, which allows you to use
the memory of the machine as a filesystem.

## Troubleshooting connection to burstinstance

A common error that you may encounter is that you are not able to connect to `burstinstance` from your laptop,
even though you are able to connect to the instance from the `burst` server.
If that is the case, the most likely cause is that the `~/.ssh/authorized_keys` file on the burst instance do
not contain the key your are attempting to use from your laptop.
You may check the authorized keys by opening the `~/.ssh/authorized_keys` file on the GCP instance in an editor
(e.g. `nano` or `vim`).
If you only see a single line (note that it may wrap), ending in a comment which looks like `wz2247@log-4.nyu.cluster`,
only the key provided to you by NYU HPC on the cluster is present, and you will not be able to log in.
To fix this, you can copy paste the content of your `~/.ssh/id_rsa.pub` file (on your laptop) into the `~/.ssh/authorized_keys`
file (on the GCP instance) in a new line to save your key to the cluster.
