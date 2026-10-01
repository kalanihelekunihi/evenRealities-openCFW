#!/usr/bin/env python3
"""Offline checks of original G2 Thumb code, with explicit external call stubs.
Run with ~/.local/share/opencfw/venv/bin/python. Writes only beside this script.
No device, network, Ghidra-project or campaign writes.
"""
import csv
import hashlib
import json
from pathlib import Path
import struct
import uuid
import capstone
import unicorn
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PAYLOAD = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
BASE = 0x437fe0  # 32-byte OTA preamble; first executable/vector byte = 0x438000.
BLOB = PAYLOAD.read_bytes()
assert len(BLOB) == 3523396 and hashlib.sha256(BLOB).hexdigest() == SHA
REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]
CTX, HANDLES, MSG, DATA, ALLOC = 0x20074074, 0x20077000, 0x20077100, 0x20077200, 0x20077300
STOP = 0x10000000
SYMBOLS = list(csv.DictReader((ROOT / 'g2/symbols/apollo_main.tsv').open(), delimiter='\t'))
FUNCTIONS = [r for r in SYMBOLS if 0x4c46c0 <= int(r['address'], 16) < 0x4c4c66]
NAMES = {int(r['address'], 16): r['name'] for r in SYMBOLS}
MD = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)

def code(a, z):
    return BLOB[a-BASE:z-BASE]

def u32(a):
    return struct.unpack('<I', code(a, a+4))[0]

# Independent instruction decode and source slice hash checks, not decompiler text.
disassembly, records = [], []
for r in FUNCTIONS:
    a, z = int(r['address'], 16), int(r['end'], 16)
    digest = hashlib.sha256(code(a, z)).hexdigest()
    assert digest == r['stock_sha256'], r['name']
    insns = list(MD.disasm(code(a, z), a))
    assert sum(i.size for i in insns) == z-a
    callees = []
    disassembly.append('\n%s [%08x,%08x) sha256=%s' % (r['name'], a, z, digest))
    for i in insns:
        annotation = ''
        if i.mnemonic in ('bl', 'b.w') and i.op_str.startswith('#'):
            dest = int(i.op_str[1:], 0)
            annotation = ' ; ' + NAMES.get(dest, 'unknown')
            callees.append({'address': hex(dest), 'name': NAMES.get(dest, 'unknown')})
        disassembly.append('%08x  %-10s %-8s %s%s' % (i.address, i.bytes.hex(), i.mnemonic, i.op_str, annotation))
    records.append({'name': r['name'], 'start': hex(a), 'end': hex(z), 'sha256': digest, 'direct_callees': callees})
# Direct callers observed in existing per-function exports, then verify their BL.
for record in records:
    target = int(record['start'], 16)
    callers = []
    corpus = ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp'
    for p in corpus.glob('*.c'):
        if record['name'] + '(' not in p.read_text():
            continue
        start = int(p.stem, 16)
        row = next((r for r in SYMBOLS if int(r['address'],16) == start), None)
        if row:
            for i in MD.disasm(code(start, int(row['end'],16)), start):
                if i.mnemonic == 'bl' and i.op_str == '#0x%x' % target:
                    callers.append({'function': hex(start), 'name': row['name'], 'callsite': hex(i.address)})
    record['verified_direct_callers_nonexhaustive'] = callers
(OUT / 'disassembly.txt').write_text('\n'.join(disassembly)+'\n')

STUBS = {0x43d0ce:'log_flags', 0x43d574:'log', 0x43ce9e:'compact_log', 0x43dacc:'uuid_log',
         0x4b6ec6:'conn_in_use', 0x4b73c4:'conn_role', 0x4b579c:'write_req',
         0x4c543e:'ring_event', 0x4c548c:'ring_rx', 0x476ace:'remove_delayed',
         0x47697e:'push_delayed', 0x539dea:'write_cmd', 0x4d0c36:'tx_complete',
         0x4d0b64:'tx_wait', 0x4bf99e:'alloc', 0x4bf9ba:'msg_send', 0x5332b4:'discover'}

