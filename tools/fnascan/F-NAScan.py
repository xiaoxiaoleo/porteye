#coding:utf-8
#author:holeeinfo@gmail.com

import getopt,sys,Queue,threading,socket,struct,urllib2,time,os,re,json,base64,cgi,array,ssl

queue = Queue.Queue()
mutex = threading.Lock()
timeout = 10
port_list = []
re_data = {}
port_data = {}
statistics = {}
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
class UnicodeStreamFilter:
    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding
    def write(self, s):
        if type(s) == str:
            s = s.decode("utf-8")
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)
if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)
class SendPingThr(threading.Thread):
    def __init__(self, ipPool, icmpPacket, icmpSocket, timeout=3):
        threading.Thread.__init__(self)
        self.Sock = icmpSocket
        self.ipPool = ipPool
        self.packet = icmpPacket
        self.timeout = timeout
        self.Sock.settimeout(timeout + 1)

    def run(self):
        time.sleep(0.01)
        for ip in self.ipPool:
            try:
                self.Sock.sendto(self.packet, (ip, 0))
            except socket.timeout:
                break
        time.sleep(self.timeout)

class Nscan:
    def __init__(self, timeout=3):
        self.timeout = timeout
        self.__data = struct.pack('d', time.time())
        self.__id = os.getpid()

    @property
    def __icmpSocket(self):
        Sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        return Sock

    def __inCksum(self, packet):
        if len(packet) & 1:
            packet = packet + '\0'
        words = array.array('h', packet)
        sum = 0
        for word in words:
            sum += (word & 0xffff)
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        return (~sum) & 0xffff

    @property
    def __icmpPacket(self):
        header = struct.pack('bbHHh', 8, 0, 0, self.__id, 0)
        packet = header + self.__data
        chkSum = self.__inCksum(packet)
        header = struct.pack('bbHHh', 8, 0, chkSum, self.__id, 0)
        return header + self.__data

    def mPing(self, ipPool):
        Sock = self.__icmpSocket
        Sock.settimeout(self.timeout)
        packet = self.__icmpPacket
        recvFroms = set()
        sendThr = SendPingThr(ipPool, packet, Sock, self.timeout)
        sendThr.start()
        while True:
            try:
                ac_ip = Sock.recvfrom(1024)[1][0]
                if ac_ip not in recvFroms:
                    log("active",ac_ip,0)
                    recvFroms.add(ac_ip)
            except Exception:
                pass
            finally:
                if not sendThr.isAlive():
                    break
        return recvFroms & ipPool
def get_ac_ip(ip_list):
    try:
        s = Nscan()
        ipPool = set(ip_list)
        return s.mPing(ipPool)
    except:
        print 'The current user permissions unable to send icmp packets'
        return ip_list
