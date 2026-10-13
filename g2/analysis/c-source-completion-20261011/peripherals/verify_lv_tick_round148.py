from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-tick-contract-round148';S=D/'candidate.c';baseline='--baseline' in sys.argv
if baseline or '--selected' in sys.argv:S=R/'components/audio/uart_thread_source_candidate/display_timer_children.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);STATE=0x2006f600
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_tick','-Wl,--defsym=audio_uart_lv_tick_state=0x2006f600',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_lv_tick')
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  engines.append((u,isc))
 count=0
 for tick,callback,mutation,retries in itertools.product([0,1,0x7fffffff,0x80000000,0xffffffff],[0,1],[0,1],[0,1,3]):
  outs=[]
  for u,isc in engines:
   u.mem_write(STATE,W(tick,0xa5a5a5a5,0x101051 if callback else 0,0x12345678));events=[];clears=[];callback_reads=[]
   def code(uc,a,n,user):
    if a not in [0x101050,0x101060]:return
    events.append(('callback',a));uc.mem_write(STATE+12,W(0xabcdef01));uc.reg_write(UC_ARM_REG_R0,tick if a==0x101050 else tick^0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def memory(uc,access,a,n,value,user):
    if not STATE<=a<STATE+16:return
    events.append(('read',a,n,int.from_bytes(uc.mem_read(a,n),'little')) if access==16 else ('write',a,n,value))
    if access==16 and a==STATE+8:
     callback_reads.append(a)
     if callback and mutation and len(callback_reads)==1:uc.mem_write(STATE+8,W(0x101061))
    if access==16 and a==STATE+4 and n==1 and len(clears)<retries:
     clears.append(a);uc.mem_write(STATE+4,b'\0');uc.mem_write(STATE,W((tick+len(clears))&0xffffffff))
   h=u.hook_add(UC_HOOK_CODE,code);m=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((entry if isc else 0x473482)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((events,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(STATE,16))));u.hook_del(h);u.hook_del(m)
  if outs[0]!=outs[1]:
   failure={'status':'LV_TICK_NATIVE_TRACE_MISMATCH','case':[tick,callback,mutation,retries],'native':str(outs[0]),'source':str(outs[1]),'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest()};(D/'baseline-mismatch.json').write_text(json.dumps(failure,indent=2)+'\n');print(json.dumps(failure));raise SystemExit(0 if baseline else 1)
  count+=1
 receipt={'status':'PASS_LV_TICK_NATIVE_READ_RELOAD_RETRY_TRACE','cases':count,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual tick body executes; callback controlled cut. Full state reads/writes/return/SP and16statebytes plus callback-pointer mutation and boundedflag retries compared.','Modeled interference,not physical interrupt timing; connectedtimer/rootdata/fullimage gatesopen.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
