#!/usr/bin/env python3
"""Bounded stock/source comparison for original 0x41937c queue envelope."""
import hashlib, importlib.util, itertools, json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES['queue_submit_raw']=0x41937c
SOURCE=ROOT/'g2/components/bootloader/source_candidate_20261010/queue_submit_raw_41937c.c'
MODE=ROOT/'g2/components/bootloader/queue/runtime_mode.c'
BODY_SHA='4d5a91e625ccf2bfab4f06aa68d12af2eded6bf3ed174c58cd7cbd65196ad73a'
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  self.child_result=1
  super().__init__(*args,**kwargs)
 def code(self,uc,pc,size,user):
  if pc==0x41b2f8:
   self.events.append(['mask-interrupts',self.args()[0]])
   self.finished=True;uc.emu_stop();return
  if pc in (0x419ec0,0x41a024):
   r0,r1,r2,r3=self.args()
   self.events.append(['task' if pc==0x419ec0 else 'isr',r0,bytes(uc.mem_read(r1,12)).hex(),r2,r3])
   self.ret(self.child_result)
   return
  super().code(uc,pc,size,user)
def main():
 assert v.sha(v.BLOB)==v.SHA
 image=v.BLOB.read_bytes();body=image[0x41937c-v.BASE:0x4193de-v.BASE]
 assert len(body)==98 and hashlib.sha256(body).hexdigest()==BODY_SHA
 with tempfile.TemporaryDirectory(prefix='bootloader-queue-envelope-') as tmp:
  p=Path(tmp);script=p/'module.ld';script.write_text('''ENTRY(opencfw_boot_queue_submit_raw)
SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_bl_kernel_queue_put_blocking = 0x419ec1;
opencfw_bl_kernel_queue_put_from_isr = 0x41a025;
opencfw_bl_mask_interrupts = 0x41b2f9;
''')
  objects=[]
  for i,src in enumerate((SOURCE,MODE)):
   obj=p/f'unit{i}.o';objects.append(obj)
   subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-ffreestanding','-fno-builtin','-std=c11','-O2','-fwrapv','-c',str(src),'-o',str(obj)],check=True)
  elf=p/'source.elf';subprocess.run(['arm-none-eabi-ld','-T',str(script),*(str(x) for x in objects),'-o',str(elf)],check=True,capture_output=True)
  _,segments,symbols=v.elf.elf_info(elf)
  cases=[];trace={};coverage=set()
  vectors=itertools.product((0,0x20002100),(0,1,2),(0,4,5,6,7,0xffffffff),(0,1,2))
  for queue,mode,kind,result in vectors:
   for timeout in (0,3):
    pair=[Machine(),Machine(True,segments,symbols)];outputs=[]
    for m in pair:
     m.child_result=result;m.w(0x20027180,queue)
     m.w(0x20027150,0 if mode==1 else 1)
     m.w(0x2002716c,0 if mode==2 else 1)
     m.w(v.SP,timeout)
     result_data=m.run('queue_submit_raw',[0x42,kind,0x12345678,0x20002300])
     outputs.append({'return':result_data['return'],'events':result_data['events']})
    assert outputs[0]==outputs[1],(queue,mode,kind,result,timeout,outputs)
    trace.update(pair[0].trace)
    cases.append({'queue':queue,'runtime_mode':mode,'class':kind,'child_result':result,'timeout':timeout,'observed':outputs[0]})
  null_cases=[]
  for kind,payload,woken,timeout in itertools.product((0,4,0xffffffff),(0,0x12345678),(0,0x20002300),(0,3)):
   pair=[Machine(),Machine(True,segments,symbols)];outputs=[]
   for m in pair:
    m.w(0x20027180,0x20002100);m.w(v.SP,timeout)
    result_data=m.run('queue_submit_raw',[0,kind,payload,woken])
    outputs.append(result_data['events'])
   assert outputs[0]==outputs[1]==[['mask-interrupts',0]],(kind,payload,woken,timeout,outputs)
   trace.update(pair[0].trace)
   null_cases.append({'class':kind,'payload':payload,'woken':woken,'timeout':timeout,'terminal_event':outputs[0]})
  coverage={int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw))) if 0x41937c<=int(pc,16)+i<0x4193de}
  report={'status':'PASS','cases':len(cases),'original_image_sha256':v.SHA,'original_entry':'0x41937c','original_end_exclusive':'0x4193de','original_body_sha256':BODY_SHA,'visited_original_body_bytes':len(coverage),'unvisited_original_addresses':[hex(a) for a in range(0x41937c,0x4193de) if a not in coverage],'source_sha256':v.sha(SOURCE),'runtime_mode_source_sha256':v.sha(MODE),'comparisons':cases,'null_prefix_cases':null_cases,'limits':['Null-event cases compare only the original/source prefix through entry to the interrupt-mask lower call; subsequent invalid-address write and nonreturn loop are not executed or compared.','Blocking/ISR queue operations are controlled lower calls; envelope bytes, queue pointer, timeout, mode and return are compared.','Original and source runtime-mode queries execute; physical scheduling and ISR delivery are untested.','The compatible M4 test ELF is not the combined M55 archive.']}
  (HERE/'queue-submit-raw-round78-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
  print('PASS',len(cases),'returning cases and',len(null_cases),'null-event prefix cases; original body',len(coverage),'/98 bytes')
if __name__=='__main__':main()
