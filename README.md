# issue_5205
how to replicate icinga2 issue #5205 

This works on the recent (as in 'see commit timestamp') single node icinga2 vagrant box.

As user root on the vagrant box:

> git clone https://github.com/grrvs/issue_5205.git
> cd issue_5205
> python prepare_environment.py # setup dependencies
> python check_for_issue.py # creates & deletes hosts / services over and over

wait and see - or just use the lazy mode
