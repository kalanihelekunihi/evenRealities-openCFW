#!/usr/bin/env python3
"""Native receive edge limits, sample output, live callback reloads and adapter composition."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-receive';C=0x200075c4;O=0x20002000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_stacmd_read_bit_native':(0x87b30,110),'r1_stacmd_read_bit_adapter_native':(0x969ec,16)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_receive.o'
 assert sha(obj)==r['units'][0]['object_sha256'] and '-falign-loops=1' in r['units'][0]['command']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';ghidra={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);ghidra[p.name]=sha(p)
 rows=[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in ENTRIES.values()]];(OUT/'evidence.json').write_text(json.dumps(dict(ownership_rows=rows,locked_ownership_changed=False,polls_per_edge=1000,nop_iterations=26,nops_per_iteration=4,output='Always stores uint32 (~sample)&1, including timeout',adapter='Actual receive body; copies full word even on failure',scope='Native Ghidra-MCP bytes and locked ownership rows; hardware timing unproven'),indent=2)+'\n')
 pairs=sorted({*(itertools.product((0,1,998,999,1000,1001),(0,999,1000))),*(itertools.product((999,1000),(0,1,998,999,1000,1001)))})
 counts={n:0 for n in ENTRIES};totals={'native':0,'source':0};read_calls={'native':0,'source':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd='+hex(C),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={}
  def hook(u,a,size,_):
   f=states[id(u)];side='source' if id(u)==id(machines[1]) else 'native'
   if bytes(u.mem_read(a,2))==b'\x00\xbf':f['nops']+=1;totals[side]+=1
   if a==0x1100020:event=('input',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1));value=0xffffffff
   elif a in (0x1100040,0x1100060):
    index=f['read_index'];f['read_index']+=1;first_calls=min(f['first']+1,1000)
    if index<first_calls:value=1 if index<f['first'] else f['first_exit']
    elif index==first_calls:value=f['sample']
    else:value=0 if index-first_calls-1<f['second'] else f['second_exit']
    event=('read',a,u.reg_read(UC_ARM_REG_R0),value);read_calls[side]+=1
   else:
    if side=='source' and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   f['trace'].append(event)
   if f['mutation']:
    index=len(f['trace']);u.mem_write(C+12,struct.pack('<I',0x80000000+index));u.mem_write(C+40,struct.pack('<I',0x1100061))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,pair,sample,exits,mutation in itertools.product(ENTRIES,pairs,(0,1,2,0xffffffff),((0,1),(2,0xffffffff),(0xffffffff,2)),(False,True)):
   first,second=pair;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'nops':0,'read_index':0,'first':first,'second':second,'sample':sample,'first_exit':exits[0],'second_exit':exits[1],'mutation':mutation};u.mem_write(C-4,b'\x96'*116);u.mem_write(C+12,struct.pack('<I',33));u.mem_write(C+28,struct.pack('<I',0x1100021));u.mem_write(C+32,b'\x03');u.mem_write(C+40,struct.pack('<I',0x1100041));u.mem_write(O-4,struct.pack('<3I',0xaabbccdd,0x11223344,0x55667788));u.reg_write(UC_ARM_REG_R0,O);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=30000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==int(first<1000 and second<1000) and states[id(u)]['nops']==104
    assert struct.unpack('<3I',bytes(u.mem_read(O-4,12)))==(0xaabbccdd,(~sample)&1,0x55667788)
    assert states[id(u)]['read_index']==min(first+1,1000)+1+min(second+1,1000)
    results.append((states[id(u)]['trace'],bytes(u.mem_read(C-4,116)),bytes(u.mem_read(O-4,12))))
   assert results[0]==results[1],(name,pair,sample,exits,mutation,results);counts[name]+=1
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,edge_boundary_pairs=len(pairs),total_nops=totals,read_callback_counts=read_calls,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=ghidra,body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['GPIO/input/read callbacks are fixtures; adapter executes actual receive body','Timeouts still sample and store output; no null-pointer/device fallback added','Fixed configuration remains a test binding; shared typed registration unresolved','NOP counts do not prove physical timing/cycle scheduling; full frame/transport composition and byte identity open']),indent=2)+'\n');print('STACMD receive:',counts,totals,read_calls)
if __name__=='__main__':main()
