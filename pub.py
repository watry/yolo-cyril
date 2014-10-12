import time

debug_level=0111

def dbg(lv,content,forewords=''):
	if lv>=debug_level:
		print forewords+content


class OBJ(object):
	def __init__(self,data={}):
		self.observer = []
		self.observer_dic = {}
		self.observer_rdic = {}
		self.data={}
		self.load(data)

	def load(self, data):
		for x in data:
			self.data[x] = data[x]

	def show(self):
		for x in self.observer:
			print x.data

	def set(self, vname, value):
		self.data[vname] = value

	def get(self, vname, value_if_unexisted=None):
		if vname not in self.data:
			return value_if_unexisted
		return self.data[vname]

	def register(self, target):
		target.registerObserver(self)

	def unregister(self, target):
		dbg(1, target.__class__.__name__+' <-/- '+self.__class__.__name__)
		target.unregisterObserver(self)

	def _makeName(self, target):
		#assert() #defined by themselves
		return target.get('loc', '') + '_' + target.get('name')

	def _getName(self, target, value_if_unexisted=None):
		if target not in self.observer_rdic:
			return value_if_unexisted
		return self.observer_rdic[target]

	def _occupyName(self, name, target):
		assert(name not in self.observer_dic)
		assert(target not in self.observer_rdic)
		self.observer_dic[name]    = target
		self.observer_rdic[target] = name

	def _freeName(self, name, target):
		assert(name in self.observer_dic)
		assert(target in self.observer_rdic)
		del self.observer_dic[name] 
		del self.observer_rdic[target] 

	def registerObserver(self, target):
		assert(target not in self.observer)
		name = self._makeName(target)
		self._occupyName(name, target)
		self.observer.append(target)

	def unregisterObserver(self, target):
		assert(target in self.observer)
		name = self._getName(target)
		self._freeName(name, target)
		self.observer.remove(target)

	def query(self, name, loc=None):
		if loc==None:
			return self.observer_dic['_'+name]
		return self.observer_dic[loc+'_'+name]

	def queryList(self, index, value):
		result = []
		for x in self.observer:
			if x.get(index)==value:
				result.append(x)
		return result

	def queryList_mc(self, conditions):
		# mutiple conditions
		# e.g. conditions = {'name':['Amy', 'Bob'], 'age':range(5,80)}
		result = []
		for x in self.observer:
			found = True
			for c in conditions:
				if x.get(c) not in conditions[c]:
					found = False
					break
			if found:
				result.append(x)
		return result

