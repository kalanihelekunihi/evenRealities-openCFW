# SPDX-License-Identifier: MIT
"""Build recovered denoise control flow with explicit unresolved subsystem bindings."""
import json,subprocess
from analyze_gx8002_backup_denoise_initialize import analyze,ROOT,sha,Elf32


def build():
    evidence=analyze();out=ROOT/'build/gx8002-backup-denoise-initialize'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_denoise_initialize.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-fno-builtin','-ffreestanding','-ffunction-sections','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'initialize.o')],check=True)
    helpers={'denoise_status_3c8f8':0x3c8f8,'denoise_prepare_428e8':0x428e8,'denoise_prepare_42850':0x42850,'denoise_rate_428c0':0x428c0,'denoise_allocate_4286c':0x4286c,'denoise_drc_470c4':0x470c4,'denoise_beamforming_44140':0x44140,'denoise_imcra_4425c':0x4425c,'denoise_audio_42d58':0x42d58,'denoise_callback_44694':0x44694,'printf':0x42274}
    bindings={name:offset-0x38940+0x10000000 for name,offset in helpers.items()}
    messages={'start':0x10013990,'none':0x100139f4,'rate':0x100137b4,'drc_ok':0x10013800,'double':0x100139b8,'double_fail':0x1001381c,'single':0x10013894,'single_fail':0x100138c8,'drc_fail':0x100137d4,'audio_fail':0x10013a1c,'audio_ok':0x10013a4c,'ok':0x10013a74}
    assert all(hex(address) in evidence['strings'] for address in messages.values())
    bindings.update({'denoise_msg_'+name:address for name,address in messages.items()});bindings['backup_denoise_state']=0x2002d2bc
    ld='SECTIONS { .denoise_init 0x1000bc44 : { *(.text*) } }\n'+''.join(f'{name} = {value:#x};\n' for name,value in bindings.items())
    (out/'initialize.ld').write_text(ld);path=out/'initialize.elf';subprocess.run([pre+'ld','-T',str(out/'initialize.ld'),str(out/'initialize.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'denoise init');alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    size=alloc[0]['size']
    disassembly=subprocess.check_output([pre+'objdump','-d',str(path)],text=True)
    (out/'initialize.disassembly.txt').write_text(disassembly)
    from verify_gx8002_memcpy_source import decode
    code=decode(disassembly)
    assert size<=272 and bindings['backup_denoise_state']%4==0
    assert not any(op in ('ld.b','st.b') for op,args,width in code.values())
    assert any(op=='ld.w' and args.endswith(', 0x10)') for op,args,width in code.values())
    assert any(op=='st.w' and args.endswith(', 0x18)') for op,args,width in code.values())
    report={'analysis':evidence,'source_sha256':sha(source.read_bytes()),'bytes':size,'envelope_bytes':272,'fits':size<=272,'state_alignment':4,'word_accesses_verified':True,'bindings':bindings,'source_admitted':False,'limits':['Control flow translated to C; exact helper signatures remain provisional ABI declarations. Helper/string/state bindings explicit. Decoded equivalence and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-denoise-initialize-build.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print({k:v for k,v in build().items() if k in ('bytes','fits')})
