from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-sector-rollover-round221';S=D/'candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_error_set_4b127c','audio_uart_nema_list_finalize_514b7c','audio_uart_nema_submit_523f10','audio_uart_nema_poll_514026'];native=[0x4b127c,0x514b7c,0x523f10,0x514026];cuts=[0x101010+i*16 for i in range(4)]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native5147b0');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native5147b0')[0]+selected[a:z if z>=0 else len(selected)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_sector_rollover_5147b0']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,present,flags,used,sector,capacity,position,ready,seq,poll,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  ctx=0x20002000;u.mem_write(0x20074efc,W(ctx));u.mem_write(ctx,bytes(256));u.mem_write(ctx+249,bytes([ready]));u.mem_write(P,bytes(64))
  for offset,value in [(20,used),(24,flags),(28,seq),(40,capacity),(44,sector),(48,position),(52,seq)]:u.mem_write(P+offset,W(value))
  events=[];trace=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=uc.reg_read(UC_ARM_REG_R0);events.append((i,[r]))
   if mutation==i:
    if i==1:
     uc.mem_write(P+24,W(flags^32));uc.mem_write(P+52,W(0x00ffffff));uc.mem_write(ctx+249,b'\x01')
    if i==2:uc.mem_write(P+52,W(0x12345678))
   uc.reg_write(UC_ARM_REG_R0,poll if i==3 else 0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+64 or ctx<=a<ctx+256 or a==0x20074efc:trace.append((access,a,n,(v&((1<<(8*n))-1)) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if present else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_sector_rollover_5147b0'] if isc else 0x5147b0)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,bytes(u.mem_read(P,64)).hex(),bytes(u.mem_read(ctx,256)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=[(1,f,u,sector,64,pos,r,seq,poll,m) for f,u,sector,pos,r,seq,poll,m in itertools.product([0,32,255],[0,1,16,0x80000000],[0,8,0xffffffff],[0,16,32,48,7],[0,1],[0x00ffffff,7],[0,0xffffffff],[-1,1,2])]
 cases += [(0,0,0,0,0,0,0,0,0,-1)]
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_NEMA_SECTOR_ROLLOVER','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':4,'limits':['NULL/error, signed sector division/wrapped residue, capacity quarter/half/three-quarter/zero positions, context ready, seq sentinel/poll signed gate, child mutations, ordered accesses/fullstate/SP matched.','Finalize/submit/poll/error children controlled; actual driver/sector ownership/faults/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
