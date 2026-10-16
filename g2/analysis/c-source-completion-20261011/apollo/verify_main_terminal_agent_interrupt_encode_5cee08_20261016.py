#!/usr/bin/env python3
"""Compare agent-interrupt packet, sequence wrap and logs with stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_agent_interrupt_encode_5cee08.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-agent-interrupt-encode-5cee08'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';SEQ=0x20074fff
CALLS={'audio_uart_buffer_zero':0x43c0e4,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,'audio_terminal_send_message_5ce7c4':0x5ce7c4}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN or struct.unpack_from('<I',blob,0x5cf204-0x438000)[0]!=SEQ:raise RuntimeError('payload/sequence changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_message_sequence':SEQ};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,sequence,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(SEQ,bytes((sequence,)))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);trace=[];fi=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,170)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal fi
   if pc not in CALLS.values():return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP);v=0
   if pc==0x43c0e4:trace.append(('zero',r[1],r[2]));cpu.mem_write(r[0],b'\0'*r[1])
   elif pc==0x43d0ce:trace.append(('flags',fi));v=flags[min(fi,len(flags)-1)];fi+=1
   elif pc==0x43d574:
    line,msg,magic=struct.unpack('<III',cpu.mem_read(sp,12));trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),line,cstr(cpu,msg),magic))
   elif pc==0x43ce9e:trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),r[3]))
   else:
    notify=struct.unpack('<I',cpu.mem_read(sp,4))[0];trace.append(('send',r[0],r[1],bytes(cpu.mem_read(r[2],1)),r[3],notify));v=9
   cpu.reg_write(A.UC_ARM_REG_R0,v);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_agent_interrupt_encode_5cee08'] if compiled else 0x5cee08)|1,0x600000,count=220)
  return trace,u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((0,1,255),((0,0,0),(2,0,0),(0,1,0),(0,0,4),(2,1,4))))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:print('mismatch',i,args,stock,source);raise RuntimeError('interrupt encoder mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_INTERRUPT_ENCODE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'One-byte payload, sequence wrap, exact log arguments and lower send call','limits':['Lower protobuf/send and logger effects isolated; final sequence RAM startup and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
