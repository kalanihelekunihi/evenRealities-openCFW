# SPDX-License-Identifier: MIT
"""Reserve recovered audio/context buffers from C declarations, without payload bytes."""
import json,subprocess
from build_gx8002_backup_context_initialize import build as authenticate,ROOT,sha,Elf32,FLAGS


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-backup-context-storage';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_context_storage.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(ROOT/'build/upstream-nationalchip-lvp-kws/include'),'-c',str(source),'-o',str(out/'storage.o')],check=True)
    placements=[('context_header',0x20017700,120),('context_frames',0x20017780,11264),('output_samples',0x2001a380,6144),('microphone_samples',0x20030000,12288)]
    ld='SECTIONS {\n'+''.join(f'.backup_{name} {address:#x} (NOLOAD) : {{ *(.bss.backup_{name}) }}\n' for name,address,size in placements)+'}\n'
    (out/'storage.ld').write_text(ld);path=out/'storage.elf'
    subprocess.run([pre+'ld','-T',str(out/'storage.ld'),str(out/'storage.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'storage');alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==4
    for name,address,size in placements:
        section=next(s for s in alloc if s['name']=='.backup_'+name)
        assert section['type']==8 and section['address']==address and section['size']==size
        symbol=next(s for s in elf.symbols() if s['name']=='backup_'+name)
        assert symbol['value']==address and symbol['section']==section['index']
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    report={'initializer_evidence':evidence,'source_sha256':sha(source.read_bytes()),'storage_header_sha256':sha((source.parent/'runtime_gx8002_backup_context_storage.h').read_bytes()),'allocations':[{'name':n,'address':a,'bytes':s} for n,a,s in placements],'source_admitted':False,'limits':['Uninitialized storage declarations only. Microphone buffer is outside startup BSS clearing range, as in recovered layout. DMA ownership, complete access census and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-context-storage.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['allocations'])
