import sys
sys.path.append('d:\\work\\yolo\\code')
import GLOBAL
import data


#make ne list
nw = []
nw.append(data.ne(p_ip = "192.168.50.4",  p_neid="20.0.0.1",  p_type="PN7700", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.6",  p_neid="20.0.0.2",  p_type="PN7700", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.10", p_neid="20.0.0.3",  p_type="PN7700", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.54", p_neid="20.0.0.4",  p_type="PN7500", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.56", p_neid="20.0.0.5",  p_type="PN7500", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.52", p_neid="20.0.0.6",  p_type="PN7500", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.94", p_neid="20.0.0.7",  p_type="PN7302", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.81", p_neid="20.0.0.8",  p_type="PN7302", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.85", p_neid="20.0.0.9",  p_type="PN7302", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.90", p_neid="20.0.0.10", p_type="PN7301", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.91", p_neid="20.0.0.11", p_type="PN7301", p_NTP="20.0.0.235", p_desc=""))
nw.append(data.ne(p_ip = "192.168.50.92", p_neid="20.0.0.12", p_type="PN7301", p_NTP="20.0.0.235", p_desc=""))
assert(len(nw)<GLOBAL.SCALE)

port={}
for i in range(len(nw)):
    port[nw[i]] = []

data.add_fib(port, nw[0], nw[1], "xg.10.1", "xg.14.1", ["ccn"])
data.add_fib(port, nw[0], nw[3], "xg.7.1", "xg.2.1", ["acn"])
data.add_fib(port, nw[0], nw[9], "ge.7.1", "ge.1.1", ["ccn"])
data.add_fib(port, nw[1], nw[2], "xg.11.2", "xg.4.1", ["ccn"])
data.add_fib(port, nw[1], nw[3], "xg.14.2", "xg.3.1")
data.add_fib(port, nw[1], nw[8], "ge.11.10", "ge.2.3", ["acn"])
data.add_fib(port, nw[2], nw[3], "xg.2.1", "xg.4.1")
data.add_fib(port, nw[2], nw[4], "xg.2.2", "xg.5.1")
data.add_fib(port, nw[2], nw[5], "xg.4.2", "xg.4.1", ["ccn"])
data.add_fib(port, nw[2], nw[10], "ge.2.8", "ge.1.1")
data.add_fib(port, nw[3], nw[4], "xg.2.2", "xg.3.1", ["acn"])
data.add_fib(port, nw[3], nw[6], "ge.2.20", "ge.2.1")
data.add_fib(port, nw[4], nw[5], "xg.5.2", "xg.3.1", ["ccn"])
data.add_fib(port, nw[4], nw[7], "ge.3.1", "ge.1.2", ["ccn"])
data.add_fib(port, nw[5], nw[11], "ge.4.5", "ge.1.4", ["acn"])
data.add_fib(port, nw[6], nw[7], "ge.2.2", "ge.1.3", ["acn"])
data.add_fib(port, nw[6], nw[9], "ge.2.3", "ge.1.4", ["acn"])
data.add_fib(port, nw[7], nw[11], "ge.1.1", "ge.1.1", ["ccn"])
data.add_fib(port, nw[8], nw[9], "ge.1.1", "ge.1.3", ["ccn"])
data.add_fib(port, nw[8], nw[10], "ge.2.2", "ge.1.2", ["ccn"])
data.add_fib(port, nw[10], nw[11], "ge.1.3", "ge.1.3", ["ccn"])

nw[0].mcn = "25.0.0.1\\24"

print "---start---"
for x in nw:
    x.gen_script(nw, port, ["neid", "slot", "nni", "ccn", "mcn", "NTP", "dr", "commit"])
    #supported: ["neid", "slot", "nni", "ccn", "mcn", "NTP", "dr", "commit"]
    print ""

print "---finish---"
print "todo: add ptp, freq, tpoam(with pools of mepid)"
