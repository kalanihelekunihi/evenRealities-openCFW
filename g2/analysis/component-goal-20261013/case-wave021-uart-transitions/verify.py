#!/usr/bin/env python3
"""Actual UART/write/wait/tick graph with explicit ordinal register inputs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
import hashlib,json,itertools,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H.parent/'case-wave016-battery-measurement-abi/qualified/case.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
UART=0x20004000;REG=0x40013800;PAY=0x20005000;TICK=0x20000120;SP=0x20008000;STOP=0x2000f000
scenarios=[{'name':'immediate','delay':0,'timeout':0,'step':1},{'name':'one_poll','delay':1,'timeout':65535,'step':1},{'name':'three_polls','delay':3,'timeout':65535,'step':1},{'name':'equal_deadline_then_ready','delay':2,'timeout':2,'step':1},{'name':'zero_timeout','delay':1,'timeout':0,'step':1},{'name':'tx0_timeout','delay':0,'timeout':2,'step':1,'stuck':'tx0'},{'name':'tx1_timeout','delay':0,'timeout':2,'step':1,'stuck':'tx1'},{'name':'tc_timeout','delay':0,'timeout':2,'step':1,'stuck':'tc'},{'name':'infinite_release','delay':3,'timeout':0xffffffff,'step':1},{'name':'ore_rx_enabled','delay':5,'timeout':65535,'step':1,'ore':True,'rx':True},{'name':'ore_rx_disabled','delay':1,'timeout':65535,'step':1,'ore':True,'rx':False},{'name':'expired_before_ore','delay':5,'timeout':0,'step':1,'ore':True,'rx':True},{'name':'infinite_ignores_ore','delay':3,'timeout':0xffffffff,'step':1,'ore':True,'rx':True}]
rows=[]
def run(native,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
 else:
  for a,b in seg:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000);u.mem_write(UART,bytes([0xa5])*0xa0);payload=bytes((i*41+17)&255 for i in range(512));u.mem_write(PAY,payload)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 w(UART,REG);w(UART+8,c['word']);w(UART+16,c['parity']);w(UART+0x88,c['state']);w(UART+0x8c,0x22);w(UART+0x90,0x11223344);w(REG,0x1a0|(4 if c.get('rx') else 0));w(REG+8,1);w(REG+32,0xabcdef00);w(TICK,c['start']);u.reg_write(UC_ARM_REG_PRIMASK,c['primask'])
 writes=[];polls={};ticks=0
 def before_read(uc,access,address,size,value,data):
  nonlocal ticks
  if address==TICK:
   w(TICK,c['start']+max(0,ticks)*c['step']);ticks+=1
  if address==REG+28:
   count=struct.unpack('<H',bytes(u.mem_read(UART+0x56,2)))[0];flag=0x80 if count else 0x40;stage='tx'+str(len([x for x in writes if x[0]==REG+40])) if count else 'tc';key=(stage,flag);n=polls.get(key,0);polls[key]=n+1
   ready=n>=c['delay'] and stage!=c.get('stuck');w(REG+28,(flag if ready else 0)|(0x800 if c.get('ore') else 0))
 def after_write(uc,access,address,size,value,data):
  if REG<=address<REG+64:writes.append((address,size,value))
 u.hook_add(UC_HOOK_MEM_READ,before_read);u.hook_add(UC_HOOK_MEM_WRITE,after_write)
 ptr=0 if c['pointer']=='null' else PAY+(1 if c['pointer']=='odd' else 0)
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[UART,ptr,c['length'],c['timeout']]):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start((0x080066ac if native else sym['case_write_controller_blocking'])|1,STOP,count=100000);assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP,(native,c,hex(u.reg_read(UC_ARM_REG_PC)))
 return {'return':u.reg_read(UC_ARM_REG_R0),'uart':bytes(u.mem_read(UART,0xa0)).hex(),'registers':bytes(u.mem_read(REG,64)).hex(),'payload':bytes(u.mem_read(PAY,512)).hex(),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'writes':writes,'tick_reads':ticks,'polls':[(a,b,n) for (a,b),n in polls.items()]}
for s,length,fmt,start,primask in itertools.product(scenarios,[1,2,5,17],[(0,0),(0x1000,0),(0x1000,0x400)],[0,0xfffffffe],[0,1]):
 c={**s,'length':length,'word':fmt[0],'parity':fmt[1],'start':start,'primask':primask,'state':0x20,'pointer':'aligned'};a=run(True,c);b=run(False,c)
 if a!=b:
  r={'status':'FAIL_NATIVE_SOURCE_UART_TRANSITIONS','case':c,'different_fields':[k for k in a if a[k]!=b[k]],'native':a,'source':b};(H/'failure.json').write_text(json.dumps(r,indent=2)+'\n');raise AssertionError((c,r['different_fields']))
 rows.append({'case':c,'return':a['return'],'TDR_writes':len([x for x in a['writes'] if x[0]==REG+40]),'tick_reads':a['tick_reads'],'polls':a['polls']})
for state,length,pointer,word in itertools.product([0,0x21,0x20],[0,1,5],['aligned','odd','null'],[0,0x1000]):
 c={**scenarios[0],'state':state,'length':length,'pointer':pointer,'word':word,'parity':0,'start':0,'primask':0};a=run(True,c);b=run(False,c);assert a==b,(c,a,b);rows.append({'case':c,'return':a['return'],'TDR_writes':len([x for x in a['writes'] if x[0]==REG+40])})
r={'status':'PASS_FULL_NATIVE_SOURCE_UART_TRANSITIONS','cases':len(rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'model':'Ordinal ISR reads supply readiness/error bits; actualtickgetter reads scriptedRAM tick progression. Actualsource/native write/wait/tick/cleanup bodies execute; nochildstubs/cuts/returninjection.','limits':['Syntheticordinal register/tick input model, notphysicalFIFOcapacity/latency/wire/IRQ proof.','Hardware W1C/ISR evolution otherthan specifiedinputs is not modeled; physicalclock/interruptarbitration notvalidated.','Infiniteunchangedwait excluded; infinite waitwithfinite scriptedrelease included.']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
