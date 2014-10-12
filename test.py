#import ethport
import time
import os

import topo
import route
import cfg



t = topo.topo()
print '===load topo==='
t.loadcfg(cfg.topo_data_dic)



print '----- TEST 1 -------'
print '===find path==='
node_A   = 'v1'
node_Z   = 'v2'
planned_route = {
	'topo':t,
	'nodeA':node_A,
	'nodeZ':node_Z,
	}

r = route.route(data=planned_route)
r.findPath()
print 'cost=%d' % r.get('cost')
t.showScript()

num_err = t.distributeScript()
if num_err==0:
	print "Success."
else:
	print "{0} errors happened.".format(num_err)



print '----- TEST 2 -------'
(fib, cost) = ('f2', 5)
print '{0}.cost <- {1}:'.format(fib, cost)
t.query(fib).set('cost', cost)
r.findPath()
print 'cost=%d' % r.get('cost')
t.showScript()




print '----- TEST 3 -------'
while True:
	time.sleep(3)
	t.updateSta()

	if r.findPath():
		print 'new path: cost=%d' % r.get('cost')
		t.showScript()
		print 'Distributing...',
		num_err = t.distributeScript()
		if num_err==0:
			print "success."
		else:
			print "{0} errors.".format(num_err)
	else:
		print 'all right'


print '----- TEST OVER -----'

