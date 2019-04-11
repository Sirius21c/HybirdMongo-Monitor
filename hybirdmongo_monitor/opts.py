from oslo_config import cfg
from prometheus_client import Gauge


auth_opts = [
    cfg.StrOpt('auth_url',
               default='',
               help=''),
    cfg.StrOpt('tenant_name',
               default='admin',
               help=''),
    cfg.StrOpt('username',
               default='admin',
               help=''),
    cfg.StrOpt('password',
               default='admin',
               help='')
]

target_opts = [
    cfg.StrOpt('hybirdmongo',
               default='',
               help=''),
    cfg.StrOpt('target',
               default='',
               help='')
]

CONF = cfg.CONF
CONF.register_opts(target_opts)
CONF.register_opts(auth_opts, group='auth')
CONF()

opcounter = Gauge('op_counters_total', 'Counting mongodb operations',
                  ['project', 'cluster', 'type'])
global_lock_queue = Gauge('global_lock_queue', '',
                    ['project', 'cluster', 'type'])
network = Gauge('network_total', '',
                    ['project', 'cluster', 'type'])
cursor = Gauge('cursor_total', '',
                    ['project', 'cluster', 'state'])
connection_current = Gauge('connection_current', '',
                    ['project', 'cluster'])
wiredtiger_cache = Gauge('wiredtiger_cache_bytes', '',
                    ['project', 'cluster', 'type'])


def list_opts():
    return [('DEFAULT', target_opts), ('auth', auth_opts)]
