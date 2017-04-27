#!/usr/bin/env python
# create hosts in icinga2 api

import requests
import json
import sys
import time

# disable insecure ssl warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# obviously vagrant
API_USER = 'root'
API_PASS = 'icinga'
API_HOST = '192.168.33.5'

# obviously obvious
base_url = 'https://' + API_HOST + ':5665/v1'
r_header = {'Accept': 'application/json'}

# sleep interval
sleep_interval = 5

class Icinga2Api(object):
    # get stuff from API
    def rGet(self, uri):
        try:
            r = requests.get(
                    base_url + uri,
                    auth		= (API_USER, API_PASS),
                    headers	= r_header,
                    verify	= False)
        except Exception as e:
            print e
            sys.exit(1)
        return r

    # put stuff to API
    def rPut(self, uri, payload = None):
        try:
            r = requests.put(
                base_url + uri,
                auth=(API_USER, API_PASS),
                headers=r_header,
                data=json.dumps(payload),
                verify=False)
        except Exception as e:
            print e
            sys.exit(1)

        return r

    # delete stuff from API
    def rDelete(self, uri):
        try:
            r = requests.delete(
                    base_url + uri,
                    auth=(API_USER, API_PASS),
                    headers=r_header,
                    verify=False)
        except Exception as e:
            print e
            sys.exit(1)
        return r

    def createHost(self, host):
        data = { "attrs": { "address": "127.0.0.1", "check_command": "dummy" } }
        r = self.rPut('/objects/hosts/' + host, data)
        if r.status_code != 200:
            print r.text
            sys.exit(1)
        return r

    def createService(self, host, service):
        data = { "templates":[ "generic-service" ],"attrs": { "display_name": service , "check_command" : "dummy", "host_name": host } }
        r = self.rPut('/objects/services/' + host + '!' + service, data)
        if r.status_code != 200:
            print r.text
            sys.exit(1)
        return r

    def rDeleteHostCascade(self, host):
        r = self.rDelete('/objects/hosts/' + host + '?cascade=1')
        if r.status_code != 200:
            print r.text
            sys.exit(1)
        return r

    def apiCheck(self):
        # check if API is working
        api_test = self.rGet('/status')
        if api_test.status_code != 200:
            print "ooops, the API got sour"
            print api_test.text
            sys.exit(1)
        else:
            print "API alive"

    def genRandomHostsServices(self, hn = 'host', hc = 10, sn = 'service', sc = 10):
        """
        this generates hosts & services: 
        * hn -> static part of hostname to generate
        * hc -> number of hosts to generate
        * sn -> static part of servicename to generate
        * sc -> number of services to generate
        """
        lc = 0
        for i in range(1, hc+1): # generate random hosts
            lc += 1
            ht = hn + str(i).zfill(4) # fill i with zeroes
            self.createHost(ht)
            for k in range(1, sc+1): # generate random hosts
                lc += 1
                st = sn + str(k).zfill(4) # fill k with zeroes
                self.createService(ht, st)
            sys.stdout.write("\r\t%i\tof %i host(s) created" % (i, hc))
            sys.stdout.flush()
        sys.stdout.write("\n")
        print 'created all in all %i hosts with %i services each' % (hc, sc)
