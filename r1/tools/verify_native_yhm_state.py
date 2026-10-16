#!/usr/bin/env python3
"""Verify source transport/request cold storage against explicit native scatter writes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-yhm-state';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'transport_context':(0x2000687c,20),'request':(0x20016b70,20)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_yhm_state.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';data=app.read_bytes();app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';evidence={}
 for name,a,z in [('scatter-decoder',0x286f4,96),('zero-writer',0x3bc60,32),('scatter-table',0xc43ec,32)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==data[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+name+'.json');p.write_bytes(raw);evidence[p.name]={'sha256':sha(p),'address':a,'bytes':z}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';sections=''.join('.r1.yhm.'+n+' '+hex(a)+' : { *(.r1.yhm.'+n+') } ' for n,(a,z) in FIELDS.items());ld.write_text('SECTIONS { '+sections+' /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,capture_output=True)
  initial={};section_evidence={}
  for name,(a,z) in FIELDS.items():
   binary=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.r1.yhm.'+name,'-O','binary',str(elf),str(binary)],check=True);initial[name]=binary.read_bytes();assert initial[name]==bytes(z);section_evidence[name]={'address':a,'bytes':z,'sha256':sha(binary)}
  runs=[]
  for poison in (0xa5,0x5a,0xff,0x3c):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,data);u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);u.reg_write(UC_ARM_REG_SP,0x2003f000);writes=[]
   def hook(uc,access,address,size,value,_):
    if any(address<a+z and address+size>a for a,z in FIELDS.values()):writes.append({'pc':uc.reg_read(UC_ARM_REG_PC),'address':address,'bytes':size,'value':value})
   u.hook_add(UC_HOOK_MEM_WRITE,hook);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208
   expected=[{'pc':0x28726,'address':0x2000687c+i,'bytes':1,'value':0} for i in range(20)]+[{'pc':0x3bc6c,'address':0x20016b70+i,'bytes':4,'value':0} for i in range(0,20,4)];assert writes==expected
   for name,(a,z) in FIELDS.items():
    assert bytes(u.mem_read(a,z))==initial[name]
    source=Uc(UC_ARCH_ARM,UC_MODE_THUMB);source.mem_map(0x20000000,0x40000);source.mem_write(a-4,bytes([poison])*(z+8));source.mem_write(a,initial[name]);assert bytes(source.mem_read(a-4,z+8))==bytes([poison])*4+initial[name]+bytes([poison])*4
   runs.append({'ram_poison':poison,'native_writes':writes,'native_hex':{name:bytes(u.mem_read(a,z)).hex() for name,(a,z) in FIELDS.items()}})
 vp.write_text(json.dumps(dict(comparisons=len(runs),runs=runs,source_sections=section_evidence,scatter_entry='0x283a0',stop_before_runtime='0x27208',report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Explicit native cold writes and compiled initializer bytes verified; warm-reset lifecycle remains open','Isolated source ELF address/extent proof does not establish full source startup or canonical admission','Higher transport/registry/GPIO/runtime composition and original whole-image byte identity remain gates']),indent=2)+'\n');print('YHM state:',len(runs),'poisoned-RAM comparisons;40 initial bytes and25 explicit writes per run')
if __name__=='__main__':main()