class Machine:
    def __init__(self, conn=1, epoch=7, in_use=1, role=0, alloc=True):
        self.uc = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
        self.uc.mem_map(0x437000, 0x35e000)
        self.uc.mem_write(BASE, BLOB)
        self.uc.mem_map(0x20000000, 0x100000)
        self.uc.mem_map(STOP, 0x1000)
        self.uc.mem_write(CTX, struct.pack('<BBHIH', conn, 9, 0, HANDLES, epoch))
        self.uc.mem_write(HANDLES, struct.pack('<HHH', 0x10, 0x12, 0x13))
        self.uc.mem_write(DATA, b'\x61\x02\x03\x04')
        self.in_use, self.role, self.alloc = in_use, role, alloc
        self.calls = []
        self.uc.hook_add(unicorn.UC_HOOK_CODE, self.hook)
    def hook(self, uc, address, size, unused):
        if address not in STUBS:
            # All executed code must be in this recovered cluster or a declared stub.
            assert 0x4c46c0 <= address < 0x4c4c66, hex(address)
            return
        name = STUBS[address]
        args = [uc.reg_read(r) for r in REGS]
        ret = 0
        if name == 'conn_in_use': ret = self.in_use
        if name == 'conn_role': ret = self.role
        if name == 'alloc': ret = ALLOC if self.alloc else 0
        call = {'call':name, 'args':args}
        if name == 'write_req': call['value_hex'] = bytes(uc.mem_read(args[3],args[2])).hex()
        if name == 'msg_send': call['message_hex'] = bytes(uc.mem_read(args[1],12)).hex()
        if name == 'discover':
            call['stack_args'] = list(struct.unpack('<II', uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)))
            call['uuid_hex'] = bytes(uc.mem_read(args[2],args[1])).hex()
        if name not in ('log_flags','log','compact_log','uuid_log'): self.calls.append(call)
        uc.reg_write(UC_ARM_REG_R0, ret)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    def run(self, address, *args):
        self.uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
        self.uc.reg_write(UC_ARM_REG_LR, STOP | 1)
        for r,v in zip(REGS, args): self.uc.reg_write(r,v)
        self.uc.emu_start(address | 1, STOP, count=20000)
        assert self.uc.reg_read(UC_ARM_REG_PC) == STOP, 'instruction budget exhausted'
        return self.uc.reg_read(UC_ARM_REG_R0)
    def message(self, event, conn=1, status=0, handle=0x12):
        self.uc.mem_write(MSG, struct.pack('<HBBIHH', conn,event,status,DATA,4,handle))
    def calls_named(self, name): return [c for c in self.calls if c['call']==name]

cases = []
def save(name, m): cases.append({'case':name, 'calls':m.calls})

m=Machine(); assert m.run(0x4c46c0,0x34,1,0xabcd)==0xabcd0134;save('pack_epoch',m)
m=Machine();m.run(0x4c4810,9,HANDLES)
assert bytes(m.uc.mem_read(CTX,10))==struct.pack('<BBHIH',0,9,0,HANDLES,1)
assert bytes(m.uc.mem_read(HANDLES,6))==struct.pack('<HHH',0x10,0x12,0x13);save('initialize_defaults',m)
m=Machine();m.run(0x4c487c,1,HANDLES)
c=m.calls_named('discover')[0];assert c['args']==[1,16,0x7880b0,3] and c['stack_args']==[0x200030d8,HANDLES];save('discovery_six_arguments',m)
for label,token,kw,zero,expect in [
    ('valid_initial',0x70001,{},False,True),('valid_final',0x70101,{},False,True),
    ('stale_epoch',0x60001,{},False,False),('wrong_connection',0x70002,{},False,False),
    ('zero_connection',0x70000,{},False,False),('closed_connection',0x70001,{'in_use':0},False,False),
    ('missing_cccd',0x70001,{},True,False)]:
    m=Machine(**kw)
    if zero:m.uc.mem_write(HANDLES+4,b'\0\0')
    m.run(0x4c46d0,token)
    writes=m.calls_named('write_req');assert bool(writes)==expect
    if expect: assert writes[0]['args'][:3]==[1,0x13,2] and writes[0]['value_hex']=='0100'
    assert bool(m.calls_named('ring_event'))==(label=='valid_final')
    save(label,m)
