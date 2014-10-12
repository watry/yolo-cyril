import route
import time

import conn
import pub
import action


class topo(pub.OBJ):
	def __init__(self, data={}):
		self.data={
			'name':'default',
			'type':'topo',
			'route_list':[str(x) for x in range(1,1001)],
			'route_occupied_list':[False]*1000,
		}
		self.data.update(data)
		self.script_old     = {}
		self.path           = {}
		super(topo, self).__init__(self.data)

	def loadcfg(self, data):
		d = {
			'nodes':node,
			'ports':port,
			'fibs' :fib ,
		}
		for typ in data:
			for para in data[typ]:
				d[typ](para).register(self)
				# e.g. d['nodes']({'ip':1, 'name':'a'}).reg...

	def updateSta(self, show_instant=False):
		self.check(show_instant=show_instant)

	def listPhyLink_old(self, nodename):
		temp = self.queryList('n1_name', nodename) + self.queryList('n2_name', nodename)
		return [x.get('name') for x in temp]


	def makePath_old(self, name, A, Z):
		assert(name not in self.path)
		node_A = self.query(A)
		node_Z = self.query(Z)

		first_route = route.route(data={'topo':self, 'nodeA':A})

		if node_A==node_Z:
			return first_route

		potential_routes = [first_route]

		bestcost = 10000
		bestroute = None
		while(len(potential_routes)>0):
			this_route = potential_routes[0] # whose cost is least

			if this_route.cost > bestcost:
				break

			if this_route.getZ() == Z:
				bestcost = this_route.cost
				bestroute = this_route

			potential_routes.extend(this_route.grow_old())
			deleted_route = potential_routes.pop(0)
			deleted_route.destruct()
			del deleted_route
			potential_routes = sorted(potential_routes, key=lambda route:route.cost)

		if bestroute==None:
			return 1

		self.path[name] = bestroute
		return 0

	def makePath(self, A, Z):
		first_path = route.path(first_node_name = A)
		potential_paths = [first_path]
		best_path  = None

		affordable_cost   = 10000
		bestcost          = affordable_cost
		bestpath          = None

		while(len(potential_paths)>0):
			this_path = potential_paths.pop(0) # whose cost is least

			if this_path.cost > bestcost:
				break # bestpath better than rest
			if this_path.cost > affordable_cost:
				break # no suitable path

			if this_path.getEnd() == Z:
				del bestpath # then the mem is pointed to by no var, thus freed
				bestpath = this_path
				bestcost = this_path.cost

			potential_paths.extend(this_path.grow(topo_ref=self))
			potential_paths.sort(key=lambda path:path.cost)
		for x in potential_paths:
			del x

		return bestpath

	def realisePath_old(self, name):
		bestroute = self.path[name]
		if bestroute.isApplied:
			return 0
		if bestroute==None:
			return 1
		if bestroute.genScript_old('add')!=0:
			return 2
		for x in bestroute.script:
			if x not in self.script_old:
				self.script_old[x] = []
			self.script_old[x].extend(bestroute.script[x])
		bestroute.isApplied = True
		return 0

	def removePath(self, name):
		bestroute = self.path[name]
		if not bestroute.isApplied:
			return 10
		if name not in self.path:
			return 1
		if self.path[name].genScript('del')!=0:
			return 2
		for x in bestroute.script:
			if x not in self.script_old:
				self.script_old[x] = []
			self.script_old[x].extend(bestroute.script[x])
		bestroute.isApplied = False
		bestroute.destruct()
		del bestroute
		return 0
	def replacePath(self, model, target):
		pass
		target.destruct()
		target = copy.deepcopy(model)

	def getPath(self, name):
		if name in self.path:
			return self.path[name]
		return None

	def getComponentList(self, typ):
		return self.queryList('type', typ)


	def getScript(self, nodename):
		if nodename in self.script_old:
			return self.script_old[nodename]
		return []

	def showNodeScript(self, nodename):
		text = []
		node = self.query(nodename)
		for scripts_of_each_actions in node.genScript():
			for line in scripts_of_each_actions:
				text.append('| '+line)
		if len(text)>0:
			print '+--- '+nodename+' ---'
			for x in text:
				print x
		return 0

	def showScript(self, nodename=None):
		if nodename!=None:
			return showNodeScript(nodename)
		nodes = self.queryList('type', 'node')
		for each_node in nodes:
			self.showNodeScript(each_node.get('name'))
		return 0

	def showScript_old(self, nodename=None):
		if nodename!=None:
			print '+--- '+each_node.get(nodename)+' ---'
			for line in self.getScript(nodename=each_node.get('name')):
				print '|',
				print line
			return 0
		nodes = self.getComponentList('node')
		for each_node in nodes:
			print '+--- '+each_node.get('name')+' ---'
			for line in self.getScript(nodename=each_node.get('name')):
				print '|',
				print line
		return 0

	def distributeScript(self):
		num_err = 0
		nodes = self.queryList('type', 'node')
		for each_node in nodes:
			scripts = each_node.get('scripts')
			for each_action in scripts:
				n = each_action.apply()
				num_err += n
		return num_err


	def distributeScript_old(self):
		nodes = self.getComponentList('node')
		result = {}
		for each_node in nodes:
			result[each_node.get('name')] = each_node.runScript(self.getScript(each_node.get('name')))
			self.clearScript(each_node.get('name'))
		return 0

	def clearScript(self, nodename):
		if nodename in self.script_old:
			del self.script_old[nodename]
		return 0
	def genAction(self, act, route):
		vpn_seq = []

		x = 0
		while x<len(route.path)-1:
			this_ccc = [\
				route.nodepath[x+1],
				[route.path[x], 	route.path_reverse[x]],
				[route.path[x+1], 	route.path_reverse[x+1]],
			]
			vpn_seq.append(this_ccc)
			x+=1
		for x in vpn_seq:
			name_node = x[0]
			name_ingress = self.query(x[1][0]).get('n1_portname' if x[1][1] else 'n2_portname')
			name_egress  = self.query(x[2][0]).get('n2_portname' if x[2][1] else 'n1_portname') 


			content = {
				'type':		'port',
				'nodename':	name_node,
				'portname':	name_ingress,
			}
			self.genScript('add',content)
			content = {
				'type':		'port',
				'nodename':	name_node,
				'portname':	name_egress,
			}
			self.genScript('add',content)
			content = {
				'type':		'vpn',
				'nodename':	name_node,
				'port1name':	name_egress,
				'port2name':	name_egress,
			}
			self.genScript('add',content)
	def askfor(self, typ):
		if typ=='routeid':
			i=0
			for x in self.get('route_occupied_list'):
				if x==False:
					pub.dbg(10, 'find id:   '+self.get('route_list')[i])
					return self.get('route_list')[i]
				i+=1
			return None
		else:
			assert()
	def occupy(self, typ, content):
		if typ=='routeid':
			seq = self.get('route_list').index(content)
			self.get('route_occupied_list')[seq] = True
			pub.dbg(20, 'occpy id:  '+self.get('route_list')[seq])
		else:
			assert()
	def freeid(self, typ, content):
		if typ=='routeid':
			seq = self.get('route_list').index(content)
			self.get('route_occupied_list')[seq] = False
			pub.dbg(20, 'release id:'+self.get('route_list')[seq])
		else:
			assert()

	def isAvaiable(self, typ, name, loc=None):
		if typ=='node':
			n = self.query(name=name)
			return n.avaiable()
		if typ=='port':
			assert(loc!=None)
			return self.isPortAvaiable(name, loc)
		if typ=='fib':
			return self.isFibAvaiable(name)
		assert()

	def isPortAvaiable(self, name, loc):
		p = self.query(name=name, loc=loc)
		n = self.query(name=p.get('loc'))
		obj_str="interfaces/eth/"+p.get('name')
		if n.get('ip') == None: # virtual device
			return True
		session = conn.connection(n.get('ip'))
		if not session.ready():
			return False
		result = session.expect('show '+obj_str+' all', 'oper: up')
		session.close()
		return result

	def isFibAvaiable(self, name):
		p = self.query(name=name)
		if self.isPortAvaiable(p.get('n1_portname'), p.get('n1_name')):
			#print 111111111111111
			#print p.data
			#print (p.get('n2_portname'), p.get('n2_name'))
			#time.sleep(0.2)
			if self.isPortAvaiable(p.get('n2_portname'), p.get('n2_name')):
				return True
		return False



	def check(self, show_instant=False):
		#for each_node in self.getComponentList('node'):
		##	session = conn.connection(each_node.get('ip'))
		##	session.expect('get ccc/', 'admin')
		#	pass
		record = []
		for each_fib in self.getComponentList('fib'):
			record.append([each_fib.get('name')])
			if not self.isAvaiable('fib', each_fib.get('name')):
				record[-1].append('Fail')
				if each_fib.get('cost')<100000:
					each_fib.set('cost',each_fib.get('cost')+100000)
			else:
				record[-1].append('OK')
				if each_fib.get('cost')>=100000:
					each_fib.set('cost',each_fib.get('cost')-100000)
			if show_instant:
				print '{0}:{1}'.format(record[-1][0], record[-1][1])
		return 0



