from ethereum import parse_genesis_declaration, db
from ethereum.block import Block
from ethereum.config import Env
from ethereum.state_transition import apply_block
import rlp
import json
import os
import sys

# from ethereum.slogging import LogRecorder, configure_logging, set_level
# config_string = ':info,eth.vm.log:trace,eth.vm.op:trace,eth.vm.stack:trace,eth.vm.exit:trace,eth.pb.msg:trace,eth.pb.tx:debug'
# configure_logging(config_string=config_string)

if 'saved_state.json' in os.listdir(os.getcwd()):
    s = parse_genesis_declaration.state_from_snapshot(json.load(open('saved_state.json')), Env())
    print 'state generated from saved state'
elif 'genesis_frontier.json' not in os.listdir(os.getcwd()):
    print 'Please download genesis_frontier.json from http://vitalik.ca/files/genesis_frontier.json'
    sys.exit()
else:
    s = parse_genesis_declaration.state_from_genesis_declaration(json.load(open('genesis_frontier.json')), Env())
    assert s.trie.root_hash.encode('hex') == 'd7f8974fb5ac78d9ac099b9ad5018bedc2ce0a72dad1827a1709da30580f0544'
    assert s.prev_headers[0].hash.encode('hex') == 'd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3'
    print 'state generated from genesis'
if '200kblocks.rlp' not in os.listdir(os.getcwd()):
    print 'Please download 200kblocks.rlp from http://vitalik.ca/files/200kblocks.rlp and put it in this directory to continue the test'
    sys.exit()
block_rlps = open('200kblocks.rlp').readlines()[s.block_number + 1:]
for block in block_rlps:
    # print 'prevh:', s.prev_headers
    block = rlp.decode(block.strip().decode('hex'), Block)
    apply_block(s, block)
    if block.header.number % 1000 == 0:
        snapshot = parse_genesis_declaration.to_snapshot(s)
        s = parse_genesis_declaration.state_from_snapshot(snapshot, s.env)
        snapshot2 = parse_genesis_declaration.to_snapshot(s)
        if snapshot != snapshot2:
            open('/tmp/1', 'w').write(json.dumps(snapshot))
            open('/tmp/2', 'w').write(json.dumps(snapshot2))
            raise Exception("snapshot difference")
        open('saved_state.json', 'w').write(json.dumps(snapshot, indent=4))
    print 'Applied block %d, %d transactions %d gas %d limit' % (block.header.number, len(block.transactions), block.header.gas_used, block.header.gas_limit)

print 'Test successful'