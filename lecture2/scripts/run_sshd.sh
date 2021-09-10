#! /bin/bash


# This script starts a user-space SSH daemon listening on port 12345
# It is mainly intended to be run inside a container to enable vscode integration.
# In general, it is expected that you will be running this script inside a singularity container.

# Note that due to the isolation rules of singularity the started SSH daemon here may outlive the container.
# This may prevent you from starting another SSH daemon if you launch a new instance of your container.
# In order to avoid this issue, you may kill the daemon process directly
#
# First run `ps -u $USER` and look for `sshd` processes with high PIDs,
# these correspond to the processes started inside a container.
# You may simply stop them with `kill -9 PID` where PID is the value you observed from the previous command.


set -u

SSH_KEY_DIR=/ext3/ssh/
mkdir -p $SSH_KEY_DIR


if [[ ! -f $SSH_KEY_DIR/ssh_host_rsa_key ]]; then
ssh-keygen -f $SSH_KEY_DIR/ssh_host_rsa_key -N '' -t rsa -b 2048
fi

if [[ ! -f $SSH_KEY_DIR/ssh_host_ecdsa_key ]]; then
ssh-keygen -f $SSH_KEY_DIR/ssh_host_ecdsa_key -N '' -t ecdsa -b 256
fi

# This is the port on the GCP instance that will be used by the SSH daemon
SSHD_PORT=12345
SSHD_PATH=$(which sshd)

if [[ -z "$SSHD_PATH" ]]; then
echo "Could not find sshd executable)"
exit 1
fi

# Propagate environment variables to new shells
env > ~/.ssh/environment

# Start new ssh daemon binding to user port. We specify the config file as /dev/null
# to prevent sshd from reading the default config file (which requires root)
echo "Starting SSH daemon"
$SSHD_PATH -f /dev/null -p $SSHD_PORT -h $SSH_KEY_DIR/ssh_host_rsa_key -h $SSH_KEY_DIR/ssh_host_ecdsa_key -o PermitUserEnvironment=yes
