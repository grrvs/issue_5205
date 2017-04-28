#!/usr/bin/env python
# create hosts in icinga2 api

import sys
import os
import subprocess

"""
files to move / rename in order to 
	* clear all preconfigured hosts & services
	* keep icinga2.log nice & clean
"""
files = dict()
files['/etc/icinga2/conf.d'] = [
		'hosts.conf',
		'services.conf',
		'notifications.conf',
		'downtimes.conf',
		'satellite.conf',
		'additional_services.conf'
		]
files['/etc/icinga2/demo'] = [] # intentionally left empty

# web2 modules to deactivate for ease of UI, e.g. no errors in dashboard
web2modules = ['cube', 'director', 'businessprocess', 'globe' ]

def moveFiles(files, pattern = '.disabled'):
    if not isinstance(files, dict):
        print "sorry, files has to be a dict e.g { '/path/to/directory': 'file.name' }"
        sys.exit(0)
    for k, v in files.iteritems():
        if not k.endswith('/',1): # check for trailing slash, add it if missing
            k = k + '/'
        if not v: # empty list, assign all files as list to v
            try:
                dirfiles = os.listdir(k)
            except Exception as e:
                print e
                sys.exit(1)
            v = dirfiles

        if not isinstance(v, list):
            try:
                v = [v]; # make single file a list as well
            except Exception as e:
                print e
                sys.exit(1)

        if isinstance(v, list):
            for f in v:
                n = k + f # /path/to/ file
                # only concider existing files not already renamed
                if os.path.isfile(n) and not f.endswith(pattern, len(pattern)): 
                    try:
                        t = n + pattern	# target /path/to/file.pattern
                        os.rename(n,t)
                        print 'renamed %s\t->\t%s' % (n, t)
                    except Exception as e:
                        print e
                        sys.exit(1)
                elif os.path.isfile(n + pattern) or os.path.isfile(n): # file has already been renamed
                    print 'file was already renamed: %s' % n + pattern
                else:
                    print "ignored missing file %s" % n
        else:
                print "ooops, expected v to be a list, got %s" % type(v)

moveFiles(files)

if isinstance(web2modules, list):
    try:
        for m in web2modules:
            subprocess.call(['icingacli', 'module', 'disable', m])
    except Exception as e:
        print e
        sys.exit(1)

# nearly done, restart process
try:
    subprocess.call(['systemctl', 'restart', 'icinga2'])
    print "restarted icinga2"
except Exception as e:
    print e
    sys.exit(1)

print "setting up dependencies and nice to haves"

# install dependencies
try:
    subprocess.call(['yum', 'install', '-y', 'mysql-connector-python.noarch', 'python-requests.noarch'])
except Exception as e:
    print e
    sys.exit(1)

# not a dependency, but very nice
try:
    subprocess.call(['wget', 'https://dl.influxdata.com/telegraf/releases/telegraf-1.2.1.x86_64.rpm'])
    subprocess.call(['yum', 'localinstall', '-y', 'telegraf-1.2.1.x86_64.rpm'])
    subprocess.call(['cp', 'tlgrf.conf', '/etc/telegraf/telegraf.conf'])
    subprocess.call(['systemctl', 'restart', 'telegraf'])
except Exception as e:
    print e
    sys.exit(1)

try:
    import requests
    data = open('fancy_dashboard.json')
    r = requests.post(
     url='http://admin:admin@127.0.0.1:8004/api/dashboards/db',
     headers={'Content-Type': 'application/json;charset=UTF8'},
     data=data
    )
    print "fancy dashboard available - check grafana => mem_vs_api :)" 
except Exception as e:
    print e
    sys.exit(1)

print "all done - feel free to start\n> python check_for_issue.py\nor\n> python check_for_issue.py lazy\nfor edgy people"
