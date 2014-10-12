import copy
import pub

class path(object):
	def __init__(self, first_node_name):
		self.nodepath = [first_node_name]
		self.fibpath  = []
		self.fibpath_reverse = []
		self.cost = 0

	def getFirst(self):
		return self.nodepath[-1]

	def getEnd(self):
		return self.nodepath[-1]

	def getEndFib(self):
		if len(self.fibpath)==0:
			return None
		return self.fibpath[-1]

	def getNodeList(self):
		return self.nodepath

	def getFibList(self):
		return self.fibpath

	def getFibDirList(self):
		return self.fibpath_reverse


	def copy(self, target):
		self.nodepath        = copy.copy(target.nodepath)
		self.fibpath         = copy.copy(target.fibpath)
		self.fibpath_reverse = copy.copy(target.fibpath_reverse)
		self.cost            = target.cost

	def attach(self, node_name, fib_name, fib_is_reversed, cost):
		self.nodepath.append(node_name)
		self.fibpath.append(fib_name)
		self.fibpath_reverse.append(fib_is_reversed)
		self.cost += cost


	def grow(self, topo_ref):
		result = []
		temp = {'n1_name':[self.getEnd()], 'type':['fib']}
		possible_fib = topo_ref.queryList_mc(temp)
		if self.getEndFib() in possible_fib:
			possible_fib.remove(self.getEndFib())

		for this_fib in possible_fib:
			new_path = path(first_node_name=self.getFirst())
			new_path.copy(self)

			node_name       = this_fib.get('n2_name')
			fib_name        = this_fib.get('name')
			fib_is_reversed = False
			cost            = this_fib.get('cost')
			new_path.attach(node_name, fib_name, fib_is_reversed, cost)

			result.append(new_path)

		temp = {'n2_name':[self.getEnd()], 'type':['fib']}
		possible_fib = topo_ref.queryList_mc(temp)
		if self.getEndFib() in possible_fib:
			possible_fib.remove(self.getEndFib())

		for this_fib in possible_fib:
			new_path = path(first_node_name=self.getFirst())
			new_path.copy(self)

			node_name       = this_fib.get('n1_name')
			fib_name        = this_fib.get('name')
			fib_is_reversed = True
			cost            = this_fib.get('cost')
			new_path.attach(node_name, fib_name, fib_is_reversed, cost)

			result.append(new_path)
		return result

	def equal(self, target_path):
		if target_path==None:
			return False
		if self.nodepath != target_path.nodepath:
			return False
		if self.fibpath != target_path.fibpath:
			return False
		if self.fibpath_reverse != target_path.fibpath_reverse:
			return False
		return True

	def show(self):
		i = 0
		while i<len(self.getFibList()):
			print '{:>10} +'.format(self.getNodeList()[i])
			print ' '*10+' |  '+self.getFibList()[i]+ ('(rev)' if self.getFibDirList()[i] else '')
			i+=1
		print '{:>10} +'.format(self.getNodeList()[i])

