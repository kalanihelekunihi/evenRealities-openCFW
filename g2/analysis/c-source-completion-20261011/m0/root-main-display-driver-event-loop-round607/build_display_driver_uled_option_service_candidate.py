#!/usr/bin/env python3
"""Build main MSPI service with uLED vendors and two Ambiq-backed IRQ callbacks."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
here=Path(__file__).resolve().parent
out=root/'build/c-firmware/root-main-uled-option-service-round681'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
vendor=root/'build/c-firmware/root-main-uled-vendor-round678'
option=root/'build/c-firmware/root-main-uled-option-irq-round680'
vendor_audit=json.loads((vendor/'link-audit.json').read_text())
option_audit=json.loads((option/'link-audit.json').read_text())
vendor_object=vendor/'uled-vendor-candidate.o'
option_object=option/'option-irq-candidate.o'
assert sha(vendor_object)==vendor_audit['combined_sha256']
assert sha(option_object)==option_audit['combined_sha256']
source=here/'display_driver_uled_mspi_interrupt_service.c'
object_file=out/(source.stem+'.o')
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                '-Wall','-Wextra','-Werror','-O2','-c',str(source),'-o',str(object_file)],
               check=True)
combined=out/'uled-option-service-candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(vendor_object),str(option_object),
                str(object_file),'-o',str(combined)],check=True)
undefined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(combined)],text=True).splitlines()})
defined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','--defined-only',str(combined)],text=True).splitlines()})
assert not undefined,undefined
audit={'status':'relocatable candidate; MSPI service bounded native cases, option relocation open',
       'vendor_object_sha256':sha(vendor_object),
       'option_object_sha256':sha(option_object),
       'service_source_sha256':sha(source),
       'combined_object':str(combined.relative_to(root)),
       'combined_sha256':sha(combined),
       'defined':defined,'undefined':undefined,
       'option_callback_C_bodies':2,
       'option_callback_pointer_relocated':False,
       'source_complete':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_OPTION_SERVICE_CANDIDATE',len(defined),len(undefined))
