#!/usr/bin/python

# bulk add render nodes to Renderfarm zabbix group and link them to Template_Render_Blade template
# batch_file should be a list of render node host names (eg: rd06001) one on each line

import json
import requests
import sys
import subprocess
import getpass

url = 'http://monitor/zabbix/api_jsonrpc.php'
header = { 'content-type' : 'application/json' }
group_id = '11'
template_id = '10077'
domain = '.ie.dom'
ip = '10.65.7.1'
port = '10050'
batch_file = ''

try:
  batch_file = sys.argv[1]
except:
  print 'usage: %s <batch file>' % sys.argv[0]

try:
  hosts = open(batch_file, 'r')
except:
  print '%s not found' % batch_file
  sys.exit(2)

# functions
def zabbix_auth():
  sys.stdout.write('enter zabbix username: ')
  user = sys.stdin.readline().strip()
  pw = getpass.getpass('enter zabbix password: ')
  
  auth_pl = { 'jsonrpc' : '2.0', 'method' : 'user.login', 'params' : { 'user' : user, 'password' : pw }, 'id' : 1 }
  r = requests.post(url, data=json.dumps(auth_pl), headers=header)
  ret = r.json()
  if 'error' in ret:
    return 'login must have failed'
  else:
    return ret['result']

def host_add(hn,ip,tok):
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

  # check if host exists
  hosts_pl = { 'jsonrpc' : '2.0', 'method' : 'host.exists', 'params' : { 'host' : hn }, 'auth' : tok, 'id' : 1 }
  r = requests.post(url, data=json.dumps(hosts_pl), headers=header)
  res = r.json()['result']

  if res == False:
    r = requests.post(url, data=json.dumps(hostadd_pl), headers=header)
    return r.text
    #return '%s does not exists' % hn  
  else:
    return '%s already exists' % hn  

# main
tok = zabbix_auth()
if tok.startswith('login'):
  print tok
  sys.exit(1) 

for host in hosts: 
  host = host.strip()
  ip = subprocess.Popen(['host',host],stdout=subprocess.PIPE).stdout.read().split()[-1]
  ret = host_add(host,ip,tok)
  print ret
