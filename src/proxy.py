import logging
from twisted.internet import reactor
from quarry.net.proxy import DownstreamFactory, Bridge, Downstream, Upstream, UpstreamFactory

# based on https://github.com/barneygale/quarry/blob/master/examples/client_chat_logger.py
# taken from https://github.com/LiveOverflow/minecraft-hacked/blob/main/01_protocol_proxy/teleport_proxy.py

# and also based on https://github.com/barneygale/quarry/issues/135

class MyUpstream(Upstream):
    pass
    # def packet_login_encryption_request(self, buff):
    #     # buff.save()

    #     buff.restore()
    #     self.send_packet("login_encryption_request", buff.read())

class MyDownstream(Downstream):
    pass
    # def packet_login_encryption_response(self, buff):
    #     # buff.save()

    #     buff.restore()
    #     self.send_packet("login_encryption_response", buff.read())



class MyUpstreamFactory(UpstreamFactory):
    protocol = MyUpstream
    
    log_level = logging.DEBUG
    connection_timeout = 10



class MyBridge(Bridge):
    upstream_factory_class = MyUpstreamFactory

    # def __init__(self):
    #     self.enable_fast_forwarding();

    def packet_upstream_chat_message(self, buff):
        buff.save()
        chat_message = buff.unpack_string()
        print(f" >> {chat_message}")

        buff.restore()
        self.upstream.send_packet("chat_message", buff.read())

    def packet_unhandled(self, buff, direction, name):
        print(f"[*][{direction}] {name}")
        if direction == "downstream":
            self.downstream.send_packet(name, buff.read())
        elif direction == "upstream":
            self.upstream.send_packet(name, buff.read())



class MyDownstreamFactory(DownstreamFactory):
    protocol = MyDownstream
    bridge_class = MyBridge
    motd = "My Proxy" # Set default MOTD

    log_level = logging.DEBUG
    # bridge_class.enable_fast_forwarding(bridge_class)



# python basic_proxy.py -q 12345
def main(argv):
    # Parse options
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--listen-host", default="0.0.0.0", help="address to listen on")
    parser.add_argument("-p", "--listen-port", default=25565, type=int, help="port to listen on")
    parser.add_argument("-b", "--connect-host", default="127.0.0.1", help="address to connect to")
    parser.add_argument("-q", "--connect-port", default=25565, type=int, help="port to connect to")
    args = parser.parse_args(argv)

    logging.debug("Arguments parsed")

    # Create factory
    factory = MyDownstreamFactory()
    factory.connect_host = args.connect_host
    factory.connect_port = args.connect_port
    factory.motd = f"Proxy server proxying to {args.connect_host}:{args.connect_port}"

    logging.info(f"Factory created proxying to {args.connect_host}:{args.connect_port}\n")

    # Listen
    factory.listen(args.listen_host, args.listen_port)
    logging.info(f"Factory listening on {args.listen_host}:{args.listen_port}\nRunning reactor...")
    reactor.run()

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])