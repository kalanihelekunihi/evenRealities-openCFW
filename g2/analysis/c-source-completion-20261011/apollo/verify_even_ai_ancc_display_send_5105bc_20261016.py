#!/usr/bin/env python3
"""Controlled stock/C comparison for ANCC callback-list dispatch."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_ancc_display_send_5105bc.c'
OUT=G2/'build/c-firmware/20261016/main-even-ai-ancc-display-send'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,present,nodes,enabled,callbacks,value,stored):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 ctx=sy['g2_audio_ancc_display_context_20073f84'] if compiled else 0x20073f84
 n1=0x20004000;n2=0x20004020;count=0x20005000
 seed=bytearray([0xa5]*8);seed[:4]=(n1 if nodes else 0).to_bytes(4,'little');seed[4]=enabled;cpu.mem_write(ctx,bytes(seed))
 for addr,cb,next_addr in ((n1,0x100801 if callbacks&1 else 0,n2 if nodes==2 else 0),(n2,0x100901 if callbacks&2 else 0,0)):
  cpu.mem_write(addr,cb.to_bytes(4,'little')+next_addr.to_bytes(4,'little'))
 cpu.mem_write(count,stored.to_bytes(4,'little'))
 cpu.reg_write(UC_ARM_REG_R0,ctx if present else 0);cpu.reg_write(UC_ARM_REG_R1,value);cpu.reg_write(UC_ARM_REG_R2,count)
 cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 calls=[]
 def hook(machine,pc,width,unused):
  if pc not in (0x100800,0x100900):return
  calls.append((pc,machine.reg_read(UC_ARM_REG_R0),machine.reg_read(UC_ARM_REG_R1),int.from_bytes(machine.mem_read(count,4),'little')))
  machine.reg_write(UC_ARM_REG_R0,0);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_even_ai_ancc_display_send_5105bc'] if compiled else 0x5105bc
 cpu.emu_start(entry|1,0x600000,count=1000)
 return bytes(cpu.mem_read(ctx,8)),bytes(cpu.mem_read(n1,8)),bytes(cpu.mem_read(n2,8)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);elf_path=OUT/'display-send-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_even_ai_ancc_display_send_5105bc',str(SOURCE),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for args in itertools.product((False,True),(0,1,2),(0,1,2),(0,1,2,3),(0,1,0xffffffff),(0,1,0x12345678)):
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'display send mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_EVEN_AI_ANCC_DISPLAY_SEND_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Context guards, enable byte and two-node callback traversal with arguments','limits':['Concurrent list mutation and final context placement remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
