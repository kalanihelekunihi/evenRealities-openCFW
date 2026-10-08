#!/usr/bin/env python3
"""Bound the shared original/source reset at actual UART row-loop return.
No DFU, task scheduling, hardware writes or return stubs added by this runner.
"""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('failure',HERE.parent/'thread_creation/verify_source_image_failures.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
class Machine(f.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.uart_return=None
 def code(self,uc,pc,size,user):
  if pc==self.initializer_native_entries.get('opencfw_bl_post_bringup_setup'):self.uart_return=uc.reg_read(f.v.a.UC_ARM_REG_LR)&~1
  if self.uart_return is not None and pc==self.uart_return:self.stop('uart-row-loop-return');return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segments,syms=f.v.elf.elf_info(args.elf);f.p.configure_profiles(syms);blob=f.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==f.v.SHA
 app=f.s.ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert f.v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';vector=app.read_bytes()[32:40];reset=struct.unpack('<2I',vector)[1]&~1;results=[];trace={}
 for source in (False,True):
  m=Machine(source,segments,syms);f.setup(m,b'\xff'*f.s.SIZE,blob,reset,vector);m.cpu.reg_write(f.v.a.UC_ARM_REG_SP,0x2007fb00);m.cpu.reg_write(f.v.a.UC_ARM_REG_LR,f.v.STOP|1);start=syms['opencfw_boot_reset_entry']&~1 if source else 0x43291a;m.cpu.emu_start(start|1,f.v.STOP+2,count=20000000);assert m.reason=='uart-row-loop-return',m.reason
  rows=[dict(kind=m.u(0x20000454+28*i),handle=m.u(0x20000458+28*i),initialized=m.cpu.mem_read(0x2000046c+28*i,1)[0]) for i in range(4)]
  results.append(dict(rows=rows,pool=bytes(m.cpu.mem_read(0x20024400,1136)).hex(),uart_registers=[[m.u(0x40039000+(i<<12)+off) for off in (0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x40,0x44,0x48)] for i in range(4)],clock_users=[m.u(0x20026e94),m.u(0x20026e98)],power_control=m.u(0x40021004),highspeed=m.u(0x400201b0),uart_visits={name:m.initializer_native_visits[name] for name in f.p.initv.UART_ENTRIES},uart_events=[x for x in m.initializer_events if x[0].removesuffix('-native') in f.p.initv.UART_ENTRIES],uart_writes=[x for x in m.peripheral_writes if 0x40039000<=x[0]<0x4003d000]))
  if not source:trace.update(m.trace)
 assert results[0]==results[1],{k:[x[k] for x in results] for k in results[0] if results[0][k]!=results[1][k]}
 for i,handle in [(1,0x2002451c),(2,0x20024638),(3,0x20024754)]:
  assert results[0]['rows'][i]['handle']==handle and results[0]['rows'][i]['initialized']==0
  p=bytes.fromhex(results[0]['pool']);offset=i*284;assert p[offset+4]==1 and p[offset+0x118]==4
  assert results[0]['uart_registers'][i][4]==0 and results[0]['uart_registers'][i][8]==0xffffffff
 for name in ['opencfw_bl_post_context_register','opencfw_bl_post_validate','opencfw_bl_post_activate','opencfw_bl_post_record_initialized']:assert results[0]['uart_visits'][name]==3
 r=dict(status='PASS',cases=1,elf_sha256=f.v.sha(args.elf),original_sha256=f.v.SHA,comparison=results[0],original_trace=trace,runner_sha256=f.v.sha(Path(__file__)),limits=['Exact shared ELF reset/initializer instructions execute to actual post-row-loop return; DFU and scheduler phases are outside this focused case.','Reuses the seven-case fixture and its existing explicit external ROM/MMIO/FP64/provider models. This is an additional observation boundary, not a hardware or general scheduling proof.','Rows1/2/3 have real handles, final initialized0 and saved-valid1; UART CFG0 and ICRffffffff. No DMA/IRQ/TX completion or buffer-drain assertion.']);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
