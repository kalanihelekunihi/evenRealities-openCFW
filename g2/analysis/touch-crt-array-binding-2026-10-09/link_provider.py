from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/m['gcc']).parents[1];obj=T/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/crtbegin.o';out=O/'outputs';out.mkdir(exist_ok=True)
script=out/'bindings.ld';script.write_text('''SECTIONS {
 .text.deregister 0x33C0 : { *(.text.deregister_tm_clones) }
 .text.register 0x33E0 : { *(.text.register_tm_clones) }
 .text.dtors 0x3408 : { *(.text.__do_global_dtors_aux) }
 .text.frame 0x3434 : { *(.text.frame_dummy) }
 .eh_frame 0xB56C : { *(.eh_frame) }
 .init_array 0x2000087C : { *(.init_array) }
 .fini_array 0x20000880 : { *(.fini_array) }
 .tm_clone_table 0x20000884 : { *(.tm_clone_table) }
 .completed 0x200008A8 (NOLOAD) : { *(.bss.completed.1) }
 .object 0x200008AC (NOLOAD) : { *(.bss.object.0) }
 /DISCARD/ : { *(.rodata.all_implied_fbits) *(.data.__dso_handle) *(.ARM.attributes) }
}
__TMC_END__ = 0x20000884;
''')
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{T}:/tool:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','-T','/out/bindings.ld','/tool/lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/crtbegin.o','-o','/out/linked.elf'];p=subprocess.run(argv,capture_output=True,text=True)
result={'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr,'installed_provider_sha256':sha(obj),'link_script_sha256':sha(script),'source_revision':'a05ea1e5ee0867191bb432a84c055be99dbdbc16','source_rebuilt':False,'limits':'Authentic installed binary-provider/link attribution with official source interpretation. Generated internal GCC build headers/configuration absent; no invented tconfig.h/tsystem.h or source-rebuild claim. DSO/unused rodata not attributed by this script.'}
if not p.returncode:
 fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];rows=[]
 with (out/'linked.elf').open('rb') as f:
  for s in ELFFile(f).iter_sections():
   if s.name.startswith('.text.') or s.name in ['.init_array','.fini_array']:
    a=s['sh_addr'];d=s.data();flash=a if a<0x20000000 else 0xb58c+(a-0x200004c0);stock=b[flash-0x3300:flash-0x3300+len(d)];rows.append({'section':s.name,'address':hex(a),'image_flash':hex(flash),'bytes':len(d),'mismatches':[i for i,(x,y) in enumerate(zip(d,stock)) if x!=y],'provider_sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
 result.update(sections=rows,exact=all(not x['mismatches'] for x in rows),linked_elf_sha256=sha(out/'linked.elf'),binary_provider_text_bytes=152,array_data_bytes=8)
(O/'provider-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
