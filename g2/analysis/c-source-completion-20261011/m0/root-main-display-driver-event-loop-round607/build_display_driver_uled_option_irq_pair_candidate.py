#!/usr/bin/env python3
"""Build two native-matched option IRQ callbacks with pinned Ambiq providers."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
here=Path(__file__).resolve().parent
out=root/'build/c-firmware/root-main-uled-option-irq-round680'
out.mkdir(parents=True,exist_ok=True)
sources=[here/'display_driver_uled_option_irq_pair.c',
         root/'components/foundation/ambiq_mspi/ambiq_mspi_interrupts.c']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
objects=[]
for source in sources:
    obj=out/(source.stem+'.o')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-Wall','-Wextra','-Werror','-O2','-c',str(source),'-o',str(obj)],
                   check=True)
    objects.append(obj)
combined=out/'option-irq-candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',*[str(o) for o in objects],
                '-o',str(combined)],check=True)
def names(mode):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',mode,str(combined)],text=True).splitlines()})
undefined=names('-u')
defined=names('--defined-only')
assert undefined==['am_hal_mspi_interrupt_service'],undefined
provenance=root/'components/foundation/ambiq_mspi/SOURCE_PROVENANCE.json'
audit={'status':'two option callbacks and pinned Ambiq interrupt status/clear C; service open',
       'combined_object':str(combined.relative_to(root)),
       'combined_sha256':sha(combined),
       'sources':{str(p.relative_to(root)):sha(p) for p in sources},
       'foundation_provenance_sha256':sha(provenance),
       'defined':defined,'undefined':undefined,
       'option_callback_source_owned_in_candidate':['0x00592659','0x005bbd49'],
       'option_callback_pointer_relocated':False,
       'source_complete':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_OPTION_IRQ_PAIR_CANDIDATE',len(defined),len(undefined))
