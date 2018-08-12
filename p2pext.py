import hashlib, os, sys, time, socket, threading


def whoAmI():
    # os.system("sudo su")
    os.system("touch self.txt")
    os.system("ifconfig >> self.txt")
    f = open("self.txt", "r")
    ip = ""
    mac = ""
    interfaces = []
    donuthin = 0
    for ln in f.readlines():
        #print(ln)
        try:
            ip = ln.split("inet ")[1].split("netmask")[0]
            mac = ln.split("ether ")[1].split("tx")[1]
            interfaces.append(ln.split(": flags")[0])
        except:
            donuthin += 1
    os.system("rm self.txt")
    return ip, mac, interfaces


def tcp_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send("HI")
    response = client.recv(4096)
    client.close()
    print(response)
    return response


def tcp_messenger(message,where,to,):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((where, to))
    sock.send(message)
    print "Sending Message To: " +where
    response = sock.recv(1024)
    sock.close()
    return response


def main():
    start = time.time()
    peerIP = sys.argv[1]
    ip, mac, interfaces = whoAmI()
    peerID = tcp_client(peerIP,9999)
    myID = hashlib.sha256(ip).hexdigest()
    print tcp_messenger(myID,peerIP,9999)
    print "["+str(time.time() - start)+"s elapsed]"


if __name__ == "__main__":
    main()
