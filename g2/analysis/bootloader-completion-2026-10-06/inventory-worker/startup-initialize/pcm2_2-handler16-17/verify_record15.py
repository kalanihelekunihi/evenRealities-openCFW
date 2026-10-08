#!/usr/bin/env python3
"""Verify selector-15 against authenticated stock instructions and source ELF."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
FUNCTIONS=ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl'
SELECTORS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json'
NATIVE_BINDINGS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-relocated/native-selector-bindings.json'
ELF_READER=ROOT/'g2/components/bootloader/update_core/elf_reader.py'
IMAGE_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRY,END,DIGEST=0x429524,0x429624,'b9c0d1de31402701d130b56442cb955fe92c59ce4973cfc4a79652df8a6e23be'
STOP=0x08000000
STATE=[0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4,
       0x40020044,0x40020048,0x40020080,0x400083e0,0x40008064,0x20026c04,
       0x400083e8,0x40008010,0x40008068,0x4002037c,0x40021000,0x2000055a,
       0xe000e108,0xe000e188,0xe000e288]
spec=importlib.util.spec_from_file_location('elf_reader',ELF_READER)
er=importlib.util.module_from_spec(spec); spec.loader.exec_module(er)
def p32(x): return struct.pack('<I',x&0xffffffff)
def pack(vddf,active,tempco,vddc): return (vddf&127)|((active&1023)<<7)|((tempco&15)<<17)|((vddc&127)<<21)
def fixtures():
    rows=[]
    for i,(new,old) in enumerate(((3,0),(0,3),(1,2),(7,4),(19,20),(20,1),(11,8),(15,14))):
        prof=[pack((13+7*i+11*j)&127,(31+43*i+71*j)&1023,(i+3*j)&15,(17+9*i+13*j)&127) for j in range(21)]
        lv=sum(((i*31+j*41)&127)<<(7*j) for j in range(4))
        rows.append(dict(name=f'profile-{i}-states-{new}-{old}',args=[new,old,(i+2)&7,(i+3)&7],profiles=prof,low_voltage=lv,timer_control=0,timer_status=0,mode=(i&3)<<3))
    for state in (2,7,26):
      for ready in (True,False):
        i=state+(1 if ready else 7)
        prof=[pack((13+7*i+11*j)&127,(31+43*i+71*j)&1023,(i+3*j)&15,(17+9*i+13*j)&127) for j in range(21)]
        lv=sum(((i*11+j*37)&127)<<(7*j) for j in range(4))
        rows.append(dict(name=f'timer-state-{state}-ready-{int(ready)}',args=[3,0,2,5],profiles=prof,low_voltage=lv,timer_control=0x80001235,timer_status=0x40000000 if ready else 0,mode=0,timer_state=state,clock_user=True))
    return rows
def seed(u,f):
    info=bytearray(0x6c); struct.pack_into('<I',info,0,0x1f01600d)
    for i,w in enumerate(f['profiles']): struct.pack_into('<I',info,4+4*i,w)
    struct.pack_into('<I',info,0x64,f['low_voltage']); u.mem_write(0x20026ba0,bytes(info))
    for addr in STATE: u.mem_write(addr,p32(0x5a5a0000|(addr&0xffff)))
    u.mem_write(0x40021000,p32(f['mode'])); u.mem_write(0x400083e0,p32(f['timer_control']))
    u.mem_write(0x40008064,p32(f['timer_status'])); u.mem_write(0x400083e8,p32(0x1234))
    u.mem_write(0x40008010,p32(0x8000)); u.mem_write(0x40008068,p32(0x76543210))
    u.mem_write(0x4002037c,p32(0xa5123456)); u.mem_write(0x40004030,p32(0x01000000)); u.mem_write(0x40004044,p32(0x20))
    u.mem_write(0x20000550,b'\x01'); u.mem_write(0x20027030,p32(0)); u.mem_write(0x20027044,p32(0))
    u.mem_write(0x2002719c,b'\0'); u.mem_write(0x2002719e,b'\0'); u.mem_write(0x20026e74,bytes(56))
    u.mem_write(0x47ff0000,p32(0x12345678)); u.mem_write(0x2000055a,bytes([f.get('timer_state',0)]))
    if f.get('clock_user'): u.mem_write(0x20026ea8,p32(1<<17))
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000); u.reg_write(a.UC_ARM_REG_LR,STOP|1); u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    for i,v in enumerate(f['args']): u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),v)
def initialize_table(u,stock,image,segments,symbols,stock_raw=None):
    u.mem_write(0x20000000,b'\xa5'*1372);u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    if stock:
        u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0);entry=0x415326
    else:
        assert 'opencfw_boot_install_initialized_data' in symbols
        for reg in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3):u.reg_write(reg,0)
        entry=symbols['opencfw_boot_install_initialized_data']&~1
    done=[False]
    def hook(cpu,pc,size,_):
        if pc==STOP:done[0]=True;cpu.emu_stop();return
        if not stock and 0x410000<=pc<0x435000:raise AssertionError(f'source installer executed locked bytes at {pc:#x}')
    h=u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(entry|1,0,count=200000);u.hook_del(h);assert done[0],('initialized-data installer did not return',stock)
    raw=bytes(u.mem_read(0x20000000,1371));pad=u.mem_read(0x20000000+1371,1)[0]
    assert pad==0xa5
    table_receipt=json.loads(SELECTORS.read_text());targets=[int(x['thumb_target'],16) for x in table_receipt['selectors']]
    bindings=json.loads(NATIVE_BINDINGS.read_text())['slots']
    if stock:
        assert hashlib.sha256(raw).hexdigest()==table_receipt['output_sha256']
        return {'raw':raw,'sha256':hashlib.sha256(raw).hexdigest(),'normalized_sha256':hashlib.sha256(raw).hexdigest(),'table_sha256':hashlib.sha256(raw[0x158:0x158+108]).hexdigest(),'slot16':struct.unpack_from('<I',raw,0x158+16*4)[0],'padding_byte':pad}
    normalized=bytearray(raw)
    for slot,name in bindings.items():
        offset=0x158+4*int(slot);actual=struct.unpack_from('<I',raw,offset)[0]
        assert name in symbols and actual==(symbols[name]|1),(slot,hex(actual),name,hex(symbols.get(name,0)))
        normalized[offset:offset+4]=p32(targets[int(slot)])
    assert stock_raw is not None and bytes(normalized)==stock_raw
    return {'raw':raw,'normalized_sha256':hashlib.sha256(normalized).hexdigest(),'sha256':hashlib.sha256(raw).hexdigest(),'table_sha256':hashlib.sha256(raw[0x158:0x158+108]).hexdigest(),'slot16':struct.unpack_from('<I',raw,0x158+16*4)[0],'padding_byte':pad}
def run(stock,image,source_segments,symbols,f,stock_raw=None):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS); u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,sz in [(0,0x1000),(0x08000000,0x1000),(0x10000,0x40000),(0x20000000,0x40000),(0x40000000,0x100000),(0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]: u.mem_map(lo,sz)
    if stock: u.mem_write(0x410000,image); start=ENTRY
    else:
      for seg in source_segments: u.mem_write(seg['address'],seg['data'])
      start=symbols['opencfw_spot_pcm22_transition15']&~1
    table=initialize_table(u,stock,image,source_segments,symbols,stock_raw)
    seed(u,f); writes=[]; waits=[]; visited=set(); done=[False]
    def code(uc,pc,size,_):
      if pc==STOP: done[0]=True; uc.emu_stop(); return
      if pc==0x40:
        waits.append(uc.reg_read(a.UC_ARM_REG_R0)); uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR)); return
      if stock and ENTRY<=pc<END: visited.update(range(pc,pc+size))
      if not stock and 0x410000<=pc<0x435000: raise AssertionError(f'source entered locked code {pc:#x}')
    def wr(uc,access,addr,size,value,_):
      if 0x40000000<=addr<0x40100000 or 0xe0000000<=addr<0xe0020000: writes.append([addr,size,value&((1<<(8*size))-1)])
    u.hook_add(UC_HOOK_CODE,code); u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
    try: u.emu_start(start|1,0,count=5000000)
    except Exception as e: raise RuntimeError(f'{f["name"]} {"stock" if stock else "source"} PC={u.reg_read(a.UC_ARM_REG_PC):#x}') from e
    assert done[0],(f['name'],'not returned',hex(u.reg_read(a.UC_ARM_REG_PC)))
    result={'return':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],'state':{f'{ad:08x}':bytes(u.mem_read(ad,4)).hex() for ad in STATE},'writes':writes,'wait_cycles':waits,'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
    return result,visited,table
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base',type=Path); ap.add_argument('--addon',type=Path); ap.add_argument('--elf',type=Path); ap.add_argument('--output',type=Path,default=HERE/'comparison-record4b-direct15.json'); args=ap.parse_args()
    assert bool(args.elf) != bool(args.base or args.addon), 'use either --elf or both --base and --addon'
    image=IMAGE.read_bytes(); assert hashlib.sha256(image).hexdigest()==IMAGE_SHA
    if args.elf:
      _,segments,symbols=er.elf_info(args.elf); candidate=args.elf
    else:
      assert args.base and args.addon
      _,base_segs,base_syms=er.elf_info(args.base); _,add_segs,add_syms=er.elf_info(args.addon)
      segments=base_segs+add_segs; symbols={**base_syms,**add_syms}; candidate=args.base
    assert 'opencfw_spot_pcm22_transition15' in symbols
    records={int((d:=json.loads(l))['entry'],16):d for l in FUNCTIONS.read_text().splitlines()}
    rec=records[ENTRY]; body=image[ENTRY-0x410000:END-0x410000]
    selector_table=json.loads(SELECTORS.read_text())
    selector=next(x for x in selector_table['selectors'] if x['selector']==15)
    assert selector['entry']==hex(ENTRY) and selector['thumb_target']==hex(ENTRY|1)
    assert selector['body_bytes']==END-ENTRY and selector['body_sha256']==DIGEST
    assert int(rec['body_end_inclusive'],16)+1==END and len(body)==END-ENTRY and hashlib.sha256(body).hexdigest()==DIGEST
    assert hashlib.sha256(body[:-1]).hexdigest()!=DIGEST and hashlib.sha256(image[ENTRY-0x410000:END+1-0x410000]).hexdigest()!=DIGEST
    rows=[]; coverage=set(); initialized_stock=None
    for f in fixtures():
      stock,vis,stock_table=run(True,image,segments,symbols,f)
      if initialized_stock is None: initialized_stock=stock_table['raw']
      source,_,source_table=run(False,image,segments,symbols,f,initialized_stock)
      assert stock==source,(f['name'],stock,source)
      rows.append({'fixture':f,'result':stock,'initialized_data':{'stock_sha256':stock_table['sha256'],'source_sha256':source_table['sha256'],'normalized_sha256':source_table['normalized_sha256'],'source_slot15':hex(struct.unpack_from('<I',source_table['raw'],0x158+15*4)[0])}}); coverage|=vis
    out={'status':'PASS','image_sha256':IMAGE_SHA,'candidate_elf':str(candidate),'candidate_elf_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'entry':hex(ENTRY),'end_exclusive':hex(END),'bytes':END-ENTRY,'body_sha256':DIGEST,'visited_stock_bytes':len(coverage),'unvisited_addresses':[hex(x) for x in sorted(set(range(ENTRY,END))-coverage)],'cases':len(rows),'comparisons':rows,'limits':['Source machine executes only source ELF segments from the candidate and traps if PC enters locked image range.','The source initialized-data installer executes before fixture setup; callback table bytes are verified against the stock decoder after normalizing only authenticated source callback relocations.','ROM cycle-wait address 0x40 is the sole controlled peripheral timing boundary; actual stock handler and linked source delay/timer/clock routines execute. No hardware behavior or whole-firmware equivalence is claimed.']}
    args.output.write_text(json.dumps(out,indent=2)+'\n'); print('PASS',len(rows),'cases; stock instruction bytes visited',len(coverage),'/',END-ENTRY)
if __name__=='__main__': main()
