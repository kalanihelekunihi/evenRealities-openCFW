#!/usr/bin/env python3
"""Compare stock selector 3 with an isolated source addon and native children."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE, arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
FUNCTIONS=ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl'
TABLE_RECEIPT=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json'
IMAGE_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
BASE_ELF_SHA='8d7f5748fa1d8fd2857bdf7a005766a2d4d191557ef0863d939165c823dc710d'
EXPECTED_DATA='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
ENTRY,END,DIGEST=0x428068,0x428240,'7828372b3a4b3704f7d9202a325edc738dcf1af81ad60af87d11495e284388ad'
STOP=0x08000000
STATE=[0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4,
       0x4002004c,0x400083e0,0x40008064,0x20026c04,0x400083e8,0x40008010,
       0x40008068,0x4002037c,0x40021000,0x2000055a]
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
er=importlib.util.module_from_spec(spec);spec.loader.exec_module(er)
from elftools.elf.elffile import ELFFile
_original_read=er.elf_info
def bounded_read(path):
    path=Path(path)
    if path.name!='handler1-addon.elf':return _original_read(path)
    with path.open('rb') as f:
        e=ELFFile(f);assert e.elfclass==32 and e['e_machine']=='EM_ARM'
        seg=[]
        for s in e.iter_segments():
            if s['p_type']!='PT_LOAD':continue
            assert 0x50000<=s['p_vaddr']<=s['p_vaddr']+s['p_memsz']<=0x51000
            seg.append({'address':s['p_vaddr'],'memory_size':s['p_memsz'],'data':s.data(),'flags':s['p_flags']})
        sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name and x['st_shndx']!='SHN_UNDEF'}
        return path.read_bytes(),seg,sy
er.elf_info=bounded_read


def p32(v): return struct.pack('<I',int(v)&0xffffffff)
def r32(u,p): return struct.unpack('<I',u.mem_read(p,4))[0]
def sha(b): return hashlib.sha256(b).hexdigest()

def pack(vddf,core,tempco,vddc):
    return (vddf&0x7f)|((core&0x3ff)<<7)|((tempco&0xf)<<17)|((vddc&0x7f)<<21)

def fixtures():
    result=[]
    states=[(19,7,6,6),(5,7,0,6),(3,0,2,5),(0,3,3,4),
            (15,14,7,2),(8,12,4,1)]
    for index,(new,old,newton,oldton) in enumerate(states):
        result.append({'name':f'profiles-{index}-states-{new}-{old}',
            'args':[new,old,newton,oldton],
            'profiles':[pack((13+7*index+11*j)&127,(31+43*index+71*j)&1023,
                            (index+3*j)&15,(17+9*index+13*j)&127) for j in range(21)],
            'low':sum(((index*31+j*41)&127)<<(7*j) for j in range(4)),
            'timer_control':0,'timer_status':0,'timer_state':0,'clock_user':False})
    # A ready timer entry exercises the linked timer-service dependency with
    # actual stock/native helper bodies; no timer result is stubbed.
    index=9;new,old=19,7
    result.append({'name':'timer-ready-state26','args':[new,old,6,6],
        'profiles':[pack((13+7*index+11*j)&127,(31+43*index+71*j)&1023,
                         (index+3*j)&15,(17+9*index+13*j)&127) for j in range(21)],
        'low':sum(((index*11+j*37)&127)<<(7*j) for j in range(4)),
        'timer_control':0x80001235,'timer_status':0x40000000,
        'timer_state':26,'clock_user':True})
    sat=dict(result[0],name='saturated-double-boost',profiles=[pack(0,200,3,0)]*21)
    sat['profiles'][sat['args'][0]]=pack(127,777,12,127)
    result.append(sat)
    timeout=dict(result[-2],name='timer-timeout60',timer_status=0)
    result.append(timeout)
    return [dict(f,cache=c,name=f["name"]+"-cache"+str(c)) for f in result for c in [0,0x20000]]

def init_image(u,stock,image,segments,symbols):
    u.mem_write(0x20000000,b'\xa5'*1372)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    if stock:
        u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0)
        u.reg_write(a.UC_ARM_REG_R9,0);entry=0x415326
    else:
        u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0)
        u.reg_write(a.UC_ARM_REG_R9,0);entry=symbols['opencfw_boot_expand_adapter']&~1
    done=[False]
    def hook(cpu,pc,size,_):
        if pc==STOP:done[0]=True;cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(entry|1,0,count=200000)
    assert done[0],('data initializer did not return',stock,hex(u.reg_read(a.UC_ARM_REG_PC)))
    raw=bytes(u.mem_read(0x20000000,1371));assert u.mem_read(0x20000000+1371,1)==b'\xa5'
    return raw

def seed(u,f):
    for addr in STATE:u.mem_write(addr,p32(0x5a5a0000|(addr&0xffff)))
    profile=bytearray(0x6c);struct.pack_into('<I',profile,0,0x1f01600d)
    for i,w in enumerate(f['profiles']):struct.pack_into('<I',profile,4+4*i,w)
    struct.pack_into('<I',profile,0x64,f['low']);u.mem_write(0x20026ba0,bytes(profile))
    # Deterministic peripheral and mutable-SPOT fixture; timer state is
    # synthetic and labeled in the receipt. All MMIO writes remain observable.
    for addr,val in [(0x400083e0,f['timer_control']),
                     (0x40008064,f['timer_status']),
                     (0x400083e8,0x1234),(0x40008010,0x8000),
                     (0x40008068,0x76543210),(0x4002037c,0xa5123456),
                     (0x40004030,0x01000000),(0x40004044,0x20),
                     (0x40021000,0),(0x20027030,0),(0x20027044,0),
                     (0x47ff0000,0x12345678)]:u.mem_write(addr,p32(val))
    u.mem_write(0x20000550,b'\x01');u.mem_write(0x2000055a,bytes([f.get('timer_state',0)]))
    u.mem_write(0x20026e74,bytes(56));u.mem_write(0x2002719c,b'\0');u.mem_write(0x2002719e,b'\0')
    if f.get('clock_user'):u.mem_write(0x20026ea8,p32(1<<17))
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    for i in range(4):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),f['args'][i])
    for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xa0000000+i)

def run(stock,image,base_segments,addon_segments,base_symbols,addon_symbols,f):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,sz in [(0,0x1000),(STOP,0x1000),(0x10000,0x50000),
                  (0x20000000,0x40000),(0x40000000,0x100000),
                  (0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]:u.mem_map(lo,sz)
    if stock:u.mem_write(0x410000,image);segments=base_segments
    else:
        segments=base_segments+addon_segments
        for seg in segments:u.mem_write(seg['address'],seg['data'])
    raw=init_image(u,stock,image,segments,{**base_symbols,**addon_symbols})
    if stock:assert sha(raw)==EXPECTED_DATA
    seed(u,f);u.mem_write(0xe000ed14,p32(f.get("cache",0)));writes=[];waits=[];visited=set();done=[False]
    start=ENTRY if stock else addon_symbols['opencfw_spot_pcm22_transition1']&~1
    def code(cpu,pc,size,_):
        if pc==STOP:done[0]=True;cpu.emu_stop();return
        if pc==0x40:
            waits.append(cpu.reg_read(a.UC_ARM_REG_R0))
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        if stock and ENTRY<=pc<END:visited.update(range(pc,min(pc+size,END)))
        if not stock and pc==ENTRY:raise AssertionError('source entered locked selector-1 entry')
    def write(cpu,access,addr,size,value,_):
        if 0x40000000<=addr<0x40100000 or 0xe0000000<=addr<0xe0020000:
            writes.append([addr,size,value&((1<<(8*size))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x400fffff)
    u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe0000000,end=0xe001ffff)
    try:u.emu_start(start|1,0,count=2000000)
    except Exception as exc:raise RuntimeError((f['name'],'stock' if stock else 'source',hex(u.reg_read(a.UC_ARM_REG_PC)))) from exc
    completed=done[0] or (u.reg_read(a.UC_ARM_REG_PC)&~1)==STOP
    assert completed,(f['name'],'did not return',hex(u.reg_read(a.UC_ARM_REG_PC)))
    out={'return':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],
         'state':{f'{ad:08x}':bytes(u.mem_read(ad,4)).hex() for ad in STATE},
         'writes':writes,'waits':waits,
         'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],
         'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
    return out,visited

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True)
    ap.add_argument('--addon',type=Path,default=HERE/'handler1-addon.elf')
    ap.add_argument('--output',type=Path,default=HERE/'comparison.json');args=ap.parse_args()
    image=IMAGE.read_bytes();assert sha(image)==IMAGE_SHA
    body=image[ENTRY-0x410000:END-0x410000]
    assert len(body)==472 and sha(body)==DIGEST
    assert sha(body[:-1])!=DIGEST and sha(image[ENTRY-0x410000:END+1-0x410000])!=DIGEST
    table=json.loads(TABLE_RECEIPT.read_text());assert table['status']=='PASS' and table['original_sha256']==IMAGE_SHA
    target=int(table['selectors'][1]['thumb_target'],16);assert target==(ENTRY|1)
    funcs={int((d:=json.loads(l))['entry'],16):d for l in FUNCTIONS.read_text().splitlines()}
    record=funcs[ENTRY];assert int(record['body_end_inclusive'],16)+1==END and record['body_bytes']==472
    assert set(record['callees'])=={'0041d1c0','0042a04a','0042a1bc','0041e22e','0041e1e8'}
    assert sha(args.base.read_bytes())==BASE_ELF_SHA
    _,base_segments,base_symbols=er.elf_info(args.base)
    _,addon_segments,addon_symbols=er.elf_info(args.addon)
    for sym in ('event_a_power_ton_adjust','opencfw_pcm22_timer_service','opencfw_hal_delay_us'):
        assert sym in base_symbols,sym
    assert 'opencfw_spot_pcm22_transition1' in addon_symbols
    rows=[];coverage=set()
    for f in fixtures():
        stock,vis=run(True,image,base_segments,addon_segments,base_symbols,addon_symbols,f)
        source,_=run(False,image,base_segments,addon_segments,base_symbols,addon_symbols,f)
        assert stock==source,(f['name'],stock,source)
        coverage|=vis;rows.append({'fixture':f,'result':stock})
    out={'status':'PASS','image_sha256':IMAGE_SHA,'base_elf_sha256':BASE_ELF_SHA,
         'addon_elf_sha256':sha(args.addon.read_bytes()),'target':hex(target),
         'entry':hex(ENTRY),'end_exclusive':hex(END),'body_bytes':len(body),
         'body_sha256':DIGEST,'visited_stock_bytes':len(coverage),
         'unvisited_stock_addresses':[hex(x) for x in sorted(set(range(ENTRY,END))-coverage)],
         'provider_frontier':['event_a_power_ton_adjust native base symbol',
             'opencfw_pcm22_timer_service native base symbol',
             'opencfw_hal_delay_us native base symbol'],
         'controlled_boundaries':['ROM cycle-wait address 0x40 immediately returns and records R0; no ROM call is expected on timer-disabled cases.',
             'MMIO values are deterministic synthetic fixture state; peripheral writes are recorded. Timer-ready fixture uses the real stock/source timer service and native sequence helpers.'],
         'limits':['Original selector-1 body extent/hash is independently authenticated against locked image and function corpus.',
             'No opaque success callback or timer-service result is substituted; only the absent ROM wait edge at 0x40 is returned immediately.',
             'Offline emulation only; no hardware or whole-firmware claim.'],
         'fixtures':rows}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print('PASS',len(rows),'direct selector1 fixtures; stock instruction bytes visited',len(coverage),'of',len(body))
if __name__=='__main__':main()
