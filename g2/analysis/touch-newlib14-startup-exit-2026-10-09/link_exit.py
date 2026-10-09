"""Link genuine exit source object using bindings read from locked instructions."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2]
meta=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0]
tool=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/meta['gcc']).parents[1]
out=O/'outputs/exit'
script=out/'stock-bindings.ld'
script.write_text('SECTIONS { .text 0xA9AC : { *(.text.exit) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }\n_exit = 0xAA41;\n__stdio_exit_handler = 0x20000F54;\n')
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','-T','/out/stock-bindings.ld','/out/public.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True)
rec={'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr,'bindings':{'_exit':'0xAA41 Thumb','__stdio_exit_handler':'0x20000F54','__call_exitprocs':'undefined weak, stock literal zero'},'limits':'Provider-source/link evidence only. Halt provider, full vendor build and runtime exit composition not established.'}
if p.returncode==0:
 with (out/'linked.elf').open('rb') as f:d=ELFFile(f).get_section_by_name('.text').data()
 fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();stock=fw[32+0xa9ac-0x3300:32+0xa9ac-0x3300+len(d)]
 rec.update(bytes=len(d),mismatches=[i for i,(a,b) in enumerate(zip(d,stock)) if a!=b],linked_sha256=hashlib.sha256(d).hexdigest(),stock_sha256=hashlib.sha256(stock).hexdigest(),extent='[0xA9AC,0xA9D4)',historical_extent_overlap='historical54-byte row overlaps memset; preserved unchanged')
rec['inputs']={str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [out/'public.o',script]}
(O/'exit-link-results.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
