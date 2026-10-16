#!/usr/bin/env python3
"""Prove cold symbolic callback relocation against native initialization writes."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-fragment-state';CELL=0x20006960;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());unit=r['units'][0];obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';runs=[]
 for poison in (165,90,255,60):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);writes=[]
  def hook(u,access,a,n,v,_):
   if a<CELL+4 and a+n>CELL:writes.append({'pc':u.reg_read(UC_ARM_REG_PC),'address':a,'bytes':n,'value':v})
  u.hook_add(UC_HOOK_MEM_WRITE,hook);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(u.mem_read(CELL,4))==struct.pack('<I',0x3407d);runs.append({'poison':poison,'writes':writes})
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';data=d/'callback.bin';ld.write_text('SECTIONS { .callback 0x20006960 : { *(.r1.fragment.send_callback) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_ble_tx_queue_dispatch_type1=0x3407d',str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.callback','-O','binary',str(elf),str(data)],check=True);assert data.read_bytes()==struct.pack('<I',0x3407d);section_hash=sha(data)
 relocations=subprocess.check_output(['arm-none-eabi-objdump','-r',str(obj)],text=True);assert 'R_ARM_ABS32' in relocations and 'r1_ble_tx_queue_dispatch_type1' in relocations
 vp.write_text(json.dumps(dict(cold_runs=runs,source_owned_section={'address':CELL,'bytes':4,'sha256_at_native_target':section_hash,'native_target':'0x3407c','source_target':'r1_ble_tx_queue_dispatch_type1','symbolic_relocation':'R_ARM_ABS32'},report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Native-target link proves callback data relocation, not original provider instruction identity','Actual source-target relocation/execution is checked separately in fragment-tx graph','Warm state, concurrency, product initialization and physical queue delivery remain gated']),indent=2)+'\n');print('Fragment callback cold state: four poisons, symbolic type1 relocation matched')
if __name__=='__main__':main()
