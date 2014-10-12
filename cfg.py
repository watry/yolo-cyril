

topo_data = {
	'nodes' : [
		['name',	'cost',			'ip'],
		['t80' ,	100,			'5.1.1.12'],
		['t21a',	100,			'5.1.1.11'],
		['t200',	100,			'5.1.1.13'],
		['v1',		100,		None],
		['v2',		100,		None],
	], # name, type, ip

	'ports' : [
		['loc',		'cost',	'name'],
		['t80', 	100,	'ge.1.5'],
		['t80', 	100,	'ge.1.9'],
		['t80', 	100,	'ge.1.12'],
		['t200', 	100,	'ge.1.5'],
		['t200', 	100,	'ge.1.8'],
		['t21a', 	100,	'ge.1.2'],
		['t21a', 	100,	'fe.1.1'],
		['t21a', 	100,	'fe.1.2'],
		['v1', 		100,	'p1'],
		['v2', 		100,	'p2'],
	],

	'fibs' : [
		['name', 'cost', 'n1_name', 'n1_portname', 'n2_name', 'n2_portname'],
		['f1',	 10,     't80', 'ge.1.5', 't200', 'ge.1.5'],
		['f2',	 10,     't80', 'ge.1.12', 't21a', 'ge.1.2'],
		['f3',	 10,     't21a', 'fe.1.2', 't200', 'ge.1.8'],
		['f4',	 10,     't80', 'ge.1.9', 'v1', 'p1'],
		['f5',	 10,     't21a', 'fe.1.1', 'v2', 'p2'],
	],
}

topo_data_dic = {}
for x in topo_data:
	topo_data_dic[x] = []
	for y in topo_data[x][1:]:
		t = []
		for z in range(len(y)):
			t.append((topo_data[x][0][z], y[z]))
		topo_data_dic[x].append(dict(t))


