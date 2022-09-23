# Sample code for homework 2

This folder contains the baseline code for running the training requested in homework 2.
Although you will not need to write significant amounts of new code, it is recommended
that you familiarize yourself with the code presented in this folder, as it can serve
as a basis for your projects.

## Creating the overlays for your container

The `scripts/` folder contains two scripts which create the base overlay, containing a copy
of the pytorch environment provided by Nvidia that we can modify, and the package overlay, installing
additional packages into the environment. By running those scripts from this directory, you will create
the overlays required to work on the homework.

```{bash}
./scripts/create_base_overlay.sh
./scripts/create_package_overlay.sh
```

## Running an instance of your container

The script `./start_singularity_instance.sh` starts an instance of your container named `mycontainer`.
In addition, it creates a "temporary overlay" in the current directory where all changes to your container
instance (e.g. the installation of the vscode server component) are saved. Once you have started your instance,
you can check that it is running using `singularity instance list`, connect to it from vscode as described in
the [documentation](../../../doc/singularity.md).

## Optimizing data access from your container

We are working with a large dataset of images, which comprises of a large number of small files.
Such accesses are difficult to handle efficiently for networked file systems, like what is found
on GCP or on Greene. It will thus be helpful to first copy the data to a local directory before
accessing it.

As all the data is contained within the file `/scratch/wz2247/data/places365.squashfs`, it will
be sufficient to move that file to a local directory which is faster to access on the local computer.
- On GCP / Greene, it is possible to move the data to your RAM. Linux provides a ramdisk at `/dev/shm`,
  to which you can copy the data. For example you may run the following to copy the data into the ramdisk.
  (note that this may take several minutes, as the dataset is large).
```{bash}
rsync --info=progress2 /scratch/wz2247/data/places365.squashfs /dev/shm/
```
- On Greene only, each machine has a large local SSD which provides fast local storage. It is automatically
  made available to you on a new job at the $TMPDIR location. You can copy the data into that SSD as follows.
```{bash}
rsync --info=progress2 /scratch/wz2247/data/places365.squashfs $TMPDIR
```

In either case, the local data will be deleted after your job / instance ends.
To make use of your local copy, simply set the `DATA_DIRECTORY` environment variable before starting
your singularity instance or your singularity command.
For example, assuming you put the data in `/dev/shm`, start your singularity instance in the following fashion:
```{bash}
DATA_DIRECTORY=/dev/shm ./start_singularity_instance.sh
```

## Running commands directly with an image

Athough requesting a shell can be helpful when working interactively, in some cases it may be helpful to simply
run the training command directly (e.g. if you are writing a SLURM script or similar).
In that case, we may use the `conda run` facility to execute a command in the `conda` environment of our choice
directly (without having to explicitly activate the environment).

For example, suppose that I wished to run the tests in my environment, in the container instance that I have already
started. I may then run:
```{bash}
singularity run --containall --pwd=$PWD instance://mycontainer conda run -p /ext3/conda/bootcamp --no-capture-output python -m pytest
```
The command involves three parts:
- `singularity run --containall --pwd=$PWD instance://mycontainer`: this part directs singularity on which container
    to use when executing your command. We pass `--containall` to ensure isolation, but also specify `--pwd=$PWD` to ensure
    that the working directory is set correctly. We specify the container we wish to use using the syntax `instance://mycontainer`,
    indicating that we wish to use a singularity instance (instead of an image).
- `conda run -p /ext3/conda/bootcamp --no-capture-output`: this parts directs `conda` to run our command using the
    given environment. We specify `-p /ext3/conda/bootcamp` to point to the environment we want to use (in this case,
    the environment we created at `/ext3/conda/bootcamp`), and we additionally specify `--no-capture-output` to ensure
    that we see display in real time from the output.
- `python -m pytest`: this parts is the command we wish to run.

Instead of using an instance, we may also use a container image directly, through the `./start_singularity.sh` script.
```{bash}
./start_singularity.sh conda run -p /ext3/conda/bootcamp --no-capture-output python -m pytest
```
where the `./start_singularity.sh` script will ensure that the remaining parts runs within a properly
configured container.
