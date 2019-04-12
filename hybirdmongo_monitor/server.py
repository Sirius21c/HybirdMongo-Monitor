import json
import requests
import time

from keystoneauth1 import identity
from keystoneauth1 import session as auth_session
from oslo_config import cfg
from prometheus_client import start_http_server, Gauge

import opts


CONF = cfg.CONF

def main():

    hybirdmongo = CONF.hybirdmongo
    target = json.loads(CONF.target)
    token = get_token()
    headers = {'X-Auth-Token': token}

    while True:
        for project in target.keys():
            for cluster in target[project]:
                url = '%s/%s/clusters/%s/status' % (hybirdmongo, project, cluster)

                try:
                    result = requests.get(url, headers=headers)

                    if result.text == 'Authentication required':
                        token = get_token()
                        headers = {'X-Auth-Token': token}
                        result = requests.get(url, headers=headers)
                    assert result.status_code == 200
                except:
                    pass

                text = json.loads(result.text)
                assign_metrics(text, project, cluster)

        time.sleep(10)

def get_token():
    username = CONF.auth.username
    password = CONF.auth.password
    tenant_name = CONF.auth.tenant_name
    auth_url = CONF.auth.auth_url

    auth = identity.Password(username=username,
                             password=password,
                             tenant_name=tenant_name,
                             auth_url=auth_url)
    session = auth_session.Session(auth=auth)
    token = session.get_token()
    return token

def assign_metrics(text, project, cluster):
    status = text['status']
    op = status['opcounter']
    glq = status['global_lock_queue']
    net = status['network']
    cursor = status['cursor']
    conn = status['connection']['current']
    wc = status['wiredTiger_cache']

    opts.opcounter.labels(project, cluster, 'getmore').set(op['getmore'])
    opts.opcounter.labels(project, cluster, 'insert').set(op['insert'])
    opts.opcounter.labels(project, cluster, 'update').set(op['update'])
    opts.opcounter.labels(project, cluster, 'command').set(op['command'])
    opts.opcounter.labels(project, cluster, 'query').set(op['query'])
    opts.opcounter.labels(project, cluster, 'delete').set(op['delete'])

    if glq :
        opts.global_lock_queue.labels(project, cluster, 'total').set(glq['total'])
        opts.global_lock_queue.labels(project, cluster, 'writers').set(glq['writers'])
        opts.global_lock_queue.labels(project, cluster, 'readers').set(glq['readers'])
    else:
        opts.global_lock_queue.labels(project, cluster, 'total').set(-1)
        opts.global_lock_queue.labels(project, cluster, 'writers').set(-1)
        opts.global_lock_queue.labels(project, cluster, 'readers').set(-1)

    opts.network.labels(project, cluster, 'net_in').set(net['net_in'])
    opts.network.labels(project, cluster, 'net_out').set(net['net_out'])
    opts.network.labels(project, cluster, 'net_request').set(net['net_request'])

    opts.cursor.labels(project, cluster, 'open').set(cursor['open'])
    opts.cursor.labels(project, cluster, 'timeout').set(cursor['timeout'])

    opts.connection_current.labels(project, cluster).set(conn)

    if wc :
        opts.wiredtiger_cache.labels(project, cluster, 'read').set(wc['read'])
        opts.wiredtiger_cache.labels(project, cluster, 'write').set(wc['write'])
        opts.wiredtiger_cache.labels(project, cluster, 'config_max').set(wc['config_max'])
    else:
        opts.wiredtiger_cache.labels(project, cluster, 'read').set(-1)
        opts.wiredtiger_cache.labels(project, cluster, 'write').set(-1)
        opts.wiredtiger_cache.labels(project, cluster, 'config_max').set(-1)
