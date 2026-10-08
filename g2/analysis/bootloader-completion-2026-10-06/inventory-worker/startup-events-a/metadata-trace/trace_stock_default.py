#!/usr/bin/env python3
"""Trace the locked event-A callback from the authenticated 1,371-byte image.

The hook stops before the first installed callback instruction and records its
real arguments/caller. No opaque handler is supplied a fabricated return.
"""
from pathlib import Path
import hashlib, json, struct, argparse
import itertools
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
EXPECTED_IMAGE='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
EXPECTED_DATA='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
ENTRY,END=0x42a878,0x42ab6e
STOP=0x08000000
TABLE=0x20000158
OFFICIAL=IMAGE.read_bytes()
assert hashlib.sha256(OFFICIAL).hexdigest()==EXPECTED_IMAGE

def decode(data):
    cur=0; out=bytearray()
    def get():
        nonlocal cur
        assert cur<len(data), 'truncated stream'
        val=data[cur];cur+=1;return val
    while cur<len(data):
        control=get(); literal=control&3; run=control>>4
        if literal==0: literal=get()+3
        if run==15: run=get()+15
        for _ in range(literal-1): out.append(get())
        if run:
            lo=get(); hi=(control>>2)&3
            if hi==3: hi=get()
            dist=lo+256*hi
            assert 0<dist<=len(out)
            for _ in range(run+2): out.append(out[-dist])
        assert len(out)<=1371
    return bytes(out)

rec=struct.unpack_from('<III',OFFICIAL,0x433104-0x410000)
assert rec==(0x10bc,1250,0x20000000) and 0x433104+rec[0]==0x4341c0
data=decode(OFFICIAL[0x241c0:0x241c0+625])
assert len(data)==1371 and hashlib.sha256(data).hexdigest()==EXPECTED_DATA
targets=list(struct.unpack_from('<27I',data,0x158))
assert all((x&1) and 0x410000<=(x&~1)<0x434000 for x in targets)
assert all(OFFICIAL[(x&~1)-0x410000:(x&~1)-0x410000+2]==bytes.fromhex('7047') for x in targets[24:])

def w(u,p,v): u.mem_write(p,struct.pack('<I',v&0xffffffff))
def r32(u,p): return struct.unpack('<I',u.mem_read(p,4))[0]

def packed_profile(index):
    # Decoded rank bytes are actual initializer evidence. The other fields in
    # each profile word are labeled synthetic values for a nonuniform fixture.
    vddc=struct.unpack_from('<21I',data,0xa4)
    vddf=struct.unpack_from('<21I',data,0xf4)
    core=(index*37+11)&0x3ff
    tempco=(index*3+5)&0xf
    return ((vddf[index]&0x7f) | (core<<7) | (tempco<<17) |
            ((vddc[index]&0x7f)<<21))

