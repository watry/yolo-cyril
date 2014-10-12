import telnetlib
import re
import pub



class connection:
    def __init__(self, p_ip=''):
        self.state = "closed"
        self.tn = None
        self.ip = p_ip
        self.port = 3000
        self.username = "admin"
        self.password = "cMPC_pxn"
        self.init1()
    def init1(self):
        if self.ip=='' or self.ip==None:
            return 1
        try:
            self.tn=telnetlib.Telnet(host=self.ip, port=self.port, timeout=1)
            self.state = "initialing"
            self.tn.read_until('User: ', 3)
            self.tn.write(self.username + '\n')
            self.tn.read_until('Password: ', 3)
            self.tn.write(self.password + '\n')
            s = self.tn.read_until('# ', 3)
            self.tn.write('option page off' + '\n')
            s = self.tn.read_until('# ', 3)
            self.state = "connected" if '#' in s else "closed"
            return  0
        except:
            return 2
    def ready(self):
        return self.state=='connected'

    def mwrite(self, p_script=[], p_show=False):
        # write mutiple lines
        try:
            assert(self.state=="connected")
        except:
            return 100 #"----Connection failed:----\n"
        l=1
        err=0
        self.tn.write('configure\n')
        s = self.tn.read_until('# ', 1)
        pub.dbg(3, '[[[ '+s)
        index = 0
        while len(p_script)>index:
            w = p_script[index]
            index += 1
            self.tn.write(w+'\n')
            s = self.tn.read_until('# ', 5)
            pub.dbg(3, '[[[ '+s)
            self.state = "connected" if '#' in s else "closed"
            if p_show:
                l+=1
                print str(l)+":"+self.state
                print s
            if "ERROR" in s or "can't find" in s:
                err += 1
                break
        #self.tn.write('ab\n') #
        self.tn.write('co\n')
        s = self.tn.read_until('# ', 1)
        self.tn.write('ex\n')
        s = self.tn.read_until('# ', 1)
        #print "----OK----" if err==0 else "----Failed:----\n"+w+'\n'+s

        return err
    def close(self):
        self.tn.close()
    def expect(self, statement, regex_exp):
        assert(self.state=="connected")
        self.tn.write(statement+'\n')
        s = self.tn.read_until('# ', 3)
        return re.search(regex_exp, s, re.MULTILINE) != None

