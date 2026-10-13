from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-packet-drivers-connected-round226';W=lambda x:struct.pack('<I',x&0xffffffff);P=0x20001000;DATA=0x20002000;DESC=0x20073db0
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 t=Path(t);sources=[]
 a=selected.index('static void packet_store');z=selected.find('\n#include',a);s=(B/'root-nema-sector-chain-packet-round225/candidate.c').read_text().split('static void packet_store')[0]+selected[a:z if z>=0 else len(selected)];p=t/'packet.c';p.write_text(s);sources.append(p)
 a=selected.index('void *audio_uart_nema_pool_select_514050');z=selected.index('/* Native5140c6',a);p=t/'pool.c';p.write_text('#include <stdint.h>\n'+selected[a:z]);sources.append(p)
 a=selected.index('/* Native5140ea..51411a:');z=selected.index('/* Native51411a',a);p=t/'flush.c';p.write_text('#include <stdint.h>\nextern void *audio_uart_nema_pool_select_514050(uint32_t);\nextern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *);\n'+selected[a:z]);sources.append(p)
 a=selected.index('static uint32_t clean_read');z=selected.find('\n#include',a);p=t/'clean.c';p.write_text('#include <stdint.h>\n'+selected[a:z]);sources.append(p)
 a=selected.index('extern const uint32_t audio_uart_nema_register_base');z=selected.find('\n#include',a);p=t/'reg.c';p.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_last_submission;\n'+selected[a:z]);sources.append(p)
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};e=t/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-u,audio_uart_nema_chain_finalize_523dba','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_sector_finalize_523ce0','-Wl,--defsym=audio_uart_nema_ring_descriptor=0x20073db0','-Wl,--defsym=audio_uart_nema_register_base=0x78f2f4','-Wl,--defsym=audio_uart_nema_last_submission=0x20002e08']+[str(p) for p in sources]+['-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,mode,words,capacity,index,sequence,cache,enabled):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40090000,4096);u.mem_map(0xe0000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,W(256)+W(3)+W(DATA)+W(0x20008003)+W(index)+W(sequence)+bytes(8));u.mem_write(DATA,bytes([165])*256);u.mem_write(DESC,W(P)+W(DATA)+W(0x20008003)+W(capacity)+W(0));u.mem_write(0x20000338,bytes(28));u.mem_write(0x20000350,bytes([cache]));u.mem_write(0x2000300c,W(0x20008003));u.mem_write(0xe000ed14,W((1<<16) if enabled else 0));trace=[];barriers=[]
  def hook(uc,a,n,user):
   code=bytes(uc.mem_read(a,n))
   if code==bytes.fromhex('bff34f8f'):barriers.append('DSB')
   if code==bytes.fromhex('bff36f8f'):barriers.append('ISB')
  def mem(uc,access,a,n,v,user):
   if 0x40090000<=a<0x40091000 or 0xe000ed00<=a<0xe000f000:trace.append((access,a,n,v&((1<<(8*n))-1) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  names=['audio_uart_nema_sector_finalize_523ce0','audio_uart_nema_chain_finalize_523dba'];native=[0x523ce0,0x523dba];u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0x20003000 if mode else 0x20008003);u.reg_write(UC_ARM_REG_R1,words);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[names[mode]] if isc else native[mode])|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return trace,barriers,bytes(u.mem_read(P,32)).hex(),bytes(u.mem_read(DATA,256)).hex(),bytes(u.mem_read(DESC,20)).hex(),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1],[0,1],[4,16],[0,3],[0,0xffffff,0xffffffff],[0,1],[0,1]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_REAL_PACKET_POOL_FLUSH_SCB_REGISTER_GRAPH','cases':len(cases),'selected_fixture_sha256':hashes,'child_cuts':0,'limits':['Real pool selector/flush/cache-clean/register-write and sector/chain packets execute; RAM-backed SCB/MMIO trace,barrier instruction trace,ring/descriptor/buffer/result/SP match.','Physical cache/MMIO/barrier effects,invalid pointers/ownership/scheduler/full-image/hardware remain unqualified; ordered arena bus trace not collected.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
