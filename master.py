import sys
from utils import msg as msg_, logger

try:
    port = sys.argv[2]
except IndexError:
    port = 5555

logger = logger()

debug_ = logger.debug
info_ = logger.info
warning_ = logger.warning
critical_ = logger.critical
error_ = logger.error


import zmq

ctx = zmq.Context()

cmd_sck = ctx.socket(zmq.PULL)

cmd_sck.bind('tcp://*:%s' % port)
debug_('bound to %s successful' % port)

hd_sck = ctx.socket(zmq.PUSH)
hd_sck.connect('tcp://192.168.1.102:21557')

nodes = {}
nodes_sockets = {}

while True:
    debug_('blocking when recv_json')
    msg = cmd_sck.recv_json()

    assert 'act' in msg
    action = msg['act']

    if action == 'up':
        addr = msg['addr']
        info_('addr %s up' % addr)
        nodes[addr] = 1
        _s = nodes_sockets[addr] = ctx.socket(zmq.PUSH)
        _s.connect(addr)
        _s.send_json(msg_('ret', status='ok', payload='ACK'))

    elif action == 'list nodes':
        info_('listing nodes %s', nodes)
        hd_sck.send_json(msg_('ret', status='list nodes ok', payload=nodes))

    elif action == 'down':
        addr = msg['addr']
        del nodes[addr]
        nodes_sockets[addr].close()
