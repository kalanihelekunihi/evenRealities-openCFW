"""Actual PendSV save/select/restore instructions; stop before BX EXC_RETURN."""
from pathlib import Path
import argparse,importlib.util,json,struct,hashlib
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[6]
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
s=importlib.util.spec_from_file_location('er',ROOT/'g2/components/bootloader/update_core/elf_reader.py');er=importlib.util.module_from_spec(s);s.loader.exec_module(er)
_,segments,symbols=er.elf_info(args.elf)
b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
trace={}
def run(source,index,fp):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,n in [(0x10000,0x10000),(0x30000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0xe000e000,0x1000)]:u.mem_map(lo,n)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,b)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 old,new=0x20030000,0x20030100;os,ns=0x20031000,0x20032000;frame=ns+0x80
 for p,v in [(0x20027134,old),(0x2002716c,0),(0x20027170,index),(0x2002714c,0),(old+0x30,os),(new+0x30,ns),(old+0x58,100),(new+0x58,101),(new,frame)]:w(p,v)
 u.mem_write(os,b'\xa5'*16);u.mem_write(ns,b'\xa5'*16)
 u.mem_write(frame,struct.pack('<10I',ns,0xffffffed if fp else 0xfffffffd,*[0xb0000000+i for i in range(4,12)]))
 if fp:u.mem_write(frame+40,struct.pack('<16I',*[0x41000000+i for i in range(16)]))
 w(0xe000ed88,0x00f00000);u.reg_write(a.UC_ARM_REG_FPEXC,0x40000000)
 for i in range(16,32):u.reg_write(getattr(a,f'UC_ARM_REG_S{i}'),0x42000000+i)
 # Coherent ready list containing idle/new only; outgoing task already removed.
 l=0x20024870;end=l+8;item=new+4
 for p,v in [(l,1),(l+4,end),(end,0xffffffff),(end+4,item),(end+8,item),(item,0),(item+4,end),(item+8,end),(item+12,new),(item+16,l)]:w(p,v)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_PSP,os+0x180);u.reg_write(a.UC_ARM_REG_LR,0xffffffed if fp else 0xfffffffd)
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xa0000000+i)
 entry=(symbols['opencfw_boot_pendsv_entry']&~1) if source else 0x41b31c
 dis=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
 stop=next(x.address for x in dis.disasm(bytes(u.mem_read(entry,140)),entry) if x.mnemonic=='bx' and x.op_str=='r3')
 done=[False]
 def hook(cpu,pc,n,_):
  if not source:trace[pc]=bytes(cpu.mem_read(pc,n)).hex()
  if pc==stop:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry|1,0,count=10000);assert done[0]
 return {'current':struct.unpack('<I',u.mem_read(0x20027134,4))[0],'psp':u.reg_read(a.UC_ARM_REG_PSP),'basepri':u.reg_read(a.UC_ARM_REG_BASEPRI),'r3':u.reg_read(a.UC_ARM_REG_R3),'registers':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'outgoing_tcb_stack':bytes(u.mem_read(old,4)).hex(),'outgoing_saved_frame':bytes(u.mem_read(os+(0x118 if fp else 0x158),104 if fp else 40)).hex(),'history':bytes(u.mem_read(0x20026500,512)).hex(),'selection':bytes(u.mem_read(0x20024870,20)).hex(),'index':bytes(u.mem_read(0x20027170,4)).hex(),'fp_registers':[u.reg_read(getattr(a,f'UC_ARM_REG_S{i}')) for i in range(16,32)]}
rows=[]
for index in [0,63]:
 for fp in [False,True]:
  x,y=run(False,index,fp),run(True,index,fp);assert x==y,(x,y);assert x['current']==0x20030100 and x['psp']==0x200320a8+(64 if fp else 0) and x['r3']==(0xffffffed if fp else 0xfffffffd);rows.append({'index':index,'fp':fp,'result':x})
args.output.write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'original_trace':{hex(k):v for k,v in trace.items()},'comparisons':rows,'limits':['Actual basic/FP-high-register PendSV save/select/restore executes with synthetic coherent TCBs/ready lists and seeded PSP. Stops before BX EXC_RETURN; no architectural hardware stacking/unstacking or automatic task entry.','S16-S31 software save/restore executes for FType0; S0-S15/FPSCR architectural/lazy stacking, MVE/VPR state and exception unstacking are not emulated. No live IRQ/concurrency/hardware timing proof. Idle cleanup separately tested; this does not establish a real completed self-delete-to-idle lifecycle.']},indent=2)+'\n');print('PASS actual non-FP PendSV save/select/restore',len(rows),'cases')
