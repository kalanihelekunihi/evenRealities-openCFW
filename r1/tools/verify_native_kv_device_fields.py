#!/usr/bin/env python3
"""Native external stack slice, partial/no cached reads, aliasing and live handle reload."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-kv-device-fields';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();TOP=0x2003f000;F=TOP-64;I=0x20002000;SLOT=0x20007de8
P={'r1_kv_class_read':0x73930,'r1_kv_class_write':0x73968}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_kv_device_fields.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-73710.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-73710-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==60;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x73710&length=64']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x73710-0x27000:0x73710-0x27000+64];p=OUT/'ghidra-body.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 counts={'comparisons':0,'read_calls':0,'write_calls':0,'null_inputs':0};machines=[];states={}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_device_info_record_kv_handle='+hex(SLOT),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];assert args[1:]==[F,52] and args[0]==struct.unpack('<I',bytes(u.mem_read(SLOT,4)))[0]
   if n=='r1_kv_class_read':
    assert bytes(u.mem_read(F,52))==f['frame_seed'];f['reads']+=1
    if f['width']:u.mem_write(F,f['payload'][:f['width']])
    if f['mutation']:u.mem_write(SLOT,struct.pack('<I',0x20003080));u.mem_write(f['input'],struct.pack('<IH',0xa5a5a5a5,0x3fff))
    model=bytearray(u.mem_read(F,52));pointer=f['input']
    def read_model(p,z):return bytes(model[p-F:p-F+z]) if F<=p and p+z<=F+52 else bytes(u.mem_read(p,z))
    model[36:40]=read_model(pointer,4);word=struct.unpack_from('<I',model,40)[0];word=(word&0xfffffffc)|(read_model(pointer+4,1)[0]&3);struct.pack_into('<I',model,40,word);bits=struct.unpack('<H',read_model(pointer+4,2))[0]>>2;struct.pack_into('<I',model,40,(word&0xffff0003)|(bits<<2));f['expected']=bytes(model)
   else:
    f['writes']+=1;assert bytes(u.mem_read(F,52))==f['expected']
    if f['mutation']:u.mem_write(F,b'\x39');u.mem_write(F+51,b'\x73')
   f['trace'].append((n,args[0],bytes(u.mem_read(F,52)),bytes(u.mem_read(f['input'],6))))
   u.reg_write(UC_ARM_REG_R0,f['status']);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.chain(((n,52,0xa5,I,False,0) for n in range(65536)),itertools.product((0,0x1234,0x8000,0xffff),(0,1,4,36,40,41,42,44,51,52),(0,0x5a,0xff),(I,F,F+1,F+32,F+35,F+36,F+38,F+40,F+46),(False,True),(0,5,0xffffffff)),((0,0,0xa5,0,False,5),))
  for packed,width,poison,pointer,mutation,status in cases:
   results=[];frame_seed=bytes((poison+i*13)&255 for i in range(52));payload=bytes((i*37+packed)&255 for i in range(52))
   for candidate,u in enumerate(machines):
    u.mem_write(F-128,b'\x96'*256);u.mem_write(F,frame_seed);u.mem_write(I,struct.pack('<II',packed^0x89abcdef,(0x12340000|packed)));u.mem_write(SLOT,struct.pack('<I',0x20003000))
    # Aliased input begins as incoming stack data; full/partial cached reads may replace it.
    states[id(u)]={'input':pointer,'frame_seed':frame_seed,'payload':payload,'width':width,'mutation':mutation,'status':status,'trace':[],'reads':0,'writes':0};u.reg_write(UC_ARM_REG_R0,pointer);u.reg_write(UC_ARM_REG_SP,TOP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_kv_dev_info_fields_set'] if candidate else 0x73710)|1,0x20000100,count=3000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==TOP and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    f=states[id(u)];assert f['reads']==f['writes']==int(pointer!=0);results.append((bytes(u.mem_read(F,52)),bytes(u.mem_read(I,8)),bytes(u.mem_read(SLOT,4)),f['trace']))
   assert results[0]==results[1],(packed,width,poison,pointer,mutation,status,results);counts['comparisons']+=1;counts['read_calls']+=int(pointer!=0);counts['write_calls']+=int(pointer!=0);counts['null_inputs']+=int(pointer==0)
 vp.write_text(json.dumps(dict(**counts,all_packed_halfwords=True,partial_read_widths=[0,1,4,36,40,41,42,44,51,52],native_frame_bytes=52,native_frame_offset=-64,input_aliases=[I,F,F+1,F+32,F+35,F+36,F+38,F+40,F+46],report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Cached class read/write endpoints are fixtures; actual cached-class/updater composition remains open','Explicit native stack frame boundary preserves failed-read bytes for selected target; other compiler/LTO settings require revalidation','Record handle initialization, locking/persistence, physical stack/interrupt behavior and original image identity remain gates']),indent=2)+'\n');print('KV device fields:',counts)
if __name__=='__main__':main()
