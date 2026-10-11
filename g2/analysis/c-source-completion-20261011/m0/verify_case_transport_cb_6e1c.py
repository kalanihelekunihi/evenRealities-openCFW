#!/usr/bin/env python3
"""CASE 0x6e1c native/source one-loop transport worker at wait cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_cb_6e1c_candidate.c';obj=H/'cb6e1c.oracle.o';stub=H/'cb6e1c.oracle_stub.c';stubobj=H/'cb6e1c.oracle_stub.o';elf=H/'cb6e1c.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
undefined=[line.split()[-1] for line in subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
stub.write_text('#include <stdint.h>\n'+''.join(f'uint32_t {name}(void){{return 0;}}\n' for name in undefined))
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={0xaaf0:'case_policy_event_signal',0xa816:'case_policy_event_peek',0xa7d2:'case_policy_event_clear',0x6b98:'case_boot_transport_stop_link',0x6b80:'case_boot_transport_stop_clock',0x67c8:'log_hex_buffer',0x258c:'case_policy_send_probe',0x2744:'case_policy_ota_transmit',0x1e94:'case_policy_parse_probe',0x3b90:'case_boot_transport_rx_restart',0x9170:'case_policy_log',0x9a9c:'case_policy_no_reply_reset',0x502c:'case_init_display_reset',0x085c:'case_boot_transport_event_085c',0x23f4:'case_boot_transport_left_aging',0x24c0:'case_boot_transport_right_aging',0x12e4:'case_policy_box_failure_reset',0xab26:'case_policy_task_reset',0xd154:'case_policy_service_idle',0xa888:'case_boot_sensor_finish_signal',0xa7b0:'case_policy_wait'}
rng=random.Random(0x6e1c)
for i in range(192):
 bits=[0,2,4,8,0x20,0x400,0x40,0x100,0x200,0x80,0x1000,0x20|0x400,0x80|2][i%13];shared=bytearray(0x120);state=bytearray(rng.randbytes(64));shared[4]=0;shared[5]=1;shared[7]=1;shared[0x1c]=0;shared[0x3d]=0;shared[0xfc]=0x31;shared[0xfd]=0;shared[0xfe]=i%2;shared[0xff]=7;shared[0x100]=0
 # Explicit stable task/event tokens and packet contents.
 for o,v in ((0x10,0x20002000),(0x18,0x20002100),(0x1c,0x20002200),(0x20,0x20002300),(0x24,0x20002400),(0x38,0x20002500)):
  struct.pack_into('<I',shared,o,v)
 state[0x10]=1;state[0x11]=1;state[0x19]=i%2;state[0x1a]=i%3==0
 quiet=1;restart=1 if i%2 else 0;pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000b8,bytes(shared));u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000bf,bytes([quiet]));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08000000+a:b for a,b in native.items()} if original else {sym[v]&~1:v for v in undefined});calls=[];stopped=[False]
  def hook(uc,a,n,_):
   name=targets.get(a)
   if name is None:return
   kind=name if original else next((k for k,v in native.items() if v==name),None)
   if original: name=native[a-0x08000000]
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if name=='case_policy_wait' and x==1:
    calls.append((name,x));stopped[0]=True;uc.emu_stop();return
   if name in ('case_policy_event_signal','case_policy_event_clear','case_boot_sensor_finish_signal'):calls.append((name,x,y))
   elif name in ('case_policy_send_probe','case_policy_ota_transmit'):calls.append((name,x,z,w,bytes(uc.mem_read(y,z))))
   elif name=='log_hex_buffer':calls.append((name,y,bytes(uc.mem_read(x,y))))
   elif name=='case_policy_log':calls.append((name,bytes(uc.mem_read(x,100)).split(b'\0')[0]))
   else:calls.append((name,x if name in ('case_boot_transport_stop_link','case_boot_transport_stop_clock','case_boot_transport_left_aging','case_boot_transport_right_aging','case_policy_event_peek','case_policy_parse_probe','case_policy_task_reset','case_policy_no_reply_reset','case_policy_wait') else None))
   if name=='case_policy_event_peek':uc.reg_write(UC_ARM_REG_R0,bits)
   elif name=='case_boot_transport_rx_restart':uc.reg_write(UC_ARM_REG_R0,restart)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08006e1c if original else sym['case_boot_transport_cb_6e1c'])|1,0,count=10000)
  assert stopped[0],(i,original,calls)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x120)),bytes(u.mem_read(0x2000087c,64))))
 assert pair[0]==pair[1],(i,[(x[0],*x[1:4]) for x in pair[0][0]],[(x[0],*x[1:4]) for x in pair[1][0]])
print('PASS_CASE_TRANSPORT_CB_6E1C',192)
