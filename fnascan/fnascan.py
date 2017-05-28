#coding:utf-8
#author:wolf@future-sec

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
                        if title or h_server:server_type = 'web || ' + title
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
            re_data[host].append(str(port) + " " + str(info)  )
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
    port_list = []
    if '.ini' in port:
        port_config = open(port,'r')
        for port in port_config:
            port_list.append(port.strip())
        port_config.close()
    else:
        port_list = port.split(',')
    return port_list
def write_result():
    re_json = []
    re_array = {}
    td = ''
    try:
        ip_list = re_data.keys()
        ip_list.sort()
        for ip_str in ip_list:
            port_array = []
            for port_str in re_data[ip_str]:
                port_array.append({"name":port_str,"url":"%s"%(ip_str + ":" + port_str.split(" ")[0])})
            ip_array = {"name":ip_str,"submenu":port_array}
            if re_array.has_key(ip_str[0:ip_str.rindex('.')]+'.*'):
                re_array[ip_str[0:ip_str.rindex('.')]+'.*'].append(ip_array)
            else:
                re_array[ip_str[0:ip_str.rindex('.')]+'.*']=[]
                re_array[ip_str[0:ip_str.rindex('.')]+'.*'].append(ip_array)
        for ip_c in re_array:
            re_json.append({"name":ip_c,'submenu':re_array[ip_c]})
        # for server in statistics:
        #     td += "<tr><td align='center'>%s</td><td align='center'>%d</td></tr>"%(server,statistics[server])
        # td_html =  "<table><tr><th>Service</th><th>Count</th></tr>" + td + "</table>"
        if re_json:
            mo_html = "$adinfo$ \n____\n $data$ \n____\n '$statistics$'"
            mo_html = mo_html.replace('$adinfo$',str(json.dumps(re_json)))
            mo_html = mo_html.replace('$data$',json.dumps(port_data))
            mo_html = mo_html.replace('$statistics$',json.dumps(statistics))
            #result = open(ip + "-" + str(int(time.time())) + ".html","w")
            result = open(ip   + ".html","w")
            result.write(mo_html)
            result.close()
    except Exception,e:
        print 'Results output failure'
def t_join(m_count):
    tmp_count = 0
    i = 0
    while True:
        time.sleep(2)
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
        port = '21,22,23,25,53,80,110,139,143,389,443,445,465,873,993,995,1080,1723,1433,1521,3306,3389,3690,4440,5432,5800,5900,6379,7001,8000,8001,8080,8081,8888,9200,9300,9080,9999,11211,27017'
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

