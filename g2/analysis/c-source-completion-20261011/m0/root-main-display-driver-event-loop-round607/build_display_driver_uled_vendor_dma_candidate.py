#!/usr/bin/env python3
"""Build the growing uLED vendor callback C candidate separately."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
here=Path(__file__).resolve().parent
out=root/'build/c-firmware/root-main-uled-vendor-round654'
out.mkdir(parents=True,exist_ok=True)
sources=[here/name for name in ('display_driver_uled_vendor_shutdown.c',
                                'display_driver_uled_mspi_status.c',
                                'display_driver_uled_mspi_destroy.c',
                                'display_driver_uled_mspi_dma_wrappers.c')]
objects=[]
for source in sources:
 obj=out/(source.stem+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                 '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                 '-Wall','-Wextra','-Werror','-O2','-c',str(source),
                 '-o',str(obj)],check=True)
 objects.append(obj)
combined=out/'uled-vendor-candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',*[str(x) for x in objects],
                '-o',str(combined)],check=True)
undefined={line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(combined)],text=True).splitlines()}
defined={line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','--defined-only',str(combined)],text=True).splitlines()}
receipt=json.loads((root/'build/c-firmware/root-main-round604/receipt.json').read_text())
selected=set(receipt['images']['apollo_main']['relocatable_link']['defined_symbols'])
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
audit={'status':'candidate callback subset; vendor and whole-image gates open',
       'combined_object':str(combined.relative_to(root)),
       'combined_sha256':sha(combined),
       'sources':{str(p.relative_to(root)):sha(p) for p in sources},
       'defined':sorted(defined),'undefined':sorted(undefined),
       'selected_provider_imports':sorted(undefined&selected),
       'missing_helper_imports':sorted(undefined-selected),
       'source_complete':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_VENDOR_CANDIDATE_LINK',len(defined),
      len(audit['selected_provider_imports']),len(audit['missing_helper_imports']))
