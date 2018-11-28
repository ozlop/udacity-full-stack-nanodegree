# Project: Logs Analysis
The Logs Analysis project is design to simulate a real-world scenario in which
interaction with a live database housing a website's user access log and content
information is required to generate use statistics.

Prompt:
```
You've been hired onto a team working on a newspaper site. The user-facing
newspaper site frontend itself, and the database behind it, are already built
and running. You've been asked to build an internal reporting tool that will use
information from the database to discover what kind of articles the site's
readers like.

The database contains newspaper articles, as well as the web server log for the
site. The log has a database row for each time a reader loaded a web page. Using
that information, your code will answer questions about the site's user
activity.
```

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


### Database
#### Data
[Download](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)
the news website database data and unzip it in the `vagrant` directory.
```
wget
https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip
mv newsdate.zip /vagrant
unzip /vagrant/newsdata.zip && rm /vagrant/newsdata.zip
```
<br>

Vagrant allows sharing of the `vagrant` directory between the Host environment
and VM environment; any files placed in the `vagrant` on the Host machine will
be accessible within the VM in the `/vagrant` directory.

Log into the VM and change into the `/vagrant` directory to load the database
information into the existing PostgreSQL instance (this was installed on the VM
during initialization)
```
# Host Shell
cd vagrant/
vagrant up # The two steps are not required if the VM is already running
ssh vagrant

# Vagrant Shell
cd /vagrant
psql -d news -f newsdata.sql
```
<br>

Verify the news website database is loaded into the server instance by accessing
PostgreSQL using the CLI tool `psql`.
```
psql -d news
```
From within the `psql` command prompt run `\dt` and verify all the necessary
tables were loaded into the news database.
```
\dt

       List of relations
Schema |   Name   | Type  |  Owner
--------+----------+-------+---------
public | articles | table | vagrant
public | authors  | table | vagrant
public | log      | table | vagrant
(3 rows)

```
<br>
<br>


## How to Run
Download the files from this repository and move them to your Host machine's
`/vagrant` directory, they may now be run from the VM.
```
# Host Shell
cd /vagrant
vagrant up
ssh vagrant

# Vagrant Shell
cd /vagrant
python news_reports.py
```

You will be presented with the following statistics from the news website:
1. The top three articles with the most views
2. The top three authors with the most views
3. Any days where requests to the website resulted in an error rate above 1%

Enjoy!
