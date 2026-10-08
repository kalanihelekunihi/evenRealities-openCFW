#!/usr/bin/env python3
"""Account source-linked test ELF segments and every numeric linker alias.

This is a target-specific dependency ledger, not whole-payload completeness.
"""
import argparse,hashlib,json,re,datetime
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--linker',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();receipt=json.loads(args.receipt.read_text());assert receipt['status']=='PASS' and receipt['elf_sha256']==sha(args.elf)
 with args.elf.open('rb') as stream:
  elf=ELFFile(stream);segments=[dict(address=hex(seg['p_vaddr']),memory_bytes=seg['p_memsz'],file_bytes=seg['p_filesz'],flags=seg['p_flags'],sha256=hashlib.sha256(seg.data()).hexdigest()) for seg in elf.iter_segments() if seg['p_type']=='PT_LOAD'];symbols=elf.get_section_by_name('.symtab');names={sym.name for sym in symbols.iter_symbols()};symbol_values={sym.name:sym['st_value'] for sym in symbols.iter_symbols()};undefined=[sym.name for sym in symbols.iter_symbols() if sym.name and sym['st_shndx']=='SHN_UNDEF'];assert not undefined
 aliases=[]
 linker_text=args.linker.read_text()
 # The pinned linker is flattened before validation; reject omitted ledgers.
 assert not re.search(r'^\s*INCLUDE\s+',linker_text,re.M), 'flatten INCLUDE fragments into the pinned linker before manifesting'
 for name,raw in re.findall(r'^\s*(\w+)\s*=\s*(0x[0-9a-fA-F]+)\s*;',linker_text,re.M):
  address=int(raw,16);kind='explicit-fixture-provider-or-unexecuted-stock-alias'
  if address in [0x0200ff21,0x41,0x49]:kind='external-resident-ROM-API-body-absent-from-OTA'
  elif 0x08000000<=address<0x08010000:kind='named-test-provider-or-unrecovered-implementation-cut'
  aliases.append(dict(symbol=name,thumb_address=raw,kind=kind))
 mismatch=[]
 for raw,digest in receipt.get('source_sha256',{}).items():
  path=ROOT/raw
  if not path.exists() or sha(path)!=digest:mismatch.append(raw)
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Relocated source-linked bootloader test image. Segment execute permission includes rodata and padding; executable segment bytes are not instruction coverage. Every numeric alias is listed, including alternatives not reached by the receipt. No complete bootable payload, source closure or byte identity claim.',elf=str(args.elf),elf_sha256=sha(args.elf),linker=str(args.linker),linker_sha256=sha(args.linker),receipt=str(args.receipt),receipt_sha256=sha(args.receipt),receipt_status=receipt['status'],receipt_original_instruction_bytes=receipt['distinct_original_trace_bytes'],segments=segments,numeric_aliases=aliases,undefined_symbols=undefined,receipt_source_hash_mismatches=mismatch,authenticated_fixture_inputs=[dict(kind='initial-stack-value',bytes=4),dict(kind='compressed-initializer-data',bytes=695),dict(kind='application-vector',bytes=8)],modeled_interfaces=['Synthetic NOR ports and command completion, not physical persistence/latency/coherence','Selected mutex/kernel/delay/logger callbacks; basic exception delivery','External ROM0200ff20 status/program callback; no ROM body loaded','Lazy device-info41d792 field projection, not full status/delay effects','Generated288-byte update and RAM application/flag pages, no application instructions'],remaining_source_gaps=['Numeric aliases listed above must each be closed or justified as legitimate external APIs for a standalone payload','Generic CQ/descriptor execution alternatives, asynchronous progress and cancellation outside exercised source paths','Initializer child ADC/platform/service/RTOS APIs and remaining startup orchestration, ISR/deferred/cancellation/termination integration','Full payload vectors/assets/layout/data source definition and compiler reproduction'])
 # A numeric-boundary ledger must describe this ELF rather than a historical
 # fixture projection from an earlier profile.
 if 'opencfw_boot_device_info_query' in names:
  report['modeled_interfaces']=[x for x in report['modeled_interfaces'] if not x.startswith('Lazy device-info')]
  report['modeled_interfaces'].append('Native device-info mode1 query; silicon/core-debug values and resident-ROM delay remain synthetic inputs')
 if 'opencfw_boot_icache_enable' in names:
  report['modeled_interfaces'].append('Native cache startup and maintenance operands/barriers; synthetic SCB registers do not establish physical coherence')
 if 'opencfw_boot_initializer_callback_records' in names:
  report['modeled_interfaces'].append('Native initializer table/qsort/callback bodies; explicit child API cuts, synthetic ADC samples and six emulated stock FP64 instruction effects')
 if 'opencfw_provider_420002' in names:
  report['modeled_interfaces'].append('Native NOR timing/address/serial-mode chain; synthetic status registers, JEDEC response and immediate SPI completion')
 if symbol_values.get('opencfw_bl_kernel_state')==symbol_values.get('opencfw_boot_kernel_state') and 'opencfw_boot_kernel_state' in names:
  report['modeled_interfaces'].append('Kernel-state caller now binds native source; actual stock/source RAM flag queries have a separate73-case NOR wait comparison with modeled lower status/raw-delay/task-delay APIs. Normal immediately-ready paths may not enter this secondary wait branch.')
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(elf_sha256=report['elf_sha256'],numeric_aliases=len(aliases),source_hash_mismatches=len(mismatch),segments=len(segments))))
if __name__=='__main__':main()
