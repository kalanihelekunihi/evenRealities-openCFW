from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-end-unbind-connected-round196';S=B/'root-ambiq-common-end-round178/candidate.c';CELL=0x200746c0;U=0x20001000;ALT=0x20002000;TXT=0x20003000;W=lambda v:struct.pack('<I',v&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_cl_submit_514cf2','audio_uart_nema_cl_wait_514d00','audio_uart_nema_cl_unbind_5144ba','audio_uart_nema_power_control_51419a','audio_uart_ambiq_context_unlock_4b0886','audio_uart_nema_get_error_4b128a','audio_uart_nema_vg_get_error_51564c','audio_uart_nema_error_interpret_4b0594','audio_uart_nema_vg_error_interpret_4b0584','audio_uart_lvgl_log'];native=[0x514cf2,0x514d00,0x5144ba,0x51419a,0x4b0886,0x4b128a,0x51564c,0x4b0594,0x4b0584,0x44d25c]
with tempfile.TemporaryDirectory() as t:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4c791a..4c7920;');fixture=Path(t)/'selected.c';z=selected.index('#include <stdint.h>',a);fixture.write_text(S.read_text().split('/* Native4c791a')[0].replace('extern void audio_uart_ambiq_context_unlock_4b0886(void *);','extern uint32_t audio_uart_ambiq_context_unlock_4b0886(void *);')+selected[a:z]);S=fixture
  a=selected.index('/* Native4b0886..4b092a.');uf=Path(t)/'selected-unlock.c';uf.write_text((B/'root-ambiq-context-unlock-round180/candidate.c').read_text().split('/* Native4b0886')[0]+selected[a:selected.index('#include <stdint.h>',a)]);US=uf
  ms=(R/'components/audio/uart_thread_source_candidate/display_timer_children.c').read_text();a=ms.index('uint32_t audio_uart_lv_unlock_core(void *cell) {');z=ms.index('\nvoid *audio_uart_lv_list_first',a);mf=Path(t)/'selected-mutex.c';mf.write_text((B/'root-lv-mutex-unlock-round181/candidate.c').read_text().split('uint32_t audio_uart_lv_unlock_core(void *cell) {')[0]+ms[a:z]);MS=mf
  a=selected.index('/* Native4b128a..4b1298:');ef=Path(t)/'selected-error.c';ef.write_text((B/'root-nema-error-get-round179/candidate.c').read_text().split('/* Native4b128a')[0]+selected[a:selected.index('#include <stdint.h>',a)]);ES=ef
 else:ES=B/'root-nema-error-get-round179/candidate.c'
 e=Path(t)/'test.elf';cuts=[0x101010+i*16 for i in range(10)];subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_submit_4b0c8a','-Wl,--defsym=audio_uart_ambiq_unit_cell=0x200746c0']+['-Wl,--defsym='+n+'='+hex(a|1) for i,(n,a) in enumerate(zip(names,cuts)) if i not in [2,4,5,6,7,8]]+['-Wl,--defsym=audio_uart_nema_context_cell=0x20074efc','-Wl,--defsym=audio_uart_nema_vg_context_cell=0x20074f04','-Wl,--defsym=audio_uart_lv_mutex_ensure=0x101101','-Wl,--defsym=xQueueGiveMutexRecursive=0x101111',str(S),str(ES),str(US),str(MS),str(B/'root-nema-error-text-round191/candidate.c'),str(B/'root-nema-vg-error-state-round193/candidate.c'),str(B/'root-nema-cl-unbind-round195/candidate.c'),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,sync,power,gfx,vg,mutation,give,list_state):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(0x20074efc,W(0x20005000));u.mem_write(0x20005000,bytes([165])*48);u.mem_write(0x20005020,W(gfx));u.mem_write(0x20005004,W(0x20008000 if list_state else 0));u.mem_write(0x20008000,bytes([165])*64);u.mem_write(0x20008008,W(0x20009000));u.mem_write(0x20008010,W(1 if list_state==1 else 8));u.mem_write(0x20008014,W(0));u.mem_write(0x20009000,bytes([90])*64);u.mem_write(0x20074f04,W(0x20006000));u.mem_write(0x20006000,bytes([90])*256);u.mem_write(0x20006080,W(vg));u.mem_write(CELL,W(U));u.mem_write(U,bytes([165])*256);u.mem_write(U+132,W(1));u.mem_write(U+136,W(0x20007000));u.mem_write(U+140,W(1));u.mem_write(ALT,bytes([90])*256);u.mem_write(TXT,b'controlled interpretation\0');events=[];trace=[]
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a==(0x101100 if isc else 0x4d47cc):
    events.append(('ensure',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if a==(0x101110 if isc else 0x441710):
    events.append(('give',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,give&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if a not in addresses or addresses.index(a) in [2,4,5,6,7,8]:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0x12345678
   if i==9:
    sp=uc.reg_read(UC_ARM_REG_SP);fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];err=struct.unpack('<I',uc.mem_read(sp+4,4))[0] if r[2] in [538,555,559] else None;text=string(struct.unpack('<I',uc.mem_read(sp+8,4))[0]) if r[2] in [555,559] else None;events.append(('log',r[0],string(r[1]),r[2],string(r[3]),string(fmt),err,text))
   else:events.append((i,tuple(r[:2 if i==3 else 1 if i in [0,1,4,7,8] else 0])))
   if mutation and i in [0,4]:uc.mem_write(CELL,W(ALT))
   if i==3:ret=power
   if i==5:ret=gfx
   if i==6:ret=vg
   if i in [7,8]:ret=TXT
   uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4 or 0x20074efc<=a<0x20074f00 or 0x20005000<=a<0x20005030 or 0x20074f04<=a<0x20074f08 or 0x20006000<=a<0x20006100 or 0x20008000<=a<0x20008040 or 0x20009000<=a<0x20009040 or U<=a<U+256:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,sync);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_ambiq_submit_4b0c8a'] if isc else 0x4b0c8a)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(CELL,4)),bytes(u.mem_read(U,256)),bytes(u.mem_read(ALT,256)),bytes(u.mem_read(0x20005000,48)),bytes(u.mem_read(0x20006000,256)),bytes(u.mem_read(0x20008000,64)),bytes(u.mem_read(0x20009000,64))
 cases=list(itertools.product([0,1,255,256,257,0xffffffff],[0,1,0xffffffff],[0,1,2,0x7fffffff,0x80000000,0xffffffff],[0,1,0xffffffff],[0,1],[0,1,257],[0,1,2]))
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_CONNECTED_COMMON_END_REAL_UNBIND_VG_ERROR_STATE','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'fixture_body_hashes':{str(k):hashlib.sha256(k.read_bytes()).hexdigest() for k in [S,ES,US,MS,B/'root-nema-error-text-round191/candidate.c',B/'root-nema-vg-error-state-round193/candidate.c',B/'root-nema-cl-unbind-round195/candidate.c']},'selected_source_hashes':{name:hashlib.sha256((R/'components/audio/uart_thread_source_candidate'/name).read_bytes()).hexdigest() for name in ['display_lv_init_children.c','display_timer_children.c']},'limits':['Actual default-unit/error getter/context-unlock/mutex-unlock and both error-label tables/lookup/VG getter/command-list unbind; ensure/queue/log/remaining GPU child cuts; full48contextbytes and ordered error read/clear compared. Lowbyte sync, power early-return, gfx/vg errors/logformats, mutable cell retaining cached unit, orderedcell access/full512unitbytes/return/SP compared.','Actual command-list submission/wait/power children and hardware remain unqualified.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
