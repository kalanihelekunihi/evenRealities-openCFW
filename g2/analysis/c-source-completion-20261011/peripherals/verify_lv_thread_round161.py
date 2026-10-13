from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-thread-round161';S=D/'candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);T=0x20001000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4d4768');prefix=S.read_text().split('/* Native4d4768')[0];fixture=Path(t)/'selected-thread.c';fixture.write_text(prefix+selected[a:]);S=fixture
 defs={'g2_thread_create_dynamic':0x101011,'audio_task_delete':0x101021,'audio_uart_lvgl_log':0x101031}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_thread_init_4d4610',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,op,priority,stack,result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(T,W(0x101041,0x20002000,0xa5a5a5a5,0xa5a5a5a5));u.mem_write(0x20003000,b'thread\0');u.mem_write(0x200ff000,W(stack,0x20002000));events=[]
  cuts=({0x101010:'create',0x101020:'delete',0x101030:'log'} if isc else {0x4548ba:'create',0x454aae:'delete',0x44d25c:'log'});cuts[0x101040]='callback'
  def string(a):return bytes(u.mem_read(a,220)).split(b'\0',1)[0].decode('ascii')
  def hook(uc,a,n,user):
   if a not in cuts:return
   kind=cuts[a];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=result
   if kind=='create':
    assert r[0]==(sym['audio_uart_lv_thread_trampoline_4d4768'] if isc else 0x4d4769);args=struct.unpack('<II',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8));events.append((kind,string(r[1]),r[2],r[3],*args,bytes(uc.mem_read(T,16)).hex()));uc.mem_write(args[1],W(0x20008000))
   elif kind=='log':events.append((kind,r[0],string(r[1]),r[2],string(r[3]),string(struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0])))
   else:events.append((kind,r[0]));uc.mem_write(T+12,W(0x12345678))
   uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,v in [(UC_ARM_REG_R0,T),(UC_ARM_REG_R1,0x20003000),(UC_ARM_REG_R2,priority),(UC_ARM_REG_R3,0x101041),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,v)
  u.emu_start((sym['audio_uart_lv_thread_init_4d4610' if op=='init' else 'audio_uart_lv_thread_trampoline_4d4768'] if isc else 0x4d4610 if op=='init' else 0x4d4768)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_R0) if op=='init' else None,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(T,16))
 count=0
 for op,priority,stack,result in itertools.product(['init','trampoline'],[0,40,256,0xffffffff],[0,3,4,32768,0x40000,0xffffffff],[-1,0,1,2]):
  a=run(False,op,priority,stack,result);b=run(True,op,priority,stack,result);assert a==b,(op,priority,stack,result,a,b);count+=1
 receipt={'status':'PASS_NATIVE_LV_THREAD_INIT_TRAMPOLINE','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Task-create/delete/logger and entry callback controlled cuts; priority/depth truncation,success/error,TCB-output write,callback argument/deleteNULL sequence and16cellbytes/return/SP compared.','Trampoline code pointer normalized tonative identity; realtask scheduling andfullimage gates remainopen.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
