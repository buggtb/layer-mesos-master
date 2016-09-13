from charms.reactive import when, when_not, set_state
import charms.apt

mesos_directory="/opt/mesos"

@when_not('layer-mesos-master.installed')
def install_layer_mesos():
    charms.apt.queue_install(['mesos']) 
    set_state('layer-mesos-master.installed')
