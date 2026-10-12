from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-startup-round121';S=R/'components/audio/uart_thread_source_candidate/display_font_alloc.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20000338;M=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('g2_tlsf_create_with_pool_4d06ec',0x4d06ec),('audio_uart_lv_pool_initialize_48413c',0x48413c),('audio_uart_heap_initialize_4842e6',0x4842e6)]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void*g2_tlsf_control_create_4d06b4(void*p){return 0;} void*g2_tlsf_add_pool_4d0608(void*a,void*b,unsigned c){return 0;} void*audio_uart_mutex_dynamic_create(unsigned n){return 0;} void g2_file_heap_error_log(const char*p){} void audio_uart_heap_memory_configure_4840c8(void){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],*['-Wl,-u,'+n for n,a in providers],str(S),str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('create','g2_tlsf_control_create_4d06b4',0x4d06b4),('add','g2_tlsf_add_pool_4d0608',0x4d0608),('mutex','audio_uart_mutex_dynamic_create',0x4416d6),('log','g2_file_heap_error_log',0x4733ee),('configure','audio_uart_heap_memory_configure_4840c8',0x4840c8)]};engines.append((u,cuts,isc))
 counts={n:0 for n,a in providers};spins=0
 def check(idx,args,control=M,mutex=0x20007000,add=0,mutation=0,fail=3):
  nonlocal_dummy=None
  outs=[];name,address=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(P,bytes([0xa5])*96);calls=[];created=0;logged=False;visits={};spin=False
   def hook(uc,a,n,user):
    nonlocal created,logged,spin
    if logged:
     visits[a]=visits.get(a,0)+1
     if visits[a]>32:spin=True;uc.emu_stop();return
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];ret=0
    if op=='create':
     calls.append((op,r[0]));ret=0 if idx==2 and created==fail else control;created+=1
    elif op=='add':calls.append((op,*r));ret=add
    elif op=='mutex':calls.append((op,r[0]));ret=mutex
    elif op=='log':calls.append((op,r[0]));logged=True
    else:calls.append((op,))
    if mutation:uc.mem_write(P,W(0x20007100,0x20008100,64,80,0x12345678,0xffffffff));uc.mem_write(P+24,bytes([0x7f])*72)
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
   u.emu_start((syms[name] if isc else address)|1,0x600000,count=10000);assert spin or u.reg_read(UC_ARM_REG_PC)==0x600000,(name,args)
   outs.append((calls,spin,u.reg_read(UC_ARM_REG_R0) if idx==0 else None,None if spin else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,96))));u.hook_del(h)
  assert outs[0]==outs[1],(name,args,control,mutex,add,mutation,fail,outs);counts[name]+=1
 for memory,size,control,add,mutation in itertools.product([0,M,0xfffffff0],[0,1024,3188,3189,0xffffffff],[0,M],[0,0x12345678],[0,1]):check(0,[memory,size],control=control,add=add,mutation=mutation)
 for size,control,mutex,add,mutation in itertools.product([0,1024,3188,3189,0xffffffff],[0,M],[0,0x20007000],[0,0x12345678],[0,1]):check(1,[P,M,size],control=control,mutex=mutex,add=add,mutation=mutation)
 for fail,mutex,add,mutation in itertools.product(range(4),[0,0x20007000],[0,0x12345678],[0,1]):check(2,[],mutex=mutex,add=add,mutation=mutation,fail=fail)
 receipt={'status':'PASS_COMPILED_ARM_HEAP_STARTUP_NATIVE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual create-with-pool/pool-init/three-pool startup execute; control-create/add-pool/mutex/logger/memory-configuration controlled cuts.','Unsigned header subtraction,NULL control,ignored add-pool return,failure recurrent self-loop,callback mutations and exact post-config flag clears compared. Actual child contracts/startup success and hardware unproved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