def run(f):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,size in [(0x410000,0x25000),(0x08000000,0x1000),
                    (0x20000000,0x40000),(0x40000000,0x100000)]: u.mem_map(lo,size)
    u.mem_write(0x410000,OFFICIAL)
    u.mem_write(0x20000000,data)
    # Retain authentic callback table and all initialized state/default words.
    assert [r32(u,TABLE+4*i) for i in range(27)]==targets
    w(u,0x40021108,0x30)
    w(u,0x40021000,2)
    w(u,0x40008800,0)
    w(u,0x400204d8,0)
    w(u,0x40008010,0)
    # Installed profile magic and nonuniform packed profile input. This is an
    # explicit synthetic INFO profile, not recovered SDK profile content.
    profile=bytearray(0x80)
    struct.pack_into('<I',profile,0,0x1f01600d)
    for i in range(21): struct.pack_into('<I',profile,4+4*i,packed_profile(i))
    struct.pack_into('<I',profile,0x64,0x0a654321)
    u.mem_write(0x20026ba0,bytes(profile))
    w(u,0x40021008,f.get('device',0))
    w(u,0x40021010,f.get('audio',0))
    w(u,0x40021018,f.get('memory',0))
    w(u,0x40021028,f.get('ssram',0))
    # True decoder defaults remain untouched: power state=7, TON=6, timer=255.
    assert r32(u,0x20000150)==7 and r32(u,0x20000148)==7
    assert r32(u,0x2000014c)==6 and r32(u,0x20000154)==255
    u.mem_write(0x2002708c,bytes([f.get('state_flag',1)]))
    u.mem_write(0x200271be,bytes([f.get('current_cpu',0)]))
    u.mem_write(0x200271bd,bytes([f.get('current_temp',2)]))
    u.mem_write(0x200271a5,bytes([f.get('gpu_aux',0)]))
    u.mem_write(0x200271af,b'\xa5');u.mem_write(0x200271b0,b'\xa5')
    w(u,0x20001000,f['argument'])
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    u.reg_write(a.UC_ARM_REG_R0,f['stimulus'])
    u.reg_write(a.UC_ARM_REG_R1,f.get('on',0))
    u.reg_write(a.UC_ARM_REG_R2,0x20001000)
    hit=[]; done=[False]
    def hook(cpu,pc,size,_):
        if pc==STOP: done[0]=True;cpu.emu_stop();return
        if pc==ENTRY:
            pass
        for i,t in enumerate(targets):
            if pc==(t&~1):
                lr=cpu.reg_read(a.UC_ARM_REG_LR)&~1
                hit.append({
                    'selector':i,'target':hex(pc),'caller_return':hex(lr),
                    'args':[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{k}')) for k in range(4)],
                    'sp':hex(cpu.reg_read(a.UC_ARM_REG_SP)),
                    'primask':cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                    'caller_bytes':bytes(cpu.mem_read(lr-6,6)).hex(),
                    'state_at_entry':{'current_major':r32(cpu,0x20000150),
                        'current_ton':r32(cpu,0x2000014c),
                        'timer':r32(cpu,0x20000154)},
                })
                if i<24:
                    cpu.emu_stop();return
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(ENTRY|1,0,count=100000)
    except Exception as exc:
        return {'fixture':f,'fault':repr(exc),'pc':hex(u.reg_read(a.UC_ARM_REG_PC)),
                'callbacks':hit}
    return {'fixture':f,'completed_to_stop':done[0],'callbacks':hit,
            'status':u.reg_read(a.UC_ARM_REG_R0),
            'current_major':r32(u,0x20000150),'ton':r32(u,0x2000014c),
            'timer':r32(u,0x20000154)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE/'stock-default-trace.json');ap.add_argument('--sweep',action='store_true');args=ap.parse_args()
    fixtures=[]
    # Main natural route: temp classification selects a state from authentic
    # initial major 7, then the actual trim update and table walker run.
    for temp in (0.0,49.5,50.0,-20.0,-0.5,999.0):
        fixtures.append({'name':f'temp-{temp}','stimulus':2,
            'argument':struct.unpack('<I',struct.pack('<f',temp))[0],
            'current_cpu':0,'current_temp':2,'state_flag':1})
    # Also vary other genuine event inputs with unchanged decoded defaults.
    for stimulus,arg in [(0,0),(1,1),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0)]:
        fixtures.append({'name':f'event-{stimulus}','stimulus':stimulus,
            'argument':arg,'current_cpu':0,'current_temp':2,'state_flag':1})
    if args.sweep:
        for (label,bits),cpu,flag,dev,aux in itertools.product(
            [('class0',struct.unpack('<I',struct.pack('<f',-100.0))[0]),
             ('class1',struct.unpack('<I',struct.pack('<f',-10.0))[0]),
             ('class2',struct.unpack('<I',struct.pack('<f',20.0))[0]),
             ('class3',struct.unpack('<I',struct.pack('<f',100.0))[0]),
             ('class4',struct.unpack('<I',struct.pack('<f',2000.0))[0]),
             ],(0,1),(0,1),(0,0x400,0x400000,0x400400,0x40000,0x440000),
             (0,1)):
            fixtures.append({'name':f'sweep-{label}-cpu{cpu}-flag{flag}-dev{dev:x}-aux{aux}',
                'stimulus':2,'argument':bits,'current_cpu':cpu,
                'current_temp':2,'state_flag':flag,'device':dev,'gpu_aux':aux})
    rows=[run(f) for f in fixtures]
    out={'status':'OBSERVED','image_sha256':EXPECTED_IMAGE,
        'decoded_initializer_sha256':EXPECTED_DATA,'decoded_initializer_bytes':1371,
        'initializer_record':[hex(x) for x in rec],
        'callback_table':{'address':hex(TABLE),'targets':[hex(x) for x in targets]},
        'default_state':{'major':7,'minor_adjacent_word':7,'ton':6,'last_timer':255},
        'profile_note':'Nonuniform fixture profile uses actual decoded VDDC/VDDF rank words; core/tempco and VDDCLV fields are explicitly synthetic.',
        'trace_rule':'Original stock callback bytes only; stop before first table target instruction. No opaque return is fabricated.',
        'observations':rows}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print('OBSERVED',len(rows),'stock fixtures; selector hits',[(r['fixture']['name'],[(c['selector'],c['target']) for c in r['callbacks']]) for r in rows if r['callbacks']])
if __name__=='__main__': main()
