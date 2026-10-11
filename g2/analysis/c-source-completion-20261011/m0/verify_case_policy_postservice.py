#!/usr/bin/env python3
"""Contiguous 0x7884-to-loop-edge comparison for disabled probe/event paths."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
D=R/'g2/components/case/startup_candidate_20261011'
sources=[D/('application_policy_'+name+'_candidate.c') for name in ('postservice','status','no_reply','ota_probe','event_idle','tail')]
stubs=[('case_policy_log','uint32_t x','(void)x;','void'),('case_policy_log_number','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_led_left_clear','uint32_t x','(void)x;','void'),('case_policy_led_right_clear','uint32_t x','(void)x;','void'),('case_policy_refresh','void','','void'),('case_policy_no_reply_reset','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_wait','uint32_t x','(void)x;','void'),('case_policy_send_probe','uint32_t x,const uint8_t *y,uint32_t z','(void)x;(void)y;(void)z;','void'),('case_policy_parse_probe','uint32_t x','(void)x;','void'),('case_policy_event_peek','uint32_t x','(void)x;return 0;','uint32_t'),('case_policy_event_clear','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_event_signal','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_fake_standby_clear','void','','void'),('case_policy_elapsed','uint32_t *x','(void)x;','void'),('case_init_pmic_read','uint32_t x,uint8_t *y,uint32_t z','(void)x;(void)y;(void)z;','void'),('case_init_power_set','uint32_t x','(void)x;','void'),('case_init_boost_set','uint32_t x','(void)x;','void'),('case_init_wake_mask','uint32_t x','(void)x;','void'),('case_init_wake_config','uint32_t x','(void)x;','void'),('case_init_wake_clock','void','','void'),('case_policy_task_notify','uint32_t x','(void)x;','void'),('case_policy_flash_write','uint32_t x,uint32_t y,uint32_t z','(void)x;(void)y;(void)z;','void'),('case_policy_wake_arm','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_system_reset','void','','void')]
stub=H/'policy_postservice_oracle_stubs.c'
stub.write_text('#include <stdint.h>\nconst uint8_t case_policy_ota_probe_template[12]={0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a};\n'+''.join('__attribute__((noinline,used)) '+ret+' '+n+'('+args+'){'+body+'__asm__ volatile("nop");}\n' for n,args,body,ret in stubs))
objects=[]
for s in sources+[stub]:
 o=H/(s.stem+'.postservice.oracle.o');objects.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_postservice_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objects],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
orig={0x08009170:'log',0x08006b80:'led_l',0x08006b98:'led_r',0x0800bb74:'refresh',0x0800a7b0:'wait'}
srcmap={sym[n]&~1:n.removeprefix('case_policy_') for n in ('case_policy_log','case_policy_led_left_clear','case_policy_led_right_clear','case_policy_refresh','case_policy_wait')}
norm={'led_left_clear':'led_l','led_right_clear':'led_r'}
checked=0
for left,right,old_l,old_r,silent in itertools.product((0,1),(0,1),(0,1),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x2000088c,bytes([left,right]));u.mem_write(0x200000bf,bytes([silent]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c)
   for off,val in ((0,0x200008bc),(4,0x2000089c),(12,old_l),(20,old_r)):u.mem_write(0x20007fc0+off,val.to_bytes(4,'little'))
  else:
   u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,0x2000089c);u.reg_write(UC_ARM_REG_R2,0x200008bc);u.reg_write(UC_ARM_REG_R3,old_l);u.mem_write(0x20007fc0,old_r.to_bytes(4,'little'))
  calls=[];lookup=orig if native else srcmap
  def hook(u,a,size,ctx):
   if native and a==0x08007ed6:u.emu_stop();return
   if a in lookup:
    n=norm.get(lookup[a],lookup[a]);calls.append((n,u.reg_read(UC_ARM_REG_R0) if n in ('log','wait','led_l','led_r') else 0));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007884 if native else sym['case_policy_postservice_7884'])|1,0x20001000,count=30000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x64)),bytes(u.mem_read(0x200000b8,0x10))))
 assert pair[0]==pair[1],(left,right,old_l,old_r,silent,pair[0][0],pair[1][0])
 checked+=1
print('PASS_CASE_POLICY_POSTSERVICE_CONTIGUOUS',checked)
