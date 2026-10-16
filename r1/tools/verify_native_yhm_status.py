#!/usr/bin/env python3
"""Verify raw saved-r3 status ABI and actual classifier composition without undefined C reads."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-yhm-status';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_yhm_status_native':(0x3529a,112),'r1_yhm_charge_state_native':(0x35272,40),'r1_native_charger_state_get':(0x50618,4)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_yhm_status.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 classifier_report=BASE/'native-charger-state/report.json';classifier=json.loads(classifier_report.read_text());classifier_object=classifier_report.parent/'native_charger_state.o';assert sha(classifier_object)==classifier['units'][0]['object_sha256']
 for p,h in classifier['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';evidence={}
 for name,(address,size) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{address:x}&length={size}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+size];p=OUT/('ghidra-'+name+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 rea=json.loads((OUT/'rea-body.json').read_text());assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';body=rea['normalized_result']['body'];assert body['total_bytes']==96 and body['span_bytes']==112 and body['ranges']==[{'start':'0x3529a','end':'0x352b9'},{'start':'0x352ca','end':'0x35309'}]
 row=next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0003529a');(OUT/'evidence.json').write_text(json.dumps(dict(ownership_row=row,locked_ownership_changed=False,body=body,jump_table_bytes=16,register_contract='Capture incoming r3 before readiness; initialize read word; restore full word to r3 on every returning path',read_contract='Register6 length1; transport result ignored; no-write retains incoming low byte',source_scope='Explicit ARM register moves in C source, noinline boundary; no uninitialized C read',compiler_portability_gate='Only selected emitted build verified; other compiler/prologue/LTO settings require revalidation'),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};read_counts={'native':0,'source':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_yhm_ready_native=0x1100001','--defsym=r1_yhm_register_read_native=0x1100011',str(obj),str(classifier_object),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={}
  def hook(u,address,size,_):
   f=states[id(u)];side='source' if id(u)==id(machines[1]) else 'native'
   if address in (0x3541c,0x1100000):f['trace'].append(('ready',));value=f['ready']
   elif address in (0x3540c,0x1100010):
    a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];assert a[:2]==[6,1];before=struct.unpack('<I',bytes(u.mem_read(a[2],4)))[0];assert before==f['incoming'];f['trace'].append(('read',a[0],a[1],before));read_counts[side]+=1
    if f['write'] is not None:u.mem_write(a[2],bytes([f['write']]))
    value=(0,1,0xffffffff)[f['incoming']%3];u.reg_write(UC_ARM_REG_R1,0xaabbccdd);u.reg_write(UC_ARM_REG_R2,0x12345678)
   else:
    if side=='source' and address<0x1000000 and address!=0x20000100:raise AssertionError(('source used native provider',hex(address)))
    return
   u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,low,high,ready,write in itertools.product(ENTRIES,range(256),(0,0x12345600,0xffffff00),(0,1,0xffffffff),(None,0,0xa0,0xc0,0xd0,0xe0,0xf0,0xff)):
   incoming=high|low;word=incoming if not ready or write is None else (incoming&0xffffff00)|write;raw=12 if not ready else ((word&255)>>4);raw=17 if raw==14 else raw;expected=raw if name=='r1_yhm_status_native' else 1 if 10<=raw<=12 else 2 if raw==13 else 0;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'incoming':incoming,'ready':ready,'write':write};u.reg_write(UC_ARM_REG_R3,incoming);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for index,reg in enumerate(saved):u.reg_write(reg,0x12345600+index)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+index for index in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_R3)==word,(name,incoming,ready,write,expected,hex(u.reg_read(UC_ARM_REG_R3)),hex(word));results.append(states[id(u)]['trace'])
   assert results[0]==results[1];counts[name]+=1
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,read_callback_counts=read_counts,full_r3_return_checked=True,all_low_bytes=True,high_word_patterns=3,report_sha256=sha(rp),object_sha256=sha(obj),classifier_report_sha256=sha(classifier_report),classifier_object_sha256=sha(classifier_object),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=evidence,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Readiness/transport remain fixtures; raw body executes inside actual classifier and adapter','Explicit r3 capture/restore verified for selected compiler/prologue and noinline boundary; other toolchains/LTO need revalidation','No-write semantics retained; valid device binding/actual transport policy is a separate graph','Full startup, physical GPIO/transport behavior and whole-image original byte identity remain open']),indent=2)+'\n');print('YHM raw status:',counts,read_counts)
if __name__=='__main__':main()
