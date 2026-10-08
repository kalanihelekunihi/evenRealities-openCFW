#!/usr/bin/env python3
"""One natural selector-3 top-level callback using real initialized data."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE, arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
spec=importlib.util.spec_from_file_location('selector3_verify',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
IMAGE=v.IMAGE;TABLE=0x20000158;BASE=0x410000;EVENT_ENTRY=0x42a878
NATIVE_BINDINGS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-relocated/native-selector-bindings.json'

def r(u,p,n=4):return bytes(u.mem_read(p,n))
def r32(u,p):return struct.unpack('<I',r(u,p,4))[0]

def make_profile(u,initialized):
    vddc=struct.unpack_from('<21I',initialized,0xa4)
    vddf=struct.unpack_from('<21I',initialized,0xf4)
    profile=bytearray(0x80);struct.pack_into('<I',profile,0,0x1f01600d)
    for i in range(21):
        core=(i*37+11)&0x3ff;tempco=(i*3+5)&0xf
        word=(vddf[i]&0x7f)|(core<<7)|(tempco<<17)|((vddc[i]&0x7f)<<21)
        struct.pack_into('<I',profile,4+4*i,word)
    struct.pack_into('<I',profile,0x60,0x12345678) # synthetic INFO1 TON field
    struct.pack_into('<I',profile,0x64,0x0a654321) # synthetic packed VDDCLV trims
    u.mem_write(0x20026ba0,bytes(profile))
    return hashlib.sha256(profile).hexdigest()

def seed_runtime(u):
    u.mem_write(0x2002708c,b'\0');u.mem_write(0x200271be,b'\0')
    u.mem_write(0x200271bd,b'\x02');u.mem_write(0x200271a5,b'\0')
    u.mem_write(0x200271af,b'\xa5');u.mem_write(0x200271b0,b'\xa5')
    for p,val in [(0x40021108,0x30),(0x40021000,0),(0x40008800,0),
                  (0x400204d8,0),(0x40008010,0),(0x40021008,0x00400000),
                  (0x40021010,0),(0x40021018,0),(0x40021028,0),
                  (0x400083e0,0),(0x40008064,0),(0x4002004c,0x5a5a1234),
                  (0x40020344,0x13572468),(0x40020358,0x24681357),
                  (0x40004030,0x01000000),(0x40004044,0x20)]:u.mem_write(p,struct.pack('<I',val))
    u.mem_write(0x20001000,struct.pack('<III',struct.unpack('<I',struct.pack('<f',-100.0))[0],0xaaaaaaaa,0x55555555))

def run(stock,image,base_segments,addon_segments,base_symbols,addon_symbols,expected_stock_data):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,sz in [(0,0x1000),(0x08000000,0x1000),(0x10000,0x40000),
                  (0x20000000,0x40000),(0x40000000,0x100000),
                  (0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]:u.mem_map(lo,sz)
    if stock:
        u.mem_write(BASE,image);segments=base_segments;symbols=base_symbols
    else:
        segments=base_segments+addon_segments;symbols={**base_symbols,**addon_symbols}
        for seg in segments:u.mem_write(seg['address'],seg['data'])
    raw=v.init_image(u,stock,image,segments,symbols)
    if stock:
        assert v.sha(raw)==v.EXPECTED_DATA
        assert expected_stock_data is None or raw==expected_stock_data
        installed=raw
    else:
        bindings=json.loads(NATIVE_BINDINGS.read_text())['slots']
        normalized=bytearray(raw)
        for slot,name in bindings.items():
            off=0x158+4*int(slot);actual=struct.unpack_from('<I',raw,off)[0]
            assert actual==(base_symbols[name]|1),(slot,name,hex(actual))
            struct.pack_into('<I',normalized,off,struct.unpack_from('<I',expected_stock_data,off)[0])
        assert bytes(normalized)==expected_stock_data
        installed=raw
    assert r32(u,0x20000150)==7 and r32(u,0x20000148)==7
    assert r32(u,0x2000014c)==6 and r32(u,0x20000154)==255
    profile_hash=make_profile(u,installed);seed_runtime(u)
    if not stock:
        # Isolated test binding only: use the real source-owned installer and
        # its verified relocations, then replace exactly selector 3 for this
        # harness run. No repository/shared table or candidate is modified.
        slot=addon_symbols['opencfw_spot_pcm22_transition3']|1
        u.mem_write(TABLE+12,struct.pack('<I',slot))
    targets=[r32(u,TABLE+4*i) for i in range(27)]
    assert len(targets)==27 and (targets[3]&~1)==(v.ENTRY if stock else (addon_symbols['opencfw_spot_pcm22_transition3']&~1))
    calls=[];waits=[];writes=[];done=[False];unknown=[None]
    def code(cpu,pc,size,_):
        if (pc&~1)==v.STOP:done[0]=True;cpu.emu_stop();return
        if pc==0x40:
            waits.append(cpu.reg_read(a.UC_ARM_REG_R0))
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        for i,t in enumerate(targets):
            if pc!=(t&~1):continue
            call={'selector':i,'pc':hex(pc),'args':[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{k}')) for k in range(4)],
                  'caller_return':hex(cpu.reg_read(a.UC_ARM_REG_LR)&~1),
                  'sp':hex(cpu.reg_read(a.UC_ARM_REG_SP)),
                  'primask':cpu.reg_read(a.UC_ARM_REG_PRIMASK)}
            calls.append(call)
            if i==3 or (i in (24,25,26)):
                return
            unknown[0]=call;cpu.emu_stop();return
    def write(cpu,access,addr,size,value,_):
        if 0x40000000<=addr<0x40100000:
            writes.append([addr,size,value&((1<<(8*size))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x400fffff)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,0);u.reg_write(a.UC_ARM_REG_R0,2)
    u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R2,0x20001000)
    entry=EVENT_ENTRY if stock else base_symbols['opencfw_boot_spotmgr_power_state_update_a']&~1
    try:u.emu_start(entry|1,0,count=500000)
    except Exception as exc:raise RuntimeError(('stock' if stock else 'source','fault',hex(u.reg_read(a.UC_ARM_REG_PC)))) from exc
    completed=done[0] or (u.reg_read(a.UC_ARM_REG_PC)&~1)==v.STOP
    return {'side':'stock' if stock else 'source','profile_sha256':profile_hash,
        'table_sha256':hashlib.sha256(r(u,TABLE,108)).hexdigest(),
        'slot3':hex(targets[3]),'calls':calls,'unknown_frontier':unknown[0],
        'completed':completed,'status':u.reg_read(a.UC_ARM_REG_R0),
        'state':{'major':r32(u,0x20000150),'minor':r32(u,0x200001c4),
            'ton':r32(u,0x2000014c),'timer':r32(u,0x20000154),
            'state_words':{f'{p:08x}':r(u,p,4).hex() for p in
                (0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4)}},
        'arguments_after':r(u,0x20001000,12).hex(),'waits':waits,'mmio_writes':writes,
        '_initialized':installed}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True)
    ap.add_argument('--addon',type=Path,default=HERE/'handler3-addon.elf')
    ap.add_argument('--output',type=Path,default=HERE/'comparison-natural.json');args=ap.parse_args()
    image=IMAGE.read_bytes();assert v.sha(image)==v.IMAGE_SHA
    base_hash=hashlib.sha256(args.base.read_bytes()).hexdigest();assert base_hash==v.BASE_ELF_SHA
    _,base_segments,base_symbols=v.er.elf_info(args.base);_,addon_segments,addon_symbols=v.er.elf_info(args.addon)
    stock=run(True,image,base_segments,addon_segments,base_symbols,addon_symbols,None)
    expected=stock.pop('_initialized')
    source=run(False,image,base_segments,addon_segments,base_symbols,addon_symbols,expected)
    source.pop('_initialized')
    assert [c['selector'] for c in stock['calls']]==[3],stock['calls']
    assert len(stock['calls'])==1 and stock['calls'][0]['selector']==3,stock['calls']
    assert stock['completed'] and source['completed'] and stock['unknown_frontier'] is None and source['unknown_frontier'] is None
    assert stock['status']==source['status']==0,(stock['status'],source['status'],stock['calls'],source['calls'])
    assert stock['state']==source['state'] and stock['arguments_after']==source['arguments_after']
    assert stock['mmio_writes']==source['mmio_writes']
    result={'status':'PASS','base_elf_sha256':base_hash,'addon_elf_sha256':v.sha(args.addon.read_bytes()),
        'image_sha256':v.IMAGE_SHA,'initializer_sha256':v.EXPECTED_DATA,
        'natural_fixture':{'stimulus':'temperature','temperature_c':-100.0,
            'current_major':7,'target_major':19,'current_minor':6,'target_minor':6,
            'state_flag':0,'device_power':0x00400000},
        'source_table_binding':'After running the real source-owned data installer and validating normalized data/table, the test changes only installed slot 3 to the new addon symbol in this emulator run. No shared initializer/table source or frozen base ELF is changed.',
        'comparison':{'stock':stock,'source':source},
        'limits':['Stock callback/walker/selector/handler instructions run from the authenticated firmware. Source callback and walker run from frozen 4b source ELF; only selector3 is supplied by the separately frozen addon.',
            'ROM cycle-wait at 0x40 returns immediately with R0 preserved and logs the argument; this is the only absent external boundary. Timer is disabled, so timer service is not called.',
            'INFO1 profile core/tempco and packed VDDCLV values are synthetic; VDDC/VDDF rank fields come from decoded initializer data. MMIO values and outcomes are deterministic offline fixtures, not physical hardware behavior.']}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS natural selector3 callback; args',stock['calls'][0]['args'],'state major',stock['state']['major'])
if __name__=='__main__':main()
