from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-delete-connected-round164';D.mkdir(exist_ok=True);S=B/'root-ambiq-delete-round162/candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);P=0x20001000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4d4650');z=selected.find('#include <stdint.h>',a);z=len(selected) if z<0 else z;prefix=S.read_text().split('/* Native4d4650')[0];fixture=Path(t)/'selected.c';fixture.write_text(prefix+selected[a:z]);S=fixture
 names=['audio_uart_font_bitmap_release','audio_uart_nema_cl_destroy_5142f0','audio_uart_lv_thread_sync_signal_4d4724','audio_task_delete'];defs={n:0x101011+i*16 for i,n in enumerate(names)};defs.pop('audio_uart_lv_thread_sync_signal_4d4724');defs.update({'audio_uart_lv_anim_mutex_ensure_4d47fa':0x101051,'stock_enter_critical':0x101061,'stock_exit_critical':0x101071,'audio_notify_task':0x101081})
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_delete_4c74f0',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),str(B/'root-lv-sync-round163/candidate.c'),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,stencil,inited,task,mutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,W(*[seed]*64));u.mem_write(P+60,W(0x20008000,stencil));u.mem_write(P+52,W(task));u.mem_write(P+56,bytes([inited,0xa5]));u.mem_write(P+32,W(inited,0,task));events=[]
  cuts=dict(zip([0x101010+i*16 for i in range(4)] if isc else [0x48b216,0x5142f0,0x4d4724,0x454aae],['release','cl','signal','delete']))
  cuts={a:op for a,op in cuts.items() if op!='signal'};cuts.update({(0x101050 if isc else 0x4d47fa):'ensure',(0x101060 if isc else 0x4420d0):'enter',(0x101070 if isc else 0x4420e8):'exit',(0x101080 if isc else 0x455c48):'notify'})
  def hook(uc,a,n,user):
   if a not in cuts:return
   kind=cuts[a];arg=uc.reg_read(UC_ARM_REG_R0);snapshot=bytes(uc.mem_read(P,256)).hex()
   if kind=='notify':
    r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];events.append((kind,*r,struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0],snapshot))
   else:events.append((kind,None if kind in ['enter','exit'] else arg,snapshot))
   if kind=='release' and mutation==1:u.mem_write(P+64,W(0x20009000))
   if kind=='cl' and mutation==2:u.mem_write(P+56,b'\x01');u.mem_write(P+52,W(0x2000a000))
   if kind=='exit' and mutation==2:u.mem_write(P+52,W(0x2000b000))
   uc.reg_write(UC_ARM_REG_R0,0xabcdef01);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sym['audio_uart_ambiq_delete_4c74f0'] if isc else 0x4c74f0)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,256))
 count=0
 for stencil,inited,task,mutation,seed in itertools.product([0,0x20009000],[0,1,255],[0,0x20007000],[0,1,2],[0,0xa5a5a5a5,0xffffffff]):
  a=run(False,stencil,inited,task,mutation,seed);b=run(True,stencil,inited,task,mutation,seed);assert a==b,(stencil,inited,task,mutation,seed,a,b);count+=1
 receipt={'status':'PASS_CONNECTED_AMBIQ_DELETE_SYNC_THREAD_DELETE','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual sync and thread-delete wrappers execute; bitmap/commandlist/mutex ensure/critical/tasknotify/taskdelete controlled cuts; orderedcall snapshots,child mutations,256unitbytes,exitflag,taskhandle,return1/SP compared.','No VG destroys in native body; downloaded provider is informative,not exactconfiguration proof. Real GPU destruction/scheduler/fullimage gates remainopen.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
