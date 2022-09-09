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
srun --account=ds_ga_1006_001-2022fa --partition=n1c10m64-v100-1 -c 10 --gres=gpu:v100:1 --time=8:00:00 --pty /bin/bash
```
As these nodes are backed by virtual machines, they may take a little while (~1-2 minutes) to start up.
Note that you should run this command through Tmux / Screen instance to avoid the machine being
deallocated if you disconnect.

Once the node is started, you can connect additional shells through ssh.
E.g. if the node is called `b-3-1`, simply run `ssh b-3-1` from the `burst` server.
To connect from your laptop, it is easiest to setup appropriate aliases in your `~/.ssh/config` file.
An example such file is provided ass [ssh_config](../lecture2/examples/ssh_config).

## Setting up SSH access to the GCP bursting instances

As the GCP bursting instances have a different filesystem, they do not automatically inherit the keys that you have
uploaded to `greene`. Instead, you will need to upload your public keys again in order to be able to directly
log into these machines.

To do so, we will run the `ssh-copy-id` command from the `burst` server.
- Log on to the `burst` server, and request a new GCP machine.
```
srun --account=ds_ga_1006_001-2022fa --partition=interactive --time=2:00:00 --pty /bin/bash
```
- In a new terminal, log on to the `burst` server again (`ssh greeneburst` from your laptop), and 1) check what is the name of the machine
  you have been given (`squeue -u $USER`), and check that you can `ssh` from `burst` to that machine (let's say you were given `b-2-1`,
  then you would run `ssh b-2-1`).
- In the same terminal, check that your `ssh` agent forwarding is set up correctly. You can run `ssh-add -l` to list the keys available
  to your agent. You should see a key with a path from your laptop.
- In the same terminal, run `ssh-copy-id b-2-1`. This will upload the keys from the agent to the burst instance.
- Check that you can now login from your laptop (`ssh burstinstance` after setting the configuration correctly).

You only need to do this procedure once, after which your keys will be saved to the GCP filesystem.
For the following times, you can simply change your `~/,ssh/config` and log in from your laptop after
requesting the GCP instance.

## GCP Bursting Instance information

The GCP bursting instances are equipped with access to the shared filesystem on GCP, which is persistent
between instances, and can be accessed through the `/scratch` and `/home` directories.
Additionally, each instance has a small local disk (20 GB) containing the operating system, and providing
about 15 GB of remaining free space in `/tmp`.
However, as this local disk is backed by [GCP block storage](https://cloud.google.com/persistent-disk),
it still presents sub-par random access performance.

For best random access performance, there is a ramdisk mounted in `/mnt/ram`, which allows you to use
the memory of the machine as a filesystem.

## Troubleshooting connection issues

If you have trouble connecting using VScode, I suggest you go through the following set of troubleshooting steps.

1. Connect to greene from your laptop. Can you connect to greene from your laptop terminal? (i.e. run `ssh greene`).
   You should only face at most one single password prompt if your keys at set up correctly. To add your keys to `greene`,
   run `ssh-copy-id greene`.
2. Connect to `burst` from `greene`. Once you are connected to `greene`, are you able to subsequently connect to `burst`,
   i.e. can you run (from `greene`) the command `ssh burst`?
3. Connect to `burst` from your laptop. Are you able to connect directly to `burst` from your laptop terminal?
   i.e. run `ssh greeneburst` if you have your `~/.ssh/config` set up on your laptop.
4. Start a GCP instance from burst. When troubleshooting, I recommend you start an instance on the `interactive` partition
   to avoid using up your quota needlessly.
5. Connect to that new instance from `burst`. E.g. assuming that your instance is called `b-9-1`, can you, from `burst`,
   successfully run `ssh b-9-1`? You can check your instance name by running `squeue -u $USER` on the `burst` server.
6. Connect from your laptop to the GCP instance. Make sure to edit your `~/.ssh/config` file to point to the instance,
   and then run `ssh burstinstance` from your laptop.
7. Build the overlay and start the container. Run the overlay scripts, start your container, and ensure that you can
   see the `/places365` folder (i.e. try `ls /places365`).
8. Start the SSH daemon in your container. Activate the `/ext3/conda/bootcamp` environment in the container,
   run the `run_sshd` script.
9. Connect from your laptop to the `burstinstancecontainer`. Run `ssh burstinstancecontainer` from your laptop,
   and ensure that you are connected to the container by checking that you can see the `/places365` folder.
10. Connect VSCode from your laptop.

Common issues.
- If you can run 1, but face two password prompts, or you can run 1-2 but not 3, then you probably need to ensure
  your ssh keys are correctly set up on greene.
- If you can run 1-5 but not 6, you probably need to ensure that your ssh keys are correctly set up on GCP

## Troubleshooting VScode issues

If you are having trouble with VSCode being able to connect, but it has worked in the past, try in order:
  1. Delete the temporary overlay file (`overlay-temp.ext3`), restart your GCP instance, and try again.
  2. If the above did not fix the issue, try deleting and re-creating all overlay files, and restarting your GCP instance.

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