class route(pub.OBJ):
	def __init__(self, data):
		super(route, self).__init__(data)
		topo  = self.get('topo')
		nodeA = self.get('nodeA')
		self.set('path', None)
		self.set('cost', None)
		self.set('type', 'route')


		self.set('name', topo.askfor('routeid')) #replaced...
		self.name = self.get('name')

		topo.occupy('routeid', self.name)

		self.topo = topo
		self.path = []
		self.elanid = []
		self.path_reverse = []
		self.phylink_obj_list = []

		self.script = {}
		self.A = nodeA
		self.Z = nodeA
		self.nodepath = [nodeA]
		self.cost = 0
		self.isApplied = False


	def copy(self, target):
		self.topo             = copy.deepcopy(target.topo             )
		self.path             = copy.deepcopy(target.path             )
		self.elanid           = copy.deepcopy(target.elanid           )
		self.path_reverse     = copy.deepcopy(target.path_reverse     )
		self.phylink_obj_list = copy.deepcopy(target.phylink_obj_list )
		self.script           = copy.deepcopy(target.script           )
		self.A                = copy.deepcopy(target.A                )
		self.Z                = copy.deepcopy(target.Z                )
		self.nodepath         = copy.deepcopy(target.nodepath         )
		self.cost             = copy.deepcopy(target.cost             )

	def attach(self, phylink_name):
		phylink_obj = self.topo.query(phylink_name)
		
		if self.Z == phylink_obj.get('n1_name'):
			self.Z = phylink_obj.get('n2_name')
			reverse = False
		elif self.Z == phylink_obj.get('n2_name'):
			self.Z = phylink_obj.get('n1_name')
			reverse = True
		self.nodepath.append(self.Z)
		self.path.append(phylink_name)
		self.path_reverse.append(reverse)
		self.cost += phylink_obj.get('cost')

	def destruct(self):
		pub.dbg(30, "del_route: "+self.name+' - '+str(self.path))
		for phylink_obj in self.phylink_obj_list:
			self.unregister(phylink_obj)
		self.topo.freeid('routeid', self.name)
		#del self.topo.path[self.toponame]
		del self
		
	def grow_old(self):
		result = []
		for this_phy_link in self.topo.listPhyLink_old(self.getZ()):
			if this_phy_link == self.getLastPhyLink():
				continue

			new_route      = route(data={'topo':self.topo, 'nodeA':self.A})
			new_route.copy(self)
			new_route.attach(this_phy_link)
			pub.dbg(30, "new_route: "+new_route.name+' - '+str(new_route.path))

			result.append(new_route)
		return result

	def getLastPhyLink(self):
		if self.path == []:
			return None
		return self.path[-1]

	def getZ(self):
		assert(self.Z != None)
		return self.Z

	def getScript_old(self, nodename):
		if nodename in self.script:
			return self.script_old[nodename]
		return []
	def genScript_old(self, act):
		vpn_seq = []
		x = 0
		while x<len(self.path)-1:
			this_ccc = [\
				self.nodepath[x+1],
				[self.path[x],   self.path_reverse[x]  ],
				[self.path[x+1], self.path_reverse[x+1]],
			]
			vpn_seq.append(this_ccc)
			x+=1
		for x in vpn_seq:
			name_node = x[0]
			name_ingress = self.topo.query(x[1][0]).get('n1_portname' if x[1][1] else 'n2_portname')
			name_egress  = self.topo.query(x[2][0]).get('n2_portname' if x[2][1] else 'n1_portname') 
			this_node = self.topo.query(x[0])
			if this_node not in self.script:
				self.script[x[0]] = []

			if act=='add':
				elanid = this_node.askfor('elanid')
				assert(elanid!=None)
				self.script[x[0]].extend([\
					"delete interfaces/eth/"+name_ingress+" 1 ",
					"delete interfaces/eth/"+name_egress +" 1 ",
					"create interfaces/eth/"+name_ingress+" 1 {mode='port',qos='vlanpriabc'}",
					"create interfaces/eth/"+name_egress +" 1 {mode='port',qos='vlanpriabc'}",
					"create ccc "+elanid,
					"create interfaces/eth/"+name_ingress+"/1 service {_='ccc',vpn='ccc/"+elanid+"'}",
					"create interfaces/eth/"+name_egress +"/1 service {_='ccc',vpn='ccc/"+elanid+"'}",
					])
				this_node.occupy('elanid', elanid)
				self.elanid.append(elanid)

			if act=='del':
				elanid = self.elanid.pop(0)
				assert(elanid!=None)
				self.script[x[0]].extend([\
					"del interfaces/eth/"+name_ingress+" 1",
					"del interfaces/eth/"+name_egress+" 1",
					"del ccc "+elanid,
					])
				this_node.freeid('elanid', elanid)
		return 0

	def findPath(self):
		p = self.get('topo').makePath(A=self.get('nodeA'), Z=self.get('nodeZ'))
		if not p.equal(self.get('path')):
			self.adoptPath(p)
			return True
		return False

	def adoptPath(self, path):
		if self.get('path') != None:
			for each_node in set(self.get('path').getNodeList()):
				self.unregister(self.get('topo').query(each_node))
		self.set('path', path) # previous one not destructed, leaking?
		if self.get('path')!=None:
			self.set('cost', path.cost)
			for each_node in set(self.get('path').getNodeList()):
				self.register(self.get('topo').query(each_node))
		return 0
