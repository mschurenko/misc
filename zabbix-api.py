#!/usr/bin/python

import json
import requests
import sys
import subprocess
import getpass

url = 'http://monitor/zabbix/api_jsonrpc.php'
header = { 'content-type' : 'application/json' }
#hn = subprocess.Popen('hostname',stdout=subprocess.PIPE).stdout.read().split('.')[0]
group_id = '11'
template_id = '10077'
hn = 'rd06001'
domain = '.ie.dom'
ip = '10.65.7.1'
port = '10050'

sys.stdout.write('enter username: ')
user = sys.stdin.readline().strip()

pw = getpass.getpass()

auth_pl = { 'jsonrpc' : '2.0', 'method' : 'user.login', 'params' : { 'user' : user, 'password' : pw }, 'id' : 1 }

r = requests.post(url, data=json.dumps(auth_pl), headers=header)

ret = r.json()
if 'error' in ret:
  print 'login must have failed'
  print ret['error']
  sys.exit(1)

tok = r.json()['result']

hosts_pl = { 'jsonrpc' : '2.0', 'method' : 'host.exists', 'params' : { 'host' : hn }, 'auth' : tok, 'id' : 1 }
r = requests.post(url, data=json.dumps(hosts_pl), headers=header)

#print r.status_code
#print r.text

res = r.json()['result']
hostadd_pl = {
  'jsonrpc' : '2.0',
  'method' : 'host.create',
  'params' : {
    'host' : hn,
    'interfaces' : [
      {
        'type' : 1,
        'main' : 1,
        'useip' : 0,
        'dns' : hn + domain,
        'ip' : ip,
        'port' : port
      }
    ],
    'groups' : [
      {
        'groupid' : group_id
      }
    ],
    'templates' : [
      {
        'templateid' : template_id
      }
    ]
  },
  'auth' : tok,
  'id' : 1
}

#r = requests.post(url, data=json.dumps(hostadd_pl), headers=header)
#print r.text

if res == False:
  #print type(res)
  print 'result is false'
  # add host to group
  r = requests.post(url, data=json.dumps(hostadd_pl), headers=header)
  print r.text
else:
  print "host %s already exists!" % hn
