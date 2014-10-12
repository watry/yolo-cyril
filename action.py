import pub
import re
import conn

class action(pub.OBJ):
	"""docstring for action"""
	def __init__(self, node, target):
		super(action, self).__init__()
		self.set('type', 'action')
		self.set('node', node)
		self.set('target', target)
		self.set('script', [])
		self.set('updated', False)
		self.set('applied', False)
		self.set('name', 'action_'+node.askfor('action_id'))

	def getScript(self):
		if self.get('updated')==False and self.get('applied')==False:
			self.makeScript(self)
		return self.get('script')
	def makeScript(self, act='add'):
		result = []
		if self.get('target').get('type')=='route':
			nodename   = self.get('node').get('name')
			path       = self.get('target').get('path')
			topo       = self.get('target').get('topo')

			l = len(path.fibpath)
			for i in xrange(l):
				if i==0 or i==l:
					continue # assume sink&source transmit pure data, thus need no cfg, like ixia, PC
				if path.nodepath[i]==nodename:
					f1_name       = path.fibpath[i-1]
					f1_isRevesred = path.fibpath_reverse[i-1]
					f2_name       = path.fibpath[i]
					f2_isRevesred = path.fibpath_reverse[i]

					name_ingress  = topo.query(f1_name).get('n1_portname' if f1_isRevesred else 'n2_portname')
					name_egress   = topo.query(f2_name).get('n2_portname' if f2_isRevesred else 'n1_portname')
					elanid = self.get('node').askfor('elanid')
					result.extend([\
						"delete interfaces/eth/"+name_ingress+" 1",
						"delete interfaces/eth/"+name_egress +" 1",
						"delete ccc "+elanid,
						"create interfaces/eth/"+name_ingress+" 1 {mode='port',qos='vlanpriabc'}",
						"create interfaces/eth/"+name_egress +" 1 {mode='port',qos='vlanpriabc'}",
						"create ccc "+elanid,
						"create interfaces/eth/"+name_ingress+"/1 service {_='ccc',vpn='ccc/"+elanid+"'}",
						"create interfaces/eth/"+name_egress +"/1 service {_='ccc',vpn='ccc/"+elanid+"'}",
						])
		elif self.get('target').get('type')=='action':
			t_action = self.get('target')
			assert( t_action.get('applied'))
			for line in t_action.get('script'):
				sep = line.split(' ', 3)
				if sep[0] in ['cr', 'cre', 'crea', 'creat', 'create']:
					result.append('{0} {1} {2}'.format('delete', sep[1], sep[2]))
				elif sep[0] in ['se', 'set']:
					result.append('{0} {1} {2}'.format('unset', sep[1], sep[2]))
			self.set('script', result)
			self.set('updated', True)
		else:
			result.append('unknown {0} @ {1}'.format(self.get('target').get('name'),self.get('node').get('name')))
		
		self.set('script', result)
		self.set('updated', True)
		return 0
	def apply(self):
		if self.get('node').get('ip')==None: # virtual node
			return 0
		session = conn.connection(self.get('node').get('ip'))
		if not session.ready():
			return 1
		scripts = self.getScript()
		num_err = session.mwrite(scripts)

		self.set('applied', True)
		return num_err
	def isApplied(self):
		return self.get('applied')
		


class action_old1(pub.OBJ):
	"""docstring for action"""
	def __init__(self, target, loc):
		super(action, self).__init__()
		self.set('type', 'action')
		self.set('target', target)
		self.set('loc', loc)
		
		self.script = []
		self.loc    = self.get('loc')
		self.target = None
		self.existed= False

	def genScript(self, topo):
		if self.target.get('type') == 'route':
			if self.existed:
				return self.addRoute(topo)
			else:
				return self.delRoute(topo)
		assert()

	def addRoute(self, topo):
		result = []

		if topo.query(self.target).get('path')==None:
			return result

		i = -1
		nodelist = topo.query(self.target).get('path').getNodeList()
		for x in nodelist:
			i += 1

			if x==self.loc:
				name_ingress = topo.query(self.target).get('n1_portname')
				name_egress  = topo.query(self.target).get('n2_portname')
				elanid = self.loc.getId(self.target)

		result.extend([\
			"delete interfaces/eth/"+name_ingress+" 1 ",
			"delete interfaces/eth/"+name_egress +" 1 ",
			"create interfaces/eth/"+name_ingress+" 1 {mode='port',qos='vlanpriabc'}",
			"create interfaces/eth/"+name_egress +" 1 {mode='port',qos='vlanpriabc'}",
			"create ccc "+elanid,
			"create interfaces/eth/"+name_ingress+"/1 service {_='ccc',vpn='ccc/"+elanid+"'}",
			"create interfaces/eth/"+name_egress +"/1 service {_='ccc',vpn='ccc/"+elanid+"'}",
			])

		return result


	def delRoute(self, topo):
		result = []
		return result

