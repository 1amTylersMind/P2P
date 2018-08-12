import hashlib, os, time, socket, threading
import RPi.GPIO as GPIO

def tcp_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send("GET /HTTP/1.1\r\n\r\n")
    response = client.recv(4096)
    client.close()
    return response


def udp_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto("AAABBBCCC",(host, port))
    data, address = client.recvfrom(4096)
    client.close()
    return data, address


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


def run(ip,gpioflag):
    TCPServer(ip,gpioflag)


class TCPServer:
        ACK_N = 0
        ip = ""
        Hello = False

        def __init__(self, local,gpio):
            self.hasLeds = gpio
            if self.hasLeds:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(20, GPIO.OUT)  # Green
                GPIO.setup(24, GPIO.OUT)  # Red
                GPIO.setup(27, GPIO.OUT)  # Blue
                # Server is running, to the light is GREEN
                GPIO.output(20, GPIO.HIGH)

            os.system("touch peers.txt")
            self.ip = local
            self.bind_ip = "0.0.0.0"
            self.bind_port = 9999

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.bind_ip, self.bind_port))
            server.listen(5)

            go = True
            print("[<<|- Starting P2P Node @ %s:%d-|>>]" % (self.bind_ip, self.bind_port))
            while go and not self.Hello:
                try:
                    client, addr = server.accept()
                    print "Connection Accepted from %s:%d" % (addr[0], addr[1])
                    client_handler = threading.Thread(target=self.handle_client, args=(client,addr[0]))
                    client_handler.start()
                    if self.hasLeds:
                        GPIO.output(20, GPIO.HIGH)
                except KeyboardInterrupt:
                    print "P2P Server Killed"
                    if self.hasLeds:
                        GPIO.output(27, GPIO.LOW)
                        GPIO.output(20, GPIO.LOW)
                    go = False
            print "Handshake Completed"
            os.system("rm peers.txt")
            if self.hasLeds:
                GPIO.cleanup()

        def handle_client(self, client_socket, remote_host):
            """
            Client handling thread
            :return:
            """
            if self.hasLeds:
                GPIO.output(24, GPIO.HIGH)
            request = client_socket.recv(1024)
            print("[*- %s" % request)
            # Send back an acknowledgement
            # including what peer you are
            # message = "ACK " + str(self.ACK_N)
            message = hashlib.sha256(self.ip).hexdigest()
            client_socket.send(message)
            data, peer = self.client_side_p2p(client_socket,remote_host)
            self.ACK_N += 1;

        def client_side_p2p(self, me, peer):
            if self.hasLeds:
                GPIO.output(24, GPIO.LOW)
                GPIO.output(20, GPIO.LOW)
                GPIO.output(27, GPIO.HIGH)
            peerHello = hashlib.sha256(self.ip).hexdigest()
            me.sendto(peerHello, (peer, 9999))
            data, address = me.recvfrom(4096)
            me.close()
            print
            self.Hello = True
            return data, address


def main():
    hasLED = False
    try:
        import RPi.GPIO as GPIO
        hasLED = True
    except ImportError:
        print "Cannot Use GPIO for LEDs "

    start = time.time()
    running = True
    # Get basic info about local machine for peer connections
    ip, mac, interfaces = whoAmI()
    print("Host IP: " + ip)
    print("MAC(s): " + mac)
    # Start a TCP Server to initialize Peer on the Network
    run(ip,hasLED)
    dt = time.time() - start
    print(str(dt)+"s Elapsed")


if __name__ == "__main__":
    main()
