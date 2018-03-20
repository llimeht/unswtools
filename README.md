# Python modules for automating website tasks

This module offers a rather ad hoc collection of tools for automating various
web tasks within one institution. If you're not a staff member at that
institution then there is probably nothing of interest here at all.

Authentication requires a file `.unsw_credentials` in your home directory.
The format for this file is `z1234567:mypassword`. If your password is stored
in plain text in this file, you should ensure that other users on the machine
do not have access to that file.

## Available tools

  * SSO login (for `myunsw` and `moodle`)
  * Jira login for use with the python `jira` module
  * Academic transcripts in PDF format
  * AIMS login and retrieval of course records

Authorisation of each transaction is still undertaken by the relevant web
service so if your user is not permitted to log into jira, you won't be
able to do so.


## Availability

Usage of these tools is governed by the terms of service of the web services
you may connect to and institutional policies.

The code itself is available under the MIT licence.
