"""Bounded original/source UART RX/error prefix and full EndRxTransfer tests."""
from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];fw=root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';blob=fw.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=Path(sys.argv[1]);segments=[];symbols={}
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
H=0x20002000;HW=0x40013800;probe=symbols['case_uart_rx_probe']|1
entries=[0x08005f50,symbols['case_uart_error_irq'],symbols['HAL_UART_IRQHandler']];end=[0x080086f4,symbols['case_uart_end_rx'],symbols['UART_EndRxTransfer']]
def guest(isr,cr1,cr3,callback,error,primask,mutation=0,reception=1,state=0x22):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x100000,0x10000);u.mem_map(0x40013000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW));u.mem_write(H+0x6c,struct.pack('<I',reception));u.mem_write(H+0x74,struct.pack('<I',probe if callback else 0));u.mem_write(H+0x80,bytes(4));u.mem_write(H+0x8c,struct.pack('<II',state,error));u.mem_write(HW,struct.pack('<III',cr1,0x12345678,cr3));u.mem_write(HW+0x1c,struct.pack('<II',isr,0xfeedface));u.mem_write(0x20003008,struct.pack('<I',mutation));u.reg_write(UC_ARM_REG_PRIMASK,primask);return u
def run(u,a,original_prefix=False):
 writes=[];errors=[];stopped=False
 def write(u,access,a,n,v,data):
  if HW<=a<HW+0x24:writes.append([hex(a),n,hex(v),u.reg_read(UC_ARM_REG_PRIMASK)])
  if a in (HW,HW+8):assert u.reg_read(UC_ARM_REG_PRIMASK)==1,('unmasked_atomic_write',hex(a),u.reg_read(UC_ARM_REG_PRIMASK))
 def code(u,a,n,data):
  nonlocal stopped
  if a==0x08005f42:errors.append(struct.unpack('<I',u.mem_read(H+0x90,4))[0])
  if original_prefix and a==0x08006086:u.mem_write(0x2000300c,struct.pack('<I',1));stopped=True;u.emu_stop()
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(a|1,0x20000000,count=10000);assert stopped or u.reg_read(UC_ARM_REG_PC)==0x20000000
 return (writes,errors,bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),bytes(u.mem_read(0x20003000,16)),u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for isr,cr1,cr3,callback,error,primask,mutation in itertools.product([0,1,2,4,8,0x800,0x80f,0x20,0x82f],[0,0x20,0x100,0x4000000,0x4000120],[0,1,0x10000000,0x10000001],[0,1],[0,4,8],[0,1],[0,1,2]):
 vals=[run(guest(isr,cr1,cr3,callback,error,primask,mutation),entries[m],m==0) for m in range(3)];assert vals[0]==vals[1]==vals[2],('prefix',isr,cr1,cr3,callback,error,primask,mutation,[i for i,(a,b,c) in enumerate(zip(*vals)) if a!=b or a!=c]);rows.append(dict(kind='rx_error_prefix',isr=hex(isr),cr1=hex(cr1),cr3=hex(cr3),rx_callback=callback,initial_error=error,primask=primask,synthetic_rx_mutation=mutation,icr_writes=[w[2] for w in vals[0][0] if int(w[0],16)==HW+0x20],error_callback_codes=vals[0][1],final_error=struct.unpack_from('<I',vals[0][2],0x90)[0],other_irq_boundary=struct.unpack_from('<I',vals[0][4],12)[0]==1))
for reception,cr1,cr3,callback,state,primask in itertools.product([0,1,2],[0,0xffffffff,0x120,0x10],[0,0xffffffff,0x10000001],[0,1],[0x20,0x22],[0,1]):
 vals=[run(guest(0,cr1,cr3,callback,0x80,primask,reception=reception,state=state),end[m]) for m in range(3)];assert vals[0]==vals[1]==vals[2],('end',reception,cr1,cr3,callback,state,primask);assert struct.unpack_from('<I',vals[0][2],0x8c)[0]==0x20 and struct.unpack_from('<I',vals[0][2],0x74)[0]==0;rows.append(dict(kind='end_rx',reception=reception,cr1=hex(cr1),cr3=hex(cr3),callback=callback,state=state,primask=primask,writes=vals[0][0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),raw_sha256=hashlib.sha256(raw).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Full EndRxTransfer and selected IRQ RX/error prefix only; original prefix stops before instruction08006086 when other IRQ handling is reached.','DMAR disabled throughout IRQ-prefix tests; DMA helper/link aliases not exercised.','RX callbacks are compiled synthetic count/error-mutation probes; physical UART FIFO/interrupts and real application RX body are not modeled.','Actual weak ErrorCallback08005f42 executes on all sides; hooks observe calls, never replace function bodies.','Final UART/handle/probe state, ordered MMIO writes, PRIMASK at each write and restored PRIMASK are compared; no equivalence claim for instruction/read counts.','Public selected prefix/full helper use explicit macro/type environment; no unique producing HAL/compiler or whole-image byte-equality claim.']),indent=2)+'\n');print('PASS',len(rows))
