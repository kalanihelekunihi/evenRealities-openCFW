"""Recover SPOT selector table through actual locked scatter decoder instructions.
Source comparison executes reconstructed C with authenticated compressed DATA.
No stock executable is loaded by source machine; this is data recovery, not
source generation of compressed initializer bytes.
"""
from pathlib import Path
import hashlib,json,struct,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
image=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(image).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);args=ap.parse_args()
_,segments,symbols=elf.elf_info(args.elf)
record=0x433104
relative,count,destination=struct.unpack_from('<III',image,record-0x410000)
assert (record+relative,count,destination)==(0x4341c0,1250,0x20000000)
trace={}
def run(source):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for base,length in [(0x410000,0x25000),(0x10000,0x10000),(0x30000,0x10000),(0x08000000,0x20000),(0x20000000,0x40000)]:u.mem_map(base,length)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])

 else:u.mem_write(0x410000,image)
 u.mem_write(0x20000000,b'\xa5'*1372)
 done=False
 def hook(cpu,pc,size,_):
  nonlocal done
  if pc==0x08000000:done=True;u.emu_stop();return
  if not source:trace[pc]=bytes(u.mem_read(pc,size)).hex()
 u.hook_add(UC_HOOK_CODE,hook)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,record);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0)
 entry=(symbols['opencfw_boot_expand_adapter']&~1) if source else 0x415326
 u.emu_start(entry|1,0,count=200000);assert done
 return bytes(u.mem_read(0x20000000,1372)),u.reg_read(a.UC_ARM_REG_R0)
stock,sret=run(False);source,cret=run(True)
normalized=bytearray(source)
bindings=json.loads((HERE/'native-selector-bindings.json').read_text())['slots']
for slot,name in bindings.items():
 offset=0x158+4*int(slot)
 actual=struct.unpack_from('<I',source,offset)[0]
 assert actual==symbols[name]|1,(slot,hex(actual),name)
 normalized[offset:offset+4]=stock[offset:offset+4]
for offset,name in [(0x4d0,'opencfw_boot_dfu_thread_deinit_native'),(0x4f8,'opencfw_boot_manager_thread_deinit')]:
 actual=struct.unpack_from('<I',source,offset)[0]
 assert actual==(symbols[name]|1),(hex(offset),hex(actual),name)
 normalized[offset:offset+4]=stock[offset:offset+4]
assert stock==bytes(normalized) and sret==cret==record+12

assert hashlib.sha256(stock[:1371]).hexdigest()=='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
assert stock[1371]==0xa5
for pc,raw in trace.items():assert image[pc-0x410000:pc-0x410000+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
functions={int(d['entry'],16):d for d in map(json.loads,(ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
targets=struct.unpack_from('<27I',stock,0x158)
print('TARGETS',[(i,hex(t),(t&~1) in functions) for i,t in enumerate(targets)])
assert all((t&1) and 0x410000<=(t&~1)<0x435000 for t in targets)
result=dict(native_bindings=bindings,normalized_source_sha256=hashlib.sha256(bytes(normalized[:1371])).hexdigest(),raw_source_sha256=hashlib.sha256(source[:1371]).hexdigest(),status='PASS',elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(image).hexdigest(),record_address=hex(record),compressed_data_address='0x4341c0',compressed_data_bytes=625,compressed_data_sha256=hashlib.sha256(image[0x241c0:0x241c0+625]).hexdigest(),output_bytes=1371,output_sha256=hashlib.sha256(stock[:1371]).hexdigest(),callback_table_address='0x20000158',callback_table_bytes=108,callback_table_sha256=hashlib.sha256(stock[0x158:0x158+108]).hexdigest(),selectors=[dict(selector=i,thumb_target=hex(t),entry=hex(t&~1),body_bytes=functions.get(t&~1,{}).get('body_bytes'),body_sha256=functions.get(t&~1,{}).get('body_sha256')) for i,t in enumerate(targets)],vddc_rank=list(struct.unpack_from('<21I',stock,0xa4)),vddf_rank=list(struct.unpack_from('<21I',stock,0xf4)),original_trace={hex(p):raw for p,raw in sorted(trace.items())},limits=['Original decoder instructions and independent reconstructed source produce identical1371 initialized bytes. This recovers address-valued metadata; does not implement selector target bodies.','Source machine accepts no compressed DATA fixture; compiled source owns1371 initialized bytes and native pointer relocations. Unimplemented selector entries remain original-address contracts, guarded in root tests. Other scatter records and compressed-stream generation remain separate.','No hardware execution or original-toolchain/byte-identical build claim. Scatter adapter returns next record pointer exactly; R0 compared.'])
(HERE/'initialized-record-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS initialized1371bytes;27selector targets', [hex(x) for x in targets])
