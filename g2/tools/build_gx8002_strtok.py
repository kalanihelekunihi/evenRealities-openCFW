# SPDX-License-Identifier: MIT
"""Build the recovered stateful tokenizer for primary or backup placement."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build(backup=False):
    out=ROOT/('build/gx8002-backup-strtok' if backup else 'build/gx8002-strtok');out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_strtok.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os','-fno-tree-loop-optimize',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_strtok_saved':(0x2002d3e0 if backup else 0x2002e934)}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text PLACEHOLDER : { *(.text.open_cfw_gx8002_strtok) } }\n'.replace('PLACEHOLDER',hex(0x49c14-0x3b940+0x10003000) if backup else '0x1020995c')+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    assert section['size']<=112 and not any(s['name'] and s['section']==0 for s in elf.symbols())
    r={'backup':backup,'elf_sha256':sha(elfpath.read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':112,'stock_sha256':sha(stock[0x49c14:0x49c84] if backup else stock[0x12ee8:0x12f58]),'fits':section['size']<=112,'source_admitted':False,'limits':['Source tokenizer at selected entry and saved-state binding; caller integration and hardware require separate qualification.']}
    (ROOT/('docs/research/gx8002-backup-strtok-candidate.json' if backup else 'docs/research/gx8002-strtok-candidate.json')).write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
