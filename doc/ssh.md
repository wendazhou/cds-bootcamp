# SSH Configuration tips and tricks

This document goes through the knobs to configure SSH in order to make the experience as smooth as possible.

## `.ssh/config` file

The main file we will use to make changes to how `ssh` behaves is the `~/.ssh/config` file.
It is a set of key-value pairs controlling how various aspects of the SSH connection are handled.

The rules in the files are grouped by `Host`, which denote the computer you want to connect to.
The most basic configuration is to introduce an alias for the host, which allows us to use
a nickname for a long url.
```
Host nyugateway
    User wz2247
    Hostname gw.hpc.nyu.edu
```
This configuration indicates to `ssh` that when I type `ssh nyugateway`, I wish to connect
to the given hostname with the given username.

## Key-based authentication

Instead of using passwords, ssh is able to make use of a mathematical system to prove
your identity using a secret number stored on your computer. This is commonly referred
to as key-based authentication (from the cryptographic keys being used).
By default, you will probably have a key pair `.ssh/id_rsa`.

To let the server know about your key, you can use `ssh-copy-id` to upload the key.
```
ssh-copy-id greene
```
After this, you should be able to connect without using your password (except to the gateway,
which does not support key-based authentication).

## Proxyjump

Due to the way the NYU HPC infrastructure is set up, we must connect to the gateway before
connecting to any other service (e.g. the greene cluster). Fortunately, ssh can automate
this for us through the `ProxyJump` configuration.
```
Host greene
    # Other configuration here
    # ...
    ProxyJump nyugateway
```
This configuration indicates that the to connect to `greene`, `ssh` should go through `nyugateway`.

## SSH connection multiplexing

One issue with the gateway is that unlike other hosts, it does not support key-based authentication.
This means that we must enter our password every time we connect.
We can partially bypass this issue by requesting ssh to keep a connection open, and route all other
connections through the existing one. This is called *connection multiplexing*, and is configured
through the `ControlMaster`/`ControlPath`/`ControlPersist` configuration.
```
Host nyugateway
    # Other configuration here
    # ...
    ControlPath ~/.ssh/.%r@%h:%p
    ControlMaster auto
    ControlPersist yes
```

## SSH Agent forwarding

When chaining SSH connections, it is necessary for us to be able to authenticate ourselves at each step.
One solution would be to enter a password at each step, which is very cumbersome.
Instead, we make use of key-based authentication, which keeps a secret file on our laptop through which we
can prove our identity. However, when we connect onwards, it is not desirable to keep this file at every location
we might connect from (due to in part, security reasons).
Instead, we use *agent forwarding* to forward the authentication requests all the way back to our laptop.
This can also be useful to connect to other services using ssh authentication such as Github.

```
Host nyugateway
    ForwardAgent yes

Host greene
    ForwardAgent yes
```

## SSH KeepAlive

In order to keep the connection from dropping after being inactive, you can instruct your ssh client
to send dummy packets to the server at a regular interval. Control this setting as follows:
```
Host *
    ServerAliveInterval 300
    ServerAliveCountMax 2
```
Here, `ServerAliveInterval` denotes the duration between the dummy packets in seconds.
