#!/usr/bin/env python3
"""Native/source config and motion transaction control at bus child cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_init_bus_transactions_candidate.c';obj=H/'application_init_bus_transactions.oracle.o';stub=H/'application_init_bus_transactions.oracle_stub.c';stubobj=H/'application_init_bus_transactions.oracle_stub.o';elf=H/'application_init_bus_transactions.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['case_bus_prepare','case_bus_finish','case_bus_send','case_bus_start','case_bus_poll','case_bus_read','case_bus_byte_sample','case_bus_response_bit','case_bus_output_finish','case_bus_output_send','case_bus_output_start','case_bus_output_poll','case_bus_output_parity','case_bus_output_byte_sample','case_bus_output_response_bit']
stub.write_text('#include <stdint.h>\n'+''.join('uint32_t '+n+'(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n' for n in names))
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={'prepare':0x0800a310,'finish':0x0800a24a,'send':0x0800a2c4,'start':0x0800a19a,'poll':0x0800c43c,'parity':0x0800c412,'sample':0x0800b5d6,'response':0x0800a176,'ofinish':0x0800a224,'osend':0x0800a2a2,'ostart':0x0800a188,'opoll':0x0800c42c,'oparity':0x0800c3f8,'osample':0x0800b5ac,'oresponse':0x0800a164}
source={sym[n]&~1:k for k,n in zip(native,['case_bus_prepare','case_bus_finish','case_bus_send','case_bus_start','case_bus_poll','case_bus_read','case_bus_byte_sample','case_bus_response_bit','case_bus_output_finish','case_bus_output_send','case_bus_output_start','case_bus_output_poll','case_bus_output_parity','case_bus_output_byte_sample','case_bus_output_response_bit'])}
native={v:k for k,v in native.items()}
rng=random.Random(0x0310)
for i in range(96):
 which=i&1;command=2 if which==0 else 0x5a;index=rng.randrange(8);count=i%3+1;failstage=(i//2)%8;pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,b'\xee'*8)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,command);u.reg_write(UC_ARM_REG_R1,index);u.reg_write(UC_ARM_REG_R2,count);u.reg_write(UC_ARM_REG_R3,0x20002000)
  cuts=native if original else source;trace=[];polls=0;samples=0
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
   if k in ('send','osend'):trace.append((k,r0,r1))
   elif k in ('start','ostart','response','oresponse','parity','oparity'):trace.append((k,r0))
   else:trace.append((k,))
   if k in ('poll','opoll'):
    n=sum(t[0] in ('poll','opoll') for t in trace)-1
    expected=([((command<<1)&255),index,((command<<1)+1)&255][n] if which==0 else (((command&~15)+index)*2+1)&255)
    parity=expected.bit_count()&1
    uc.mem_write(r0,struct.pack('<I',parity^(1 if failstage==n+3 else 0)))
    uc.reg_write(UC_ARM_REG_R0,0 if failstage==n else 1)
   elif k in ('parity','oparity'):uc.reg_write(UC_ARM_REG_R0,r0.bit_count()&1)
   elif k in ('sample','osample'):
    n=sum(t[0] in ('sample','osample') for t in trace)-1
    uc.mem_write(r0,bytes((0x40+n,)));uc.reg_write(UC_ARM_REG_R0,0 if failstage==6 and n==0 else 1)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=0x08000310 if which==0 else 0x08000420
  symbol='case_bus_config_input_transaction' if which==0 else 'case_motion_input_transaction'
  u.emu_start((entry if original else sym[symbol])|1,0x20008000,count=700)
  diag=0x2000007c if which==0 else 0x20000000
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(diag,12)),bytes(u.mem_read(0x20002000,8)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_INIT_BUS_TRANSACTIONS',96)
