#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded keyword registration/listing with an independent live-state model."""
import json,re,shutil,struct,subprocess
from build_gx8002_max_list_candidate import ROOT,IMAGE,build,MESSAGES
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import sha
MASK=0xffffffff
DELTA=0x101f6a74
COUNT=0x2002e79c
POINTER=COUNT+4
TABLE=0x20026c7c
ALTERNATE=0x21000000
FORMATS=[a for _,a,_ in MESSAGES]

class Memory:
    def __init__(self,seed,changes):
        self.data={COUNT:seed,POINTER:seed^MASK};self.trace=[];self.changes=changes;self.calls=0
        for table in (TABLE,ALTERNATE):
            for i in range(2):
                for offset in (76,80):self.data[table+i*88+offset]=(seed^table^(i*0x7654321)^offset)&MASK
    def read(self,address):
        if address not in self.data:raise ValueError('list invalid read/storage')
        value=self.data[address];self.trace.append(['read',address,value]);return value
    def write(self,address,value):
        if address not in (COUNT,POINTER):raise ValueError('list invalid state write')
        self.data[address]=value;self.trace.append(['write',address,value])
    def printf(self,fmt,arg):
        if fmt not in FORMATS:raise ValueError('list format')
        self.trace.append(['printf',fmt]+([] if fmt==FORMATS[4] else [arg]))
        # Explicit valid-storage domain; no clamping of corrupt live counts.
        for address,value in self.changes.get(self.calls,[]):
            if (address==COUNT and value not in (0,1,2)) or (address==POINTER and value not in (TABLE,ALTERNATE)) or address not in (COUNT,POINTER):raise ValueError('list mutation outside valid storage')
            self.data[address]=value;self.trace.append(['helper_write',address,value])
        self.calls+=1

def expected(seed,changes):
    m=Memory(seed,changes);m.write(COUNT,2);m.write(POINTER,TABLE);m.printf(FORMATS[0],2);i=0
    while i<m.read(COUNT):
        m.printf(FORMATS[1],m.read(POINTER)+i*88)
        m.printf(FORMATS[2],m.read(m.read(POINTER)+i*88+80))
        m.printf(FORMATS[3],m.read(m.read(POINTER)+i*88+76))
        m.printf(FORMATS[4],None);i+=1
    return m.trace,m.data

def execute(code,pc,delta,seed,changes):
    m=Memory(seed,changes);r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;condition=False
    for _ in range(300):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r4-r10, r15':raise ValueError('list frame')
            saved={f'r{i}':r[f'r{i}'] for i in (*range(4,11),15)};r['r14']-=32
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('list memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=m.read(address)
            else:m.write(address,r[reg])
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-32:raise ValueError('list call frame')
            if (int(args,0)+delta)&MASK!=0x10206c24:raise ValueError('list unknown helper')
            m.printf(r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^(m.calls*7919)^i)&MASK
        elif op=='pop':
            if saved is None or args!='r4-r10, r15' or r['r14']!=initial['r14']-32:raise ValueError('list return frame')
            r.update(saved);r['r14']+=32
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('list ABI')
            return m.trace,m.data
        else:raise ValueError('unknown list instruction '+op)
        pc=nxt
    raise ValueError('list execution bound')

def scenarios():
    yield {}
    for call in range(9):
        for count in range(3):
            for table in (TABLE,ALTERNATE):yield {call:[(COUNT,count),(POINTER,table)]}
    # Alternating pointer changes at every call, with shrink/restore at different boundaries.
    for shrink in range(9):
        for restore in range(shrink+1,9):
            changes={i:[(POINTER,ALTERNATE if i%2==0 else TABLE)] for i in range(9)}
            changes[shrink].append((COUNT,1));changes[restore].append((COUNT,2));yield changes

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'max-list-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11e0c','--stop-address=0x11e84',str(w)],text=True));new=decode((out/'max-list-candidate.disassembly.txt').read_text());cases=0
    for seed in (0,1,0x7fffffff,0x80000000,0xffffffff,0x12345678):
        for changes in scenarios():
            wanted=expected(seed,changes)
            for code,pc,delta in ((old,0x11e0c,DELTA),(new,0x10208880,0)):
                if execute(code,pc,delta,seed,changes)!=wanted:raise ValueError('list trace/state mismatch')
            cases+=1
    rows=[]
    for region in evidence['regions']:
        is_data=region['section_name']!='.text'
        if not region['fits'] or (is_data and not region['exact_stock_payload']):raise ValueError('list region validation')
        symbol='open_cfw_gx8002_max_list_'+region['section_name'].split('.')[-1] if is_data else 'LvpPrintMaxKwsList'
        rows.append({'symbol':symbol,'section_name':region['section_name'],'ownership_kind':'generated_source_data' if is_data else 'compiled_c','compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':symbol,'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}]})
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-MAX-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'max-list-candidate.elf',output/'max-list.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':rows,'evidence':evidence,'cases':cases,'frame_bytes':32,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,'limits':['Live count 0..2 and pointers to valid two-record tables; corrupt/out-of-range storage is not clamped or qualified. Logging-boundary mutations model reload behavior, not arbitrary interrupt timing. Eight-byte NOBITS state is source-defined, adds no payload ownership bytes. Full MAX scoring, strategy and hardware execution remain unqualified.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-max-list-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
