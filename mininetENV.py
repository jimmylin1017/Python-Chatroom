#!/usr/bin/python
#try to use mininet bind two private directory to test server-client program

from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import setLogLevel, info, debug
from functools import partial

"Single Switch Topology with Private Directory"

class myHost(Host):
	def __init__(self, name, ip, mount, *args, **kwargs):
		Host.__init__(self, name, ip=ip, privateDirs=mount, *args, **kwargs)

	def config(self, **kwargs):
		Host.config(self, **kwargs)

		#debug("cd to path %s" % self.path)

		#self.cmd('source %s' % 'cdcmd')


class myTopo( Topo ):
	def build( self, count=3 ):
		#hosts = [ self.addHost( 'h%d' % i , privateDirs = [ ( '~/mininetHost', '~/mininetHost/%d' %i ) ] )
		#		  for i in range( 1, count + 1 ) ]

		s1 = self.addSwitch( 's1' )

		for i in range(1, count+1):
			name = 'h%s' % i
            
			host = self.addHost(name , cls=myHost, 
								ip='192.168.1.%s/24' % i,
								mount=[ ( '~/mininetHost', '~/mininetHost/%s' %i ) ])

			self.addLink( host, s1 )



topos = { 'pDirTopo' : myTopo }

if __name__ == '__main__':
	setLogLevel( 'info' )
	net = Mininet( topo=myTopo( count = 10 ) )
	net.start()
	CLI( net )