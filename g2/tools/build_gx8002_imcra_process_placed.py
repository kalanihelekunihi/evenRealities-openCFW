# SPDX-License-Identifier: MIT
"""Experimental processing placement using spare source-FFT code envelope."""
import hashlib,json,subprocess
from probe_gx8002_imcra_process_lto import probe,ROOT
from build_transparent_image import Elf32

def build():
    evidence=probe();variant=evidence['experiments'][-1];assert variant['label']=='lto-register-barriers-shared-min'
    source=ROOT/'build/gx8002-imcra-process-lto-register-barriers-shared-min'
    out=ROOT/'build/gx8002-imcra-process-placed';out.mkdir(exist_ok=True)
    cluster_path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    if cluster_path.exists():
        startup=Elf32(cluster_path.read_bytes(),'startup')
        donor=next(s for s in startup.sections if s['name']=='.fft_code2')
        assert donor['address']==0x100143f4 and donor['size']==424
    else:
        # The previous failed relink left the authoritative disassembly but no ELF;
        # placement is fixed by the linker script below and revalidated on relink.
        donor={'address':0x100143f4,'size':424}
    address=donor['address']+donor['size'];end=0x100145d4
    assert address==0x1001459c
    occupied=[] if not cluster_path.exists() else [s for s in startup.sections if s['flags']&2 and s['size'] and s['address']<end and s['address']+s['size']>address]
    assert not occupied or (len(occupied)==1 and occupied[0]['name']=='.imcra_minimum' and occupied[0]['address']==address and occupied[0]['size']==36)
    original=(source/'process.ld').read_text()
    begin=original.index('SECTIONS');finish=original.index('\n',begin)
    script=original[:begin]+'''SECTIONS {
 .prepare 0x10015d34 : { *(.text.open_cfw_gx8002_imcra_process) }
 .minimum 0x1001459c : { *(.text.open_cfw_imcra_min_scan) }
}
'''+original[finish+1:]
    (out/'process.ld').write_text(script)
    objects=[str(source/(ROOT/p).stem)+'.o' for p in json.loads((ROOT/'docs/research/gx8002-imcra-process.json').read_text())['stage_sources']]
    objects.append(str(source/'shared_min.o'))
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    target=out/'process.elf'
    subprocess.run([pre+'gcc',*variant['flags'],'-save-temps=obj','-nostdlib','-Wl,-u,open_cfw_gx8002_imcra_process','-Wl,-T,'+str(out/'process.ld'),*objects,'-o',str(target)],check=True)
    # Assemble GCC's source-derived LTO output into a normal relocatable input.
    # This retains symbolic helper relocations; no linked image bytes are extracted.
    assembly=out/'process.elf.ltrans0.ltrans.s'
    native=out/'process-native.o'
    subprocess.run([pre+'gcc','-mcpu=ck804ef','-mhard-float','-c',str(assembly),'-o',str(native)],check=True)
    relinked=out/'process-native.elf'
    subprocess.run([pre+'ld','-T',str(out/'process.ld'),str(native),'-o',str(relinked)],check=True)
    original_elf=Elf32(target.read_bytes(),'LTO')
    native_elf=Elf32(relinked.read_bytes(),'native relink')
    for section in original_elf.sections:
        if section['flags']&2 and section['size']:
            other=next(s for s in native_elf.sections if s['name']==section['name'])
            assert other['address']==section['address']
            assert native_elf.contents(other)==original_elf.contents(section)
    obj=Elf32(native.read_bytes(),'source native object')
    assert not any(s['name'].startswith('.gnu.lto_') for s in obj.sections)
    expected=set(json.loads((ROOT/'docs/research/gx8002-imcra-process.json').read_text())['helper_bindings'])
    assert {s['name'] for s in obj.symbols() if s['name'] and s['section']==0}==expected
    elf=Elf32(target.read_bytes(),'placed');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert {s['name'] for s in sections}=={'.prepare','.minimum'}
    sizes={s['name']:s['size'] for s in sections}
    assert sizes['.prepare']<=0x4f10e-0x4e674 and sizes['.minimum']<=end-address
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    symbols={s['name']:s['value'] for s in elf.symbols()}
    assert symbols['open_cfw_gx8002_imcra_process']==0x10015d34
    assert symbols['open_cfw_imcra_min_scan']==address
    (out/'process.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'native_object':str(native.relative_to(ROOT)),'native_relink_exact':True,'elf_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'startup_donor_elf_sha256':hashlib.sha256(cluster_path.read_bytes()).hexdigest() if cluster_path.exists() else None,'entry':symbols['open_cfw_gx8002_imcra_process'],'compiler_variant':variant,'sizes':sizes,'minimum_address':address,'minimum_capacity':end-address,'source_admitted':False,'startup_integrated':False,'limits':['Experimental layout; donor interval checked against current allocated startup sections.', 'Repurposed FFT code-envelope permissions/reference closure inherit existing limitations.', 'Relinked code requires continuous verification; no complete firmware or hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-process-placed.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
