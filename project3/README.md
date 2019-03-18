# Linux Server Configuration

### Overview

This project takes a baseline installation of a Linux distribution on a virtual
machine and prepares it to host a web application by installing updates,
securing it from a number of attack vectors, and installing/configuring web and
database servers.

### HTTP

The web application,
[The Fungus Among Us](https://github.com/ozlop/udacity-full-stack-nanodegree/tree/master/project2)
, is hosted via HTTP at the server's IP address:
[54.185.191.122](http://54.185.191.122/).

### SSH

To gain entry into the server, one can SSH into the server by executing the
command:

```
ssh -p 2200 -i [RSA_FILE] grader@54.185.191.122
```

### Deployment Summary

#### Software
- Database Engine: PostgresQL
- WSGI: MOD WSGI
- Web Server: Apache
