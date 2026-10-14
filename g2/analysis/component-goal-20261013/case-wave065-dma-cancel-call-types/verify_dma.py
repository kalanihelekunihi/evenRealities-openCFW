from pathlib import Path
import json,struct,hashlib,itertools,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';raw=F.read_bytes()[32:];E=H/'callback-fixture.elf';link=json.loads((H/'final/receipt.json').read_text())['link_command'].copy();link[1:1]=['-ucase_uart_dma_abort_callback','-ucase_dma_abort_it'];link[-1]=str(E);subprocess.run(link,check=True)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
D=0x20003000;P=0x20004000;UART=0x20005000;CH=0x20005100;CTRL=0x20005200;BANK=0x20005300;MUX=0x20005400;CLEARS=0x20005500;SP=0x20002c88;STOP=0x801ff00
# Branch negative control: fallback skips the other predecessor's MOVR0,R4.
op=struct.unpack_from('<H',raw,0x6050)[0];assert op==0xe00d;target=0x8006050+4+2*(op&2047);assert target==0x800606e and target!=0x800606c
rows=[]
def run(kind,source,status,has_cb,mux_present,seed,mask,channel):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x8000000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x2000)
 if source:
  for a,d in segs:u.mem_write(a,d)
 else:u.mem_write(0x8000000,raw)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def half(a,v):u.mem_write(a,struct.pack('<H',v&65535))
 w(D,UART);w(D+128,P);half(D+86,0x1234);half(D+94,0xabcd)
 w(P,CH);w(P+40,D);w(P+64,BANK);w(P+68,channel);w(P+72,CTRL);w(P+76,CLEARS);w(P+80,0x12345678);w(P+84,MUX if mux_present else 0);w(P+88,CLEARS+16);w(P+92,0x87654321)
 for a in [CH,CTRL,MUX]:w(a,seed)
 u.mem_write(P+36,bytes([0x55,status]));w(UART,32);w(UART+8,64);w(UART+28,0x28)
 cb=0x80086e1 if not source else syms['case_uart_dma_abort_callback' if kind=='low_abort' else 'case_boot_sensor_cancel_callback']
 w(P+56,cb if has_cb else 0)
 source_entry={'low_abort':'case_dma_abort_it','high_ready':'case_boot_sensor_irq_restart_ready','high_irq':'case_irq_child_5f50'}[kind];native_entry=0x8005f51 if kind=='high_irq' else 0x80048e7
 callback_calls=[];low=SP
 def hook(uc,pc,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP))
  if pc==(cb&~1):callback_calls.append(uc.reg_read(UC_ARM_REG_R0))
  if pc==STOP:uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_R0,D if kind=='high_irq' else P);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 u.emu_start(syms[source_entry] if source else native_entry,0,count=100000);assert u.reg_read(UC_ARM_REG_PC)==STOP
 expected_calls=1 if (kind=='high_irq' or (status==2 and has_cb)) else 0
 assert callback_calls==[P]*expected_calls,callback_calls
 mem=bytearray(u.mem_read(D,0x2800));slot=P-D+56
 # Only the source/native cancellation function pointer identity differs.
 observed=struct.unpack_from('<I',mem,slot)[0]
 if kind=='high_irq':assert observed==cb
 else:assert observed==(cb if has_cb else 0)
 mem[slot:slot+4]=bytes(4)
 ret=u.reg_read(UC_ARM_REG_R0) if kind!='high_irq' else None
 if ret is not None:assert ret==(0 if status==2 else 1)
 return dict(R0_status=ret,callback_arguments=callback_calls,fixture_RAM=bytes(mem).hex(),PRIMASK=u.reg_read(UC_ARM_REG_PRIMASK),bounded_stack_bytes=SP-low)
for kind,status,has_cb,mux,seed,mask,channel in itertools.product(['low_abort','high_ready','high_irq'],[1,2],[False,True],[False,True],[0,0xffffffff],[0,1],[0,12]):
 if kind=='high_irq' and not has_cb:continue # dispatcher installs its own callback
 a=run(kind,False,status,has_cb,mux,seed,mask,channel);b=run(kind,True,status,has_cb,mux,seed,mask,channel)
 assert {k:v for k,v in a.items() if k!='bounded_stack_bytes'}=={k:v for k,v in b.items() if k!='bounded_stack_bytes'},(kind,status,has_cb,mux,seed,mask,channel)
 rows.append(dict(kind=kind,DMA_state=status,initial_callback=has_cb,mux_present=mux,register_seed=hex(seed),PRIMASK=mask,DMA_channel_index=channel,native_stack_bytes=a['bounded_stack_bytes'],source_stack_bytes=b['bounded_stack_bytes'],callback_arguments=a['callback_arguments'],return_status=a['R0_status']))
r=dict(status='PASS_160_REAL_DMA_CANCELLATION_PATH_PAIRS',cases=len(rows),comparisons=rows,native_fallback_branch_control=dict(PC='08006050',opcode=hex(op),target=hex(target),skipped_MOV='0800606c',argument='DMAp preserved; no UARTdescriptor substitution'),source_fixture_ELF_sha256=hashlib.sha256(E.read_bytes()).hexdigest(),production_ELF_sha256=hashlib.sha256((H/'final/case.elf').read_bytes()).hexdigest(),fixture_link_command=link,limits=['Fixture relinks only real source objects, retaining otherwise unreferenced lowDMA provider/callback; production artifact unchanged', 'Plain RAM-backed synthetic register inputs; no peripheral timing/readybit emulation or physical behavior claim','Actual native/source helpers, dispatcher, callback bodies and weak error callback execute; no provider stubs/entry cuts','Two separately named recovered source providers implement same native48e6 path; low targetvoid(uint8*) and high targetuint32(uint32) checked by slot provenance','Only callback-code pointer identity normalized; allfixturememory/status/PRIMASK compare','Synchronous fixtures exclude hardwareIRQdelivery/reentrancy/asynchronous lifetime/globalstack'])
assert len(rows)==160;(H/'dma-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(rows))
