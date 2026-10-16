#!/usr/bin/env python3
"""Controlled stock/C comparison for ANCC state packet send."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_ancc_state_sync_497cf0.c'
OUT=G2/'build/c-firmware/20261016/main-even-ai-ancc-state-sync'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,state,delay):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 cpu.reg_write(UC_ARM_REG_R0,state);cpu.reg_write(UC_ARM_REG_R1,delay);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 child=sy['audio_sync_send_to_both_ext_464f76']&~1 if compiled else 0x464f76
 calls=[]
 def hook(machine,pc,width,unused):
  if pc!=child:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  extra=int.from_bytes(machine.mem_read(machine.reg_read(UC_ARM_REG_SP),4),'little')
  calls.append((a,bytes(machine.mem_read(b,c)),c,d,extra))
  machine.reg_write(UC_ARM_REG_R0,0);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_even_ai_ancc_state_sync_497cf0'] if compiled else 0x497cf0
 cpu.emu_start(entry|1,0x600000,count=300)
 return calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True)
 stub=OUT/'state-sync-oracle-stub.c';stub.write_text('#include <stdint.h>\nuint32_t audio_sync_send_to_both_ext_464f76(uint32_t a,const void*b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n')
 elf_path=OUT/'state-sync-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_even_ai_ancc_state_sync_497cf0',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for args in itertools.product((0,1,2,4,255,256,0xffffffff),(0,1,5,500,0x12345678,0xffffffff)):
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'state sync mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_EVEN_AI_ANCC_STATE_SYNC_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Six-byte ANCC state payload and five send arguments including stack event','limits':['Paired-send side effects, whole-image link and hardware execution remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
