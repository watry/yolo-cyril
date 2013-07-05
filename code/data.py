import sys
sys.path.append('d:\\work\\yolo\\code')
import GLOBAL

class ne:
    def __init__(self, p_type='', p_neid='', p_ip='', p_NTP='', p_desc=''):
        self.neid = p_neid
        self.ip = p_ip
        self.desc = p_desc
        self.type = p_type
        self.ntp_server = p_NTP
        self.ccn_map = {}
        self.acn_map = {}
        self.mcn = None
    def gen_script(self, nelist, portlist, properties=[]):
        print "---"+self.desc+"---ip="+self.ip+"---id="+self.neid+"---type="+self.type+"---"
        ccn_in_use=0
        if "dr" in properties:
            print "dropdb"
        if "neid" in properties:
            print "set / id "+self.neid
        if "mcn" in properties:
            if self.mcn != None:
                print "set interfaces/mcn/1 ip " + self.mcn
                print "cr protocols/ospf/redistribute mcn"
        if "ccn" in properties:
            for rmt_ne in self.ccn_map:
                ccn_in_use+=1
                i = nelist.index(self)+1 #skip 0
                j = nelist.index(rmt_ne)+1
                assert(i<GLOBAL.SCALE and j<GLOBAL.SCALE)
                if i<j:
                    ccn_ip = "21." + str(i) + "." + str(j) + "."+"1/24"
                elif i>j:
                    ccn_ip = "21." + str(j) + "." + str(i) + "."+"2/24"
                else:
                    assert()
                print "create interfaces/ccn "+str(ccn_in_use)+\
                    " {admin='up',peer='"+rmt_ne.neid+\
                    "',ip='"+ccn_ip+"',admin='up',ospf={}}"
        if "slot" in properties:
            usedcard=set([])
            for each_port in [p[0] for p in portlist[self]]:
                usedcard.add(each_port.split('.')[1]) #.split('.')[1] to get slot
            if self.type == "PN7700":
                print "set slot/8/lg type XCT"
                print "co"
                print "set slot/9/lg type XCT"
                print "co"
                for slot_seq in usedcard:
                    if slot_seq in ['1', '16']:
                        print "set slot/"+slot_seq+"/lg type IP32"    #todo: in gui, on demand
                    elif slot_seq in ['2','3','4','5','6','7','10','11','12','14','15']:
                        print "set slot/"+slot_seq+"/lg type SX2G20"
                    else:
                        assert()
            elif self.type == "PN7500":
                print "set slot/3/lg type XCTPS"
                print "co"
                print "set slot/4/lg type XCTPS"
                print "co"
                for slot_seq in usedcard:
                    if slot_seq in ['6']:
                        print "set slot/"+str(slot_seq)+"/lg type IP32"    #todo: in gui, on demand
                    elif slot_seq in ['1', '2', '5']:
                        print "set slot/"+str(slot_seq)+"/lg type SX2G20"
                    elif slot_seq in ['3', '4']:
                        pass
                    else:
                        assert()
            elif self.type == "PN7302":
                print "set slot/1/lg type ACTP_A"
                print "co"
                print "set slot/2/lg type ACTP_A"
                print "co"
            elif self.type == "PN7301":
                print "set slot/1/lg type ACTP_B"
                print "co"
            else:
                print "(undefined device type)"
        if "nni" in properties:
            for p in portlist[self]:
                if self.type=="PN7500" and (p[0] in ["ge.3.5", "ge.3.6", "ge.4.5", "ge.4.6"]):
                    print "set slot/" + p[0].split('.')[1] + "/lg port" + p[0].split('.')[2] + " ETH"
                print "set interfaces/eth/" +p[0]+" admin up"
                print "set interfaces/eth/" +p[0]+" role nni"
                #todo: config it
                ccn_enable = False
                if p[1] in self.ccn_map:
                    if p[0] in self.ccn_map[p[1]]:
                        ccn_enable = True
                if p[1] in self.acn_map:
                    if p[0] in self.acn_map[p[1]]:
                        ccn_enable = True
                if not ccn_enable:
                    print "set interfaces/eth/" +p[0]+"/nbr ccn false"
        if "NTP" in properties:
            print "set protocols/ntp server " + self.ntp_server
        if "commit" in properties:
            print "commit"

def add_fib(port, ne1, ne2, port1, port2, properties=[]):
    port[ne1].append([port1, ne2, port2])
    port[ne2].append([port2, ne1, port1])
    if "ccn" in properties:
        if ne2 in ne1.ccn_map:
            ne1.ccn_map[ne2].append(port1)
        else:
            ne1.ccn_map[ne2] = [port1]
        if ne1 in ne2.ccn_map:
            ne2.ccn_map[ne1].append(port2)
        else:
            ne2.ccn_map[ne1] = [port2]
    if "acn" in properties:
        if ne2 in ne1.acn_map:
            ne1.acn_map[ne2].append(port1)
        else:
            ne1.acn_map[ne2] = [port1]
        if ne1 in ne2.ccn_map:
            ne2.acn_map[ne1].append(port2)
        else:
            ne2.acn_map[ne1] = [port2]

def get_opp_port(port, ne, p):
    for x in port[ne]:
        if x[0]==p:
            return x[2]
    assert()    #found no proper port

