# Project: Catalog

# The Fungus Among Us

Join a worldwide team in our attempt to further scientific development in the
the field of fungal studies. By cataloging our every day encounters with fungus
fruiting in the wild we are creating a data store that can be used to track
the spread and determine the origin of fungus species.

<picture>

## Requirements
Virtual Box, a virtualization technology, and Vagrant, a virtual environment
management tool, must be installed to spin up a virtual instance containing the
web server database used in this project.


### Virtual Box
Download and install [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
using instructions applicable to your environment.

### Vagrant
[Download](https://www.vagrantup.com/downloads.html) and
[Install](https://www.vagrantup.com/docs/installation/) Vagrant.

:exclamation: Extra
[configuration](https://www.vagrantup.com/docs/other/wsl.html) is required to
get Vagrant running in Windows 10 WSL
<br>
<br>

## Setup
### Virtual Machine
#### Configuration Files
Clone the Relational Databases and Full Stack Fundamentals courses virtual
machine code from official Udacity github repository
[here](https://github.com/udacity/fullstack-nanodegree-vm).

*The remaining steps will occur within the directory structure of the files held
in the repository. Any references to a `/` or `root` directory indicate the
base directory of this folder structure*

#### Spin it Up
From the `root` directory of the Fullstack VM, change into the `vagrant` directory containing the VM configuration file and run the Vagrant command `up` to initiate the virtual machine.
```
cd /vagrant
vagrant up
```
<br>

Open a connection with the VM once it is fully configured and booted using
Vagrant's `ssh` command.
```
vagrant ssh
```
<br>

You will be greeted with a shell prompt within the VM environment if the all
goes well.
```
vagrant@vagrant:~$
```
<br>

Log out of the VM shell
```
exit
```
<br>


## How to Run
Download the files from this repository and move them to your Host machine's
`/vagrant` directory, they may now be run from the VM.

Create Client OAuth2 credentials file within the same directory and add your
google web application OAuth2 Application ID and Application Secret.
client_secrets.json
```
{
  "web": {
    "app_id": "<Application ID",
    "app_secret": "<Application Secret>"
  }
}
```

```
# Host Shell
cd /vagrant
vagrant up
ssh vagrant
```
```
# Vagrant Shell
cd /vagrant

# Setup Database
python database_setup.py

# Load Database data
python fungusload.py

# Start Web Server
python fungusamongus.py
```

Once the web server is running, the application can be accessed at
`localhost:5000` using a web browser.