for event in (0x27,0x28):
    m=Machine();m.message(event);m.run(0x4c4910,0,MSG)
    assert struct.unpack('<H',m.uc.mem_read(CTX+8,2))[0]==8
    if event==0x27:
        calls=m.calls_named('push_delayed');assert [c['args'][:3] for c in calls]==[[0x4c46d1,0x80001,500],[0x4c46d1,0x80001,700],[0x4c46d1,0x80101,900]]
    else:
        assert bytes(m.uc.mem_read(HANDLES,6))==bytes(6) and m.calls_named('ring_event')[0]['args'][0]==8
    save('open' if event==0x27 else 'close',m)
m=Machine(epoch=65535);m.message(0x27);m.run(0x4c4910,0,MSG);assert bytes(m.uc.mem_read(CTX+8,2))==b'\0\0';save('epoch_wrap',m)
m=Machine(role=1);m.message(0x27);m.run(0x4c4910,0,MSG);assert not m.calls_named('push_delayed');save('peripheral_open_ignored',m)
for event,status,handle,expected in [(5,0,0x12,True),(13,0,0x12,True),(14,0,0x12,True),(5,1,0x12,False),(5,0,0x10,False)]:
    m=Machine();m.message(event,status=status,handle=handle);m.run(0x4c4910,0,MSG)
    assert bool(m.calls_named('ring_rx'))==expected
    save('rx_%02x_status%d_handle%x'%(event,status,handle),m)
# This local layer does not compare RX hdr.param against its active connection.
m=Machine();m.message(5,conn=2);m.run(0x4c4910,0,MSG);assert m.calls_named('ring_rx');save('rx_other_conn_reaches_local_handler',m)
for conn in (1,2):
    m=Machine();m.message(0xac,conn=conn);m.run(0x4c4910,0,MSG)
    assert bool(m.calls_named('write_cmd'))==(conn==1)
    assert bool(m.calls_named('tx_complete'))==(conn!=1)
    save('tx_event_conn%d'%conn,m)
for name,kw in [('send_queued',{}),('send_no_connection',{'conn':0}),('send_alloc_failure',{'alloc':False})]:
    m=Machine(**kw);assert m.run(0x4c4b7e,DATA,4)==0
    if name=='send_queued':
        packet=bytes.fromhex(m.calls_named('msg_send')[0]['message_hex'])
        assert packet[:3]==b'\1\0\xac' and struct.unpack_from('<I',packet,4)[0]==DATA and struct.unpack_from('<H',packet,8)[0]==4
    if name=='send_alloc_failure':assert m.calls_named('tx_complete')
    if name=='send_no_connection':assert not m.calls_named('tx_wait')
    save(name,m)
# Authenticate the existing decoded initializer before reading the pointer table.
ram_path=ROOT/'g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-main-canonical-replay-009/001/decoded-20000000.bin'
ram=ram_path.read_bytes();assert hashlib.sha256(ram).hexdigest()=='df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743'
ptrs=struct.unpack_from('<III',ram,0x30d8);assert ptrs==(0x78dfcc,0x78dfd4,0x78dfdc)
assert [u32(p) for p in ptrs]==[0x7880c0,0x7880d0,0x78f540]
constants=[{'address':hex(a),'wire_hex':code(a,a+16).hex(),'uuid':str(uuid.UUID(bytes=code(a,a+16)[::-1]))} for a in (0x7880b0,0x7880c0,0x7880d0)]
report={'input':str(PAYLOAD.relative_to(ROOT)), 'sha256':SHA,'mapping_base':hex(BASE),
        'capstone_version':capstone.__version__,'unicorn_version':unicorn.__version__,
        'scope':'Original seven function bodies; external calls stubbed; no radio/RTOS/timing model.',
        'functions':records,'uuid_constants':constants,'discovery_descriptor_addresses':[hex(p) for p in ptrs],
        'cases':cases,'case_count':len(cases)}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(cases),'original-code scenarios;',len(records),'function byte hashes; UUID/table checks')
