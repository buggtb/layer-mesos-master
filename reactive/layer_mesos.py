from charms.reactive import when, when_not, set_state
import charms.apt
from charmhelpers.core.hookenv import status_set, log, resource_get
from subprocess import check_call, CalledProcessError, call, check_output, Popen
from charmhelpers.core import hookenv
from charms.reactive.helpers import data_changed
from charmhelpers.core.host import service_restart

mesos_directory="/opt/mesos"

@when_not('layer-mesos-master.installed')
def install_layer_mesos():
    charms.apt.queue_install(['mesos']) 
    set_state('layer-mesos-master.installed')
    status_set('waiting', 'Apache Mesos Installed, Awaiting Configuration')



@when('zookeeper.joined')
@when_not('zookeeper.ready')
def wait_for_zookeeper(zookeeper):
    """
         We always run in Distributed mode, so wait for Zookeeper to become available.
    """
    hookenv.status_set('waiting', 'Waiting for Zookeeper to become available')


@when('zookeeper.ready')
@when_not('mesos.configured')
def configure(zookeeper):
    """
        Configure Zookeeper for the first time.
        This will set memory limits. By default we use a % model for memory calculations.
        This allows us to automatically scale the drillbit depending on where it is installed.
    """
    status_set('maintenance', 'Configuring Apache Mesos')
    write_zk_file(zookeeper)
    start_mesos()
    hookenv.open_port('5050')
    set_state('mesos.configured')
    status_set('active', 'Apache Mesos up and running')

def write_zk_file(zookeeper):
    """
        Write the ZK details to disk.
    """
    zklist = ''
    for zk_unit in zookeeper.zookeepers():
        zklist += add_zookeeper(zk_unit['host'], zk_unit['port'])
    zklist = zklist[:-1]
    t = simple_template(zklist)
    text_file = open("/etc/mesos/zk", "w")
    text_file.write(t)
    text_file.close()

def add_zookeeper(host, port):
    """
        Return a ZK hostline for the config.
    """
    return host+':'+port+','

def simple_template(zk):
    """
        Return a drill exec line for Drill configuration. This creates an entry in ZK.
    """
    return 'zk://'+zk+'/mesos'

def start_mesos():
    service_restart('mesos-master')
    status_set('active', 'Apache Mesos up and running.')
    set_state('mesos.running')