class ThreadNum(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            try:
                if queue.empty():break
                queue_task = self.queue.get()
            except:
                break
            try:
                task_host,task_port = queue_task.split(":")
                data = scan_port(task_host,task_port)
                if data:
                    if data <> 'NULL':
                        port_data[task_host + ":" + task_port] = urllib2.quote(data)
                    server_type = server_discern(task_host,task_port,data)
                    if not server_type:
                        h_server,title = get_web_info(task_host,task_port)
                        if title or h_server:server_type = 'web ' + title
                    if server_type:log('server',task_host,task_port,server_type.strip())
            except Exception,e:
                continue
def get_code(header,html):
    try:
        m = re.search(r'<meta.*?charset\=(.*?)"(>| |\/)',html, flags=re.I)
        if m:
            return m.group(1).replace('"','')
    except:
        pass
    try:
        if header.has_key('Content-Type'):
            Content_Type = header['Content-Type']
            m = re.search(r'.*?charset\=(.*?)(;|$)',Content_Type,flags=re.I)
            if m:return m.group(1)
    except:
        pass
def get_web_info(host,port):
    h_server,h_xpb,title_str,html = '','','',''
    try:
        info = urllib2.urlopen("http://%s:%s"%(host,port),timeout=timeout)
        html = info.read()
        header = info.headers
    except urllib2.HTTPError,e:
        header = e.headers
    except Exception,e:
        return False,False
    if not header:return False,False
    try:
        html_code = get_code(header,html).strip()
        if html_code and len(html_code) < 12:
            html = html.decode(html_code).encode('utf-8')
    except:
        pass
    try:
        port_data[host + ":" + str(port)] = urllib2.quote(str(header) + "\r\n\r\n" + cgi.escape(html))
        title = re.search(r'<title>(.*?)</title>', html, flags=re.I|re.M)
        if title:title_str=title.group(1)
    except Exception,e:
        pass
    return str(header),title_str
def scan_port(host,port):
    try:
        socket.setdefaulttimeout(timeout/2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((str(host),int(port)))
        log('portscan',host,port)
    except Exception,e:
        return False
    try:
        data = sock.recv(512)
        sock.close()
        if len(data) > 2:
            return data
        else:
            return 'NULL'
    except Exception,e:
        return 'NULL'
def log(scan_type,host,port,info=''):
    mutex.acquire()
    try:
        time_str = time.strftime('%X', time.localtime(time.time()))
        if scan_type == 'portscan':
            print "[%s] %s:%d open"%(time_str,host,int(port))
            try:
                re_data[host].append(port)
            except KeyError:
                re_data[host]=[]
                re_data[host].append(port)
        elif scan_type == 'server':
            print "[%s] %s:%d is %s"%(time_str,host,int(port),str(info))
            try:
                server = info.split(" ")[0].replace("(default)","")
                statistics[server] += 1
            except KeyError:
                statistics[server] = 1
            re_data[host].remove(port)
            re_data[host].append(str(port) + " " + str(info))
        elif scan_type == 'active':
            print "[%s] %s active"%(time_str,host)
    except Exception,e:
        pass
    mutex.release()
def read_config(config_type):
    if config_type == 'server_info':
        mark_list=[]
        try:
            config_file = open('server_info.ini','r')
            for mark in config_file:
                name,port,reg = mark.strip().split("|",2)
                mark_list.append([name,port,reg])
            config_file.close()
            return mark_list
        except:
            print 'Configuration file read failed'
            exit()
def server_discern(host,port,data):
    server = ''
    for mark_info in mark_list:
        try:
            name,default_port,reg = mark_info
            if int(default_port) == int(port):server = name+"(default)"
            if reg and data <> 'NULL':
                matchObj = re.search(reg,data,re.I|re.M)
                if matchObj:server = name
                if server:
                    return server
        except Exception,e:
            continue
    return server
def get_ip_list(ip):
    ip_list = []
    iptonum = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    numtoip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
    if '-' in ip:
        ip_range = ip.split('-')
        ip_start = long(iptonum(ip_range[0]))
        ip_end = long(iptonum(ip_range[1]))
        ip_count = ip_end - ip_start
        if ip_count >= 0 and ip_count <= 65536:
            for ip_num in range(ip_start,ip_end+1):
                ip_list.append(numtoip(ip_num))
        else:
            print '-h wrong format'
    elif '.ini' in ip:
        ip_config = open(ip,'r')
        for ip in ip_config:
            ip_list.extend(get_ip_list(ip.strip()))
        ip_config.close()
    else:
        ip_split=ip.split('.')
        net = len(ip_split)
        if net == 2:
            for b in range(1,255):
                for c in range(1,255):
                    ip = "%s.%s.%d.%d"%(ip_split[0],ip_split[1],b,c)
                    ip_list.append(ip)
        elif net == 3:
            for c in range(1,255):
                ip = "%s.%s.%s.%d"%(ip_split[0],ip_split[1],ip_split[2],c)
                ip_list.append(ip)
        elif net ==4:
            ip_list.append(ip)
        else:
            print "-h wrong format"
    return ip_list
def get_port_list(port):
    if '.ini' in port:
        port_config = open(port,'r')
        for port in port_config:
            port_list.append(port.strip())
        port_config.close()
    else:
        port_list = port.split(',')
    return port_list
def write_result():
    try:
        mo_html = base64.b64decode("PCFET0NUWVBFIGh0bWw+DQo8aHRtbCBsYW5nPSJlbiI+DQo8aGVhZD4NCjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4NCjxtZXRhIGh0dHAtZXF1aXY9IlgtVUEtQ29tcGF0aWJsZSIgY29udGVudD0iSUU9ZWRnZSI+DQo8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEiPg0KPCEtLSBUaGUgYWJvdmUgMyBtZXRhIHRhZ3MgKm11c3QqIGNvbWUgZmlyc3QgaW4gdGhlIGhlYWQ7IGFueSBvdGhlciBoZWFkIGNvbnRlbnQgbXVzdCBjb21lICphZnRlciogdGhlc2UgdGFncyAtLT4NCjx0aXRsZT7miavmj4/nu5Pmnpw8L3RpdGxlPg0KPCEtLSBCb290c3RyYXAgLS0+DQo8bGluayBocmVmPSJodHRwczovL21heGNkbi5ib290c3RyYXBjZG4uY29tL2Jvb3RzdHJhcC8zLjMuNi9jc3MvYm9vdHN0cmFwLm1pbi5jc3MiIHJlbD0ic3R5bGVzaGVldCI+DQo8IS0tIEhUTUw1IHNoaW0gYW5kIFJlc3BvbmQuanMgZm9yIElFOCBzdXBwb3J0IG9mIEhUTUw1IGVsZW1lbnRzIGFuZCBtZWRpYSBxdWVyaWVzIC0tPg0KPCEtLSBXQVJOSU5HOiBSZXNwb25kLmpzIGRvZXNuJ3Qgd29yayBpZiB5b3UgdmlldyB0aGUgcGFnZSB2aWEgZmlsZTovLyAtLT4NCjwhLS1baWYgbHQgSUUgOV0+DQogICAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9vc3MubWF4Y2RuLmNvbS9odG1sNXNoaXYvMy43LjIvaHRtbDVzaGl2Lm1pbi5qcyI+PC9zY3JpcHQ+DQogICAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9vc3MubWF4Y2RuLmNvbS9yZXNwb25kLzEuNC4yL3Jlc3BvbmQubWluLmpzIj48L3NjcmlwdD4NCiAgICA8IVtlbmRpZl0tLT4NCjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+DQoucG9ydCB7IGN1cnNvcjogcG9pbnRlcjsgfQ0KI2luZm9Nb2RhbCAubW9kYWwtYm9keSwgI3Jlc3BvbnNlIHsgbWF4LWhlaWdodDogNjAwcHg7IH0NCiNzdGF0Q2hhcnQgeyB3aWR0aDogMTAwJSAhaW1wb3J0YW50O2hlaWdodDogNjAwcHggIWltcG9ydGFudDsgfQ0KPC9zdHlsZT4NCjwvaGVhZD4NCjxib2R5Pg0KCTxkaXYgY2xhc3M9ImNvbnRhaW5lci1mbHVpZCI+DQoJCTxkaXYgY2xhc3M9InJvdyI+DQoJCQk8ZGl2IGNsYXNzPSJjb2wtbGctMTIiPg0KCQkJCTxkaXYgY2xhc3M9InBhbmVsIHBhbmVsLWRlZmF1bHQiPg0KCQkJCQk8ZGl2IGNsYXNzPSJwYW5lbC1oZWFkaW5nIj7mnI3liqHnu5/orqE8L2Rpdj4NCgkJCQkJPGRpdiBjbGFzcz0icGFuZWwtYm9keSI+DQoJCQkJCQk8ZGl2IGNsYXNzPSJhbGVydCBhbGVydC1zdWNjZXNzIiByb2xlPSJhbGVydCI+DQoJCQkJCQkJPHNwYW4gY2xhc3M9ImdseXBoaWNvbiBnbHlwaGljb24tdGgtbGlzdCI+PC9zcGFuPg0KCQkJCQkJCeaOoua1i+WIsOacjeWKoeWZqOaVsO+8mg0KCQkJCQkJCTxzcGFuIGlkPSJ0b3RhbC1zZXJ2ZXIiIGNsYXNzPSJiYWRnZSI+PC9zcGFuPg0KCQkJCQkJPC9kaXY+DQoJCQkJCQk8ZGl2IGNsYXNzPSJhbGVydCBhbGVydC1pbmZvIiByb2xlPSJhbGVydCI+DQoJCQkJCQkJPHNwYW4gY2xhc3M9ImdseXBoaWNvbiBnbHlwaGljb24tZmxhc2giPjwvc3Bhbj4NCgkJCQkJCQnlvIDmlL7nq6/lj6PmgLvmlbDvvJoNCgkJCQkJCQk8c3BhbiBpZD0idG90YWwtcG9ydCIgY2xhc3M9ImJhZGdlIj48L3NwYW4+DQoJCQkJCQk8L2Rpdj4NCgkJCQkJCTxkaXY+DQoJCQkJCQkJPGNhbnZhcyBpZD0ic3RhdENoYXJ0Ij48L2NhbnZhcz4NCgkJCQkJCTwvZGl2Pg0KCQkJCQk8L2Rpdj4NCgkJCQk8L2Rpdj4NCgkJCTwvZGl2Pg0KCQk8L2Rpdj4NCgkJPGRpdiBjbGFzcz0icm93Ij4NCgkJCTxkaXYgY2xhc3M9ImNvbC1sZy0xMiI+DQoJCQkJPGRpdiBjbGFzcz0icGFuZWwgcGFuZWwtZGVmYXVsdCI+DQoJCQkJCTxkaXYgY2xhc3M9InBhbmVsLWhlYWRpbmciPuaOoua1i+WIsOeahOmhtemdouagh+mimDwvZGl2Pg0KCQkJCQk8ZGl2IGNsYXNzPSJwYW5lbC1ib2R5Ij4NCgkJCQkJCTx0YWJsZSBpZD0idGl0bGUtdGFibGUiIGNsYXNzPSJ0YWJsZSB0YWJsZS1ob3ZlciI+DQoJCQkJCQkJPHRoZWFkPg0KCQkJCQkJCQk8dHI+DQoJCQkJCQkJCQk8dGg+5Zyw5Z2APC90aD4NCgkJCQkJCQkJCTx0aD7moIfpopg8L3RoPg0KCQkJCQkJCQk8L3RyPg0KCQkJCQkJCTwvdGhlYWQ+DQoJCQkJCQkJPHRib2R5Pg0KCQkJCQkJCTwvdGJvZHk+DQoJCQkJCQk8L3RhYmxlPg0KCQkJCQk8L2Rpdj4NCgkJCQk8L2Rpdj4NCgkJCTwvZGl2Pg0KCQk8L2Rpdj4NCgkJPGRpdiBjbGFzcz0icm93Ij4NCgkJCTxkaXYgY2xhc3M9ImNvbC1sZy0xMiI+DQoJCQkJPGRpdiBjbGFzcz0icGFuZWwgcGFuZWwtZGVmYXVsdCI+DQoJCQkJCTxkaXYgY2xhc3M9InBhbmVsLWhlYWRpbmciPuW8gOaUvuerr+WPozwvZGl2Pg0KCQkJCQk8ZGl2IGNsYXNzPSJwYW5lbC1ib2R5Ij4NCgkJCQkJCTx0YWJsZSBpZD0icG9ydHMtdGFibGUiIGNsYXNzPSJ0YWJsZSB0YWJsZS1ob3ZlciI+DQoJCQkJCQkJPHRoZWFkPg0KCQkJCQkJCQk8dHI+DQoJCQkJCQkJCQk8dGg+SVA8L3RoPg0KCQkJCQkJCQkJPHRoPuerr+WPozwvdGg+DQoJCQkJCQkJCTwvdHI+DQoJCQkJCQkJPC90aGVhZD4NCgkJCQkJCQk8dGJvZHk+DQoJCQkJCQkJPC90Ym9keT4NCgkJCQkJCTwvdGFibGU+DQoJCQkJCTwvZGl2Pg0KCQkJCTwvZGl2Pg0KCQkJPC9kaXY+DQoJCTwvZGl2Pg0KCTwvZGl2Pg0KCTxkaXYgY2xhc3M9Im1vZGFsIGZhZGUiIGlkPSJpbmZvTW9kYWwiIHRhYmluZGV4PSItMSI+DQoJCTxkaXYgY2xhc3M9Im1vZGFsLWRpYWxvZyBtb2RhbC1sZyI+DQoJCQk8ZGl2IGNsYXNzPSJtb2RhbC1jb250ZW50Ij4NCgkJCQk8ZGl2IGNsYXNzPSJtb2RhbC1oZWFkZXIiPg0KCQkJCQk8YnV0dG9uIHR5cGU9ImJ1dHRvbiIgY2xhc3M9ImNsb3NlIiBkYXRhLWRpc21pc3M9Im1vZGFsIj4NCgkJCQkJCTxzcGFuPiZ0aW1lczs8L3NwYW4+DQoJCQkJCTwvYnV0dG9uPg0KCQkJCQk8aDQgY2xhc3M9Im1vZGFsLXRpdGxlIj7or6bnu4bkv6Hmga88L2g0Pg0KCQkJCTwvZGl2Pg0KCQkJCTxkaXYgY2xhc3M9Im1vZGFsLWJvZHkiPg0KCQkJCQk8cHJlIGlkPSJyZXNwb25zZSI+PC9wcmU+DQoJCQkJPC9kaXY+DQoJCQkJPGRpdiBjbGFzcz0ibW9kYWwtZm9vdGVyIj4NCgkJCQkJPGJ1dHRvbiB0eXBlPSJidXR0b24iIGNsYXNzPSJidG4gYnRuLWRlZmF1bHQiIGRhdGEtZGlzbWlzcz0ibW9kYWwiPuWFs+mXrTwvYnV0dG9uPg0KCQkJCTwvZGl2Pg0KCQkJPC9kaXY+DQoJCTwvZGl2Pg0KCTwvZGl2Pg0KCTwhLS0galF1ZXJ5IChuZWNlc3NhcnkgZm9yIEJvb3RzdHJhcCdzIEphdmFTY3JpcHQgcGx1Z2lucykgLS0+DQoJPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2pxdWVyeS8xLjExLjMvanF1ZXJ5Lm1pbi5qcyI+PC9zY3JpcHQ+DQoJPCEtLSBJbmNsdWRlIGFsbCBjb21waWxlZCBwbHVnaW5zIChiZWxvdyksIG9yIGluY2x1ZGUgaW5kaXZpZHVhbCBmaWxlcyBhcyBuZWVkZWQgLS0+DQoJPHNjcmlwdCBzcmM9Imh0dHBzOi8vbWF4Y2RuLmJvb3RzdHJhcGNkbi5jb20vYm9vdHN0cmFwLzMuMy42L2pzL2Jvb3RzdHJhcC5taW4uanMiPjwvc2NyaXB0Pg0KCTxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9DaGFydC5qcy8xLjAuMi9DaGFydC5taW4uanMiPjwvc2NyaXB0Pg0KCTxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4NCgkJdmFyIHNlcnZlcnMgICAgPSAkc2VydmVycyQ7DQoJCXZhciBwb3J0ZGF0YSAgID0gJHBvcnRkYXRhJDsNCgkJdmFyIHN0YXRpc3RpY3MgPSAkc3RhdGlzdGljcyQ7DQoJCQ0KCQkkKGZ1bmN0aW9uKCkgew0KCQkJU3RyaW5nLnByb3RvdHlwZS5mb3JtYXQgPSBmdW5jdGlvbigpIHsNCgkJCSAgICB2YXIgcyA9IHRoaXMsaSA9IGFyZ3VtZW50cy5sZW5ndGg7DQoJCQkgICAgd2hpbGUgKGktLSkgew0KCQkJICAgICAgICBzID0gcy5yZXBsYWNlKG5ldyBSZWdFeHAoJ1xceycgKyBpICsgJ1xcfScsICdnbScpLCBhcmd1bWVudHNbaV0pOw0KCQkJICAgIH0NCgkJCSAgICByZXR1cm4gczsNCgkJCX07DQoJCQkNCgkJCXZhciBjdHggPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgic3RhdENoYXJ0IikuZ2V0Q29udGV4dCgiMmQiKTsNCg0KCQkJdmFyIGRhdGEgPSB7fTsNCg0KCQkJZGF0YS5sYWJlbHMgPSBPYmplY3Qua2V5cyhzdGF0aXN0aWNzKTsNCgkJCWRhdGEuZGF0YXNldHMgPSBbIHsNCgkJCQlsYWJlbCA6ICLmlbDph48iLA0KCQkJCWZpbGxDb2xvciA6ICJyZ2JhKDEwMSwxNTQsMjAxLDEpIiwNCgkJCQlzdHJva2VDb2xvciA6ICJyZ2JhKDg0LCAxNDAsIDE4OCwxKSIsDQoJCQkJaGlnaGxpZ2h0RmlsbCA6ICJyZ2JhKDEyMSwgMTg5LCAyMDYsMSkiLA0KCQkJCWhpZ2hsaWdodFN0cm9rZSA6ICJyZ2JhKDEwNSwgMTgwLCAxOTgsMSkiLA0KCQkJCWRhdGEgOiBPYmplY3Qua2V5cyhzdGF0aXN0aWNzKS5tYXAoZnVuY3Rpb24oaykgew0KCQkJCQlyZXR1cm4gc3RhdGlzdGljc1trXTsNCgkJCQl9KQ0KCQkJfSBdOw0KCQkJdmFyIHN0YXRDaGFydCA9IG5ldyBDaGFydChjdHgpLkJhcihkYXRhKTsNCgkJCSQoJyNzdGF0Q2hhcnQnKS5jbGljayhmdW5jdGlvbihldnQpIHsNCgkJCQl2YXIgYWN0aXZlQmFycyA9IHN0YXRDaGFydC5nZXRCYXJzQXRFdmVudChldnQpOw0KCQkJCSQoIiNwb3J0cy10YWJsZSB0ciIpLnJlbW92ZUNsYXNzKCk7DQoJCQkJdmFyIHR5cGUgPSBhY3RpdmVCYXJzWzBdLmxhYmVsOw0KCQkJCWlmICh0eXBlKSB7DQoJCQkJCSQoJyNwb3J0cy10YWJsZSBzcGFuW2RhdGEtb3JpZ2luYWwtdGl0bGUqPSInICsgdHlwZSArICciXScpLmNsb3Nlc3QoJ3RyJykuYWRkQ2xhc3MoJ3dhcm5pbmcnKTsNCgkJCQl9DQoJCQl9KTsNCg0KCQkJdmFyIHRvdGFsU2VydmVyID0gMCwgdG90YWxQb3J0ID0gMCwgdGl0bGVzID0gW10sIHRyZWdleCA9IC8oXGQrKSB3ZWIgKC4rKSQvOw0KCQkJJC5lYWNoKHNlcnZlcnMsIGZ1bmN0aW9uKGlwLCBwb3J0cykgew0KCQkJCXRvdGFsU2VydmVyKys7DQoJCQkJdG90YWxQb3J0ICs9IHBvcnRzLmxlbmd0aDsNCgkJCQl2YXIgb3BlbmVkID0gcG9ydHMubWFwKGZ1bmN0aW9uKHApIHsNCgkJCQkJdmFyIGFyciA9IHRyZWdleC5leGVjKHApOw0KCQkJCQlpZiAoYXJyICE9IG51bGwgJiYgYXJyLmxlbmd0aCA+IDIpIHsNCgkJCQkJCXRpdGxlcy5wdXNoKHsNCgkJCQkJCQlpcDppcCwNCgkJCQkJCQlwb3J0OmFyclsxXSwNCgkJCQkJCQl0aXRsZTphcnJbMl0NCgkJCQkJCX0pOw0KCQkJCQl9DQoJCQkJCXJldHVybiAnPHNwYW4gZGF0YS10b2dnbGU9InRvb2x0aXAiIHRpdGxlPSJ7MH0iIGNsYXNzPSJsYWJlbCBsYWJlbC1zdWNjZXNzIHBvcnQiPnsxfTwvc3Bhbj4nLmZvcm1hdChwLHAuc3BsaXQoJyAnKVswXSkNCgkJCQl9KS5qb2luKCcgJyk7DQoNCgkJCQkkKCcjcG9ydHMtdGFibGUgdGJvZHknKS5hcHBlbmQoJzx0cj48dGQ+ezB9PC90ZD48dGQ+ezF9PC90ZD48L3RyPicuZm9ybWF0KGlwLG9wZW5lZCkpOw0KCQkJfSk7DQoJCQkkKCcjdG90YWwtc2VydmVyJykuaHRtbCh0b3RhbFNlcnZlcik7DQoJCQkkKCcjdG90YWwtcG9ydCcpLmh0bWwodG90YWxQb3J0KTsNCgkJCQ0KCQkJJC5lYWNoKHRpdGxlcywgZnVuY3Rpb24oaW5kZXgsIHQpIHsNCgkJCQkkKCcjdGl0bGUtdGFibGUgdGJvZHknKS5hcHBlbmQoJzx0cj48dGQ+PGEgaHJlZj0iaHR0cDovL3swfSI+ezB9PC9hPjwvdGQ+PHRkPnsxfTwvdGQ+PC90cj4nLmZvcm1hdCh0LmlwKyc6Jyt0LnBvcnQsdC50aXRsZSkpOw0KCQkJfSk7DQoNCgkJCSQoJ1tkYXRhLXRvZ2dsZT0idG9vbHRpcCJdJykudG9vbHRpcCgpOw0KDQoJCQkkKCcucG9ydCcpLmNsaWNrKGZ1bmN0aW9uKCkgew0KCQkJCXZhciBrZXkgPSAkKHRoaXMpLnBhcmVudCgpLnByZXYoKS5odG1sKCkgKyAiOiIgKyAkKHRoaXMpLmh0bWwoKTsNCgkJCQlpZiAocG9ydGRhdGEuaGFzT3duUHJvcGVydHkoa2V5KSkgew0KCQkJCQkkKCcjcmVzcG9uc2UnKS5odG1sKGRlY29kZVVSSUNvbXBvbmVudChwb3J0ZGF0YVtrZXldKSk7DQoJCQkJCSQoJyNpbmZvTW9kYWwnKS5tb2RhbCgnc2hvdycpOw0KCQkJCX0NCgkJCX0pOw0KCQl9KTsNCgk8L3NjcmlwdD4NCjwvYm9keT4NCjwvaHRtbD4=")
        mo_html = mo_html.replace('$servers$',str(json.dumps(re_data)))
        mo_html = mo_html.replace('$portdata$',str(json.dumps(port_data)))
        mo_html = mo_html.replace('$statistics$',str(json.dumps(statistics)))
        result = open(ip + "-" + str(int(time.time())) + ".html","w")
        result.write(mo_html)
        result.close()
    except Exception,e:
        print 'Results output failure'
def t_join(m_count):
    tmp_count = 0
    i = 0
    while True:
        time.sleep(1)
        ac_count = threading.activeCount()
        if ac_count < m_count and ac_count == tmp_count:
            i+=1
        else:
            i = 0
        tmp_count = ac_count
        #print ac_count,queue.qsize()
        if (queue.empty() and threading.activeCount() <= 1) or i > 5:
            break
if __name__=="__main__":
    mark_list = read_config('server_info')
    msg = '''
Scanning a network asset information script,author:wolf@future-sec.
Usage: python F-NAScan.py -h 192.168.1 [-p 21,80,3306] [-m 50] [-t 10] [-n]
    '''
    if len(sys.argv) < 2:
        print msg
    try:
        options,args = getopt.getopt(sys.argv[1:],"h:p:m:t:n")
        ip = ''
        noping = False
        port = '21,22,23,25,53,80,110,139,143,389,443,445,465,873,993,995,1080,1723,1433,1521,3306,3389,3690,5432,5800,5900,6379,7001,8000,8001,8080,8081,8888,9200,9300,9080,9999,11211,27017'
        m_count = 100
        for opt,arg in options:
            if opt == '-h':
                ip = arg
            elif opt == '-p':
                port = arg
            elif opt == '-m':
                m_count = int(arg)
            elif opt == '-t':
                timeout = int(arg)
            elif opt == '-n':
                noping = True
        if ip:
            ip_list = get_ip_list(ip)
            port_list = get_port_list(port)
            if not noping:ip_list=get_ac_ip(ip_list)
            for ip_str in ip_list:
                for port_int in port_list:
                    queue.put(':'.join([ip_str,port_int]))
            for i in range(m_count):
                t = ThreadNum(queue)
                t.setDaemon(True)
                t.start()
            t_join(m_count)
            write_result()
    except Exception,e:
        print e
        print msg