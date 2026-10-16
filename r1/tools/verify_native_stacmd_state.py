#!/usr/bin/env python3
"""Prove source counter initialization against native scatter writes from poisoned RAM."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-state';F=0x200075c0;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_state.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';data=app.read_bytes();app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';evidence={}
 for n,a,z in [('scatter-decoder',0x286f4,96),('scatter-table',0xc43ec,32)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==data[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]={'sha256':sha(p),'address':a,'bytes':z}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'counter.bin';ld.write_text('SECTIONS { .r1.stacmd.failed_transactions 0x200075c0 : { *(.r1.stacmd.failed_transactions) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.r1.stacmd.failed_transactions','-O','binary',str(elf),str(binary)],check=True)
  initial=binary.read_bytes();assert initial==bytes(4);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};assert syms['r1_stacmd_failed_transactions']==F
  runs=[]
  for poison in (0xa5,0x5a,0xff,0x3c):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,data);u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);u.reg_write(UC_ARM_REG_SP,0x2003f000);writes=[]
   def hook(uc,access,address,size,value,_):
    if address<F+4 and address+size>F:writes.append({'pc':uc.reg_read(UC_ARM_REG_PC),'address':address,'bytes':size,'value':value})
   u.hook_add(UC_HOOK_MEM_WRITE,hook);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208
   assert bytes(u.mem_read(F,4))==initial
   assert writes==[{'pc':0x28726,'address':F+i,'bytes':1,'value':0} for i in range(4)]
   # Apply only the emitted source initializer and preserve adjacent sentinels.
   source=Uc(UC_ARCH_ARM,UC_MODE_THUMB);source.mem_map(0x20000000,0x40000);source.mem_write(F-4,bytes([poison])*12);source.mem_write(F,initial);assert bytes(source.mem_read(F-4,12))==bytes([poison])*4+initial+bytes([poison])*4
   runs.append({'ram_poison':poison,'native_counter_hex':bytes(u.mem_read(F,4)).hex(),'native_writes':writes,'source_counter_hex':initial.hex(),'native_configuration_name_pointer':struct.unpack('<I',bytes(u.mem_read(F+4,4)))[0]})
 vp.write_text(json.dumps(dict(comparisons=len(runs),runs=runs,scatter_entry='0x283a0',stop_before_runtime='0x27208',source_initializer_bytes=4,source_initializer_sha256=hashlib.sha256(initial).hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Native scatter execution proves cold initial bytes; target whole startup remains incomplete source','Source initializer/address tested in isolated ELF; canonical admission/runtime stage remain gates','Warm-reset lifecycle, physical device state and whole-image instruction/byte identity unproven']),indent=2)+'\n');print('STACMD state:',len(runs),'poisoned-RAM scatter comparisons; four explicit zero-byte writes per run')
if __name__=='__main__':main()