class node(pub.OBJ):
	def __init__(self,data={}):
		super(node, self).__init__(data=data)
		default_data={
			'name':'default',
			'type':'node',
			'scripts':[],
			'elan_list':[str(x) for x in range(1,101)],
			'elanoccupied_list':[False]*100,
			'action_list':[str(x) for x in range(1,101)],
			'action_occupied_list':[False]*100,
			'last_action_id' : 0
		}
		for x in default_data:
			if x not in self.data:
				self.data[x] = default_data[x]

	def genScript(self):
		result = []
		for x in self.get('scripts'):
			if not x.isApplied():
				result.append(x.getScript())
		return result
	def registerObserver(self, target):
		pub.dbg(6, 'reg {2:>10} {1:>10} <--- {0}'.format(target.get('name') ,self.get('name'), target.get('type')))
		if target.get('type')=='action':
			super(node, self).registerObserver( target)
			self.get('scripts').append(target)
			return 0
		if target.get('type')=='route':
			super(node, self).registerObserver( target)
			this_action = action.action(node=self, target=target)
			this_action.register(self)
			return 0
		assert() # no more type allowed

	def unregisterObserver(self, target):
		pub.dbg( 6, 'reg {2:>10} {1:>10} <-/- {0}'.format(target.get('name') ,self.get('name'), target.get('type')))
		if target.get('type')=='action':
			super(node, self).unregisterObserver( target)
			assert(target in self.get('scripts'))
			self.get('scripts').remove(target)
			if target.get('applied'):
				this_action = action.action(node=self, target=target)
				this_action.register(self)
			return 0

		if target.get('type')=='route':
			super(node, self).unregisterObserver( target)
			related_action_list = self.queryList_mc({'type':['action'], 'target':[target]})
			for x in related_action_list:
				x.unregister(self)
			return 0
		assert() # no more type allowed

	def askfor(self, typ):
		if typ=='elanid':
			i=0
			for x in self.get('elanoccupied_list'):
				if x==False:
					x=True
					return self.get('elan_list')[i]
				i+=1 
			return None
		if typ=='action_id':
			self.set('last_action_id', self.get('last_action_id')+1)
			return str(self.get('last_action_id'))
		else:
			assert()

	def askfor_old(self, typ):
		if typ=='elanid':
			i=0
			for x in self.get('elanoccupied_list'):
				session = conn.connection(self.get('ip'))
				if session.expect('get ccc/'+self.get('elan_list')[i]+' admin', 'down'):
					x=True
					continue
				if x==False:
					x=True
					return self.get('elan_list')[i]
				i+=1 
			return None
		if typ=='action_id':
			i=0
			for x in self.get('action_list'):
				if self.get('action_occupied_list')[i]==False:
					return self.get('elan_list')[i]
				i+=1
			return None
		else:
			assert()
	def occupy(self, typ, content):
		if typ=='elanid':
			seq = self.get('elan_list').index(content)
			self.get('elanoccupied_list')[seq] = True
		elif typ=='action_id':
			seq = self.get('action_list').index(content)
			self.get('action_occupied_list')[seq] = True
		else:
			assert()
	def freeid(self, typ, content):
		if typ=='elanid':
			seq = self.get('elan_list').index(content)
			self.get('elanoccupied_list')[seq] = False
		if typ=='action_id':
			seq = self.get('action_list').index(content)
			self.get('action_occupied_list')[seq] = False
		else:
			assert()
	def runScript(self, scripts):
		pub.dbg(21, 'connecting '+self.get('name')+' @ '+str(self.get('ip')))
		session = conn.connection(self.get('ip'))
		if session.ready():
			pub.dbg(25, 'writing '+self.get('name'))
			for x in scripts:
				pub.dbg(4,  '>>>'+x)
			return session.write(scripts)
		return 2
	def avaiable(self, obj_str=None):
		if self.get('ip') == None: # virtual device
			return True
		session = conn.connection(self.get('ip'))
		if not session.ready():
			return False
		if obj_str!=None:
			result = session.expect('get '+obj_str+' oper', 'up')
		session.close()
		return result




class port(pub.OBJ):
	def __init__(self,data={}):
		default_data={
			'name':'default',
			'type':'port',
		}
		super(port, self).__init__(data=data)
		for x in default_data:
			if x not in self.data:
				self.data[x] = default_data[x]



class fib(pub.OBJ):
	def __init__(self,data={}):
		default_data={
			'name':'default',
			'type':'fib',
		}
		super(fib, self).__init__(data=data)
		for x in default_data:
			if x not in self.data:
				self.data[x] = default_data[x]



