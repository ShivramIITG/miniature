#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller, Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from kubesim import KubeSim
# def tracefunc(frame, event, arg, indent=[0]):
#      if event == "call":
#          indent[0] += 2
#          print("-" * indent[0] + "> call function", frame.f_code.co_name)
#      elif event == "return":
#          print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
#          indent[0] -= 2
#      return tracefunc

# import sys
# sys.setprofile(tracefunc)


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


setLogLevel('debug')

net = KubeSim(controller=Controller)

info('*** Adding controller\n')
net.addController('c10')



defaultIP = '172.18.0.1/24'  # IP address for r0-eth1
router = net.addHost( 'r0', cls=LinuxRouter, ip=defaultIP )

s1, s2 = [ net.addSwitch( s ) for s in ('s1', 's2') ]

net.addLink( s1, router, intfName2='r0-eth1', params2={ 'ip' : defaultIP } )  # for clarity
net.addLink( s2, router, intfName2='r0-eth2', params2={ 'ip' : '172.18.3.1/24' } )

info('*** Adding docker containers\n')
net.addKubeCluster("test", config = "config/kind.yaml")
info('*** Adding docker container 1\n')
k1 = net.addKubeNode("test", "k1", role = "control-plane", type = "kind", custom_subnet="/24", defaultRoute='via 172.18.0.1')
info('*** Adding docker container 2\n')
k2 = net.addKubeNode("test", "k2", role = "worker", type = "kind", custom_ip="172.18.3.10/24", defaultRoute='via 172.18.3.1')
info('*** finished\n')


#d1 = net.addDocker('d1', ip='172.18.0.10', dimage="ubuntu:trusty")
#net.addKubeClusterConfig()

#info('*** Adding switches\n')
#s1 = net.addSwitch('s1')
#s2 = net.addSwitch('s2')
#s2 = net.addSwitch('s2')

info('*** Creating links\n')
net.addLink(k1, s1)
net.addLink(k2, s2)
#net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
#net.addLink(s1, k2)
#net.addLink(s1, d1)


info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([k1, k2])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
