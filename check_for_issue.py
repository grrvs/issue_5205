#!/usr/bin/env python

import sys
import time
import json
import subprocess

sys.path.append('/vagrant/mgervais/')

import icingadb
import icinga2api

db 	= icingadb.IcingaDb()
api = icinga2api.Icinga2Api()

"""
pattern for host and service, e.g. examplehost
BEWARE - do not change pattern without using a fresh the vagrant box
'orphaned' objects like 'the pattern from last try' might screw up this count of db objects
"""
host_pattern 	= 'examplehost'
service_pattern = 'seriouservice'

host_count    = 50
service_count = 20

if len(sys.argv) > 1 and sys.argv[1] == 'lazy':
    print "lazy mode, will reload icinga after every 10th run"
    me_so_lazy = True
else:
    me_so_lazy = False


# API selfcheck
api.apiCheck()
print "---"


run = 0
while True:
    start = time.time()
    run += 1
    print 'this is run %i' % run
    # get hosts known in API
    api_configured_hosts = api.rGet('/objects/hosts')
    api_configured_hosts = json.loads(api_configured_hosts.text)
    api_host_count = len(api_configured_hosts['results'])
    print 'found %i host(s) in API - deleting...' % api_host_count
    if api_host_count != 0:
        # try to delete all hosts by api with cascade=1
        for h in api_configured_hosts['results']:
            d = api.rDeleteHostCascade(h['name'])
            api_host_count -= 1
            sys.stdout.write("\r\t%i\thost(s) left" % api_host_count)
            sys.stdout.flush()
    print '\ndeleted %i host(s) from API' % len(api_configured_hosts['results'])



    # generate hosts & services
    print 'creating %i host(s) with %i service(s) each in API' % (host_count, service_count)
    api.genRandomHostsServices( host_pattern, host_count, service_pattern, service_count)

    # get hosts known in API
    api_configured_hosts = api.rGet('/objects/hosts')
    api_configured_hosts = json.loads(api_configured_hosts.text)
    # get services known in API
    api_configured_services = api.rGet('/objects/services')
    api_configured_services = json.loads(api_configured_services.text)
    api_object_count = len(api_configured_hosts['results']) + len(api_configured_services['results'])


    res = db.queryName1PatternIsActive(host_pattern + '%', 1)
    db_object_count = len(res)

    count = 0
    max_loops = 10
    print 'api says %i objects, icinga.icinga_objects reports %i' % (api_object_count, db_object_count)
    if api_object_count < db_object_count:
        print 'this is unexpected - there should not be more objects in icinga.icinga_objects than in API'
        print 'maybe clear the DB or just do `vagrant -f destroy && vagrant up`'
        sys.exit(1)
    while api_object_count != db_object_count:
        print "waiting for lost objects... "
        count += 1
        res = db.queryName1PatternIsActive(host_pattern + '%', 1)
        db_object_count = len(res)
        print "got %i objects in icinga.icinga_objects" % db_object_count	
        if api_object_count == db_object_count:
            continue
        if count < max_loops:
            sleep = count
            print "[%i/%i] sleep for %i second(s) for ido's grace" % (count, max_loops, sleep)
            time.sleep(sleep)
        elif count is max_loops:
            sleep = 90
            print "[extra] sleep for %i seconds for ido's grace" % sleep
            time.sleep(sleep)
        else:
            print 'finally, an error in run %i' % run
            print 'api says %i objects, icinga.icinga_objects reports %i' % (api_object_count, db_object_count)
            sys.exit(1)
    end = time.time()
    print 'all is good in just %s seconds' % (end - start)

    # feeling lazy? allright reload icinga2 every n run
    if run%10 == 0 and me_so_lazy:
        try: 
            subprocess.call(['systemctl', 'reload', 'icinga2'])
            print "this is run number %i - reloaded icinga2" % run
            time.sleep(2)
            api.apiCheck()
        except Exception as e:
            print e
            sys.exit(1)

    print "---"
