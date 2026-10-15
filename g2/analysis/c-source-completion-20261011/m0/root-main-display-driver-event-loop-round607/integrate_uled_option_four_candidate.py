#!/usr/bin/env python3
"""Trial-link four source-owned option callbacks into Apollo-main display C."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'build/c-firmware/root-main-round604'
display=root/'build/c-firmware/root-main-display-driver-relocated-four-round683'
option=root/'build/c-firmware/root-main-uled-option-service-round681'
out=root/'build/c-firmware/root-main-uled-option-four-integration-round683'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected_receipt=json.loads((base/'receipt.json').read_text())
selected_link=selected_receipt['images']['apollo_main']['relocatable_link']
display_audit=json.loads((display/'link-audit.json').read_text())
option_audit=json.loads((option/'link-audit.json').read_text())
selected=base/'apollo_main/candidate.o'
display_object=display/'display-driver-combined.o'
option_object=option/'uled-option-service-candidate.o'
leaf_object=out/'display_driver_uled_option_leaf_pair.o'
leaf_source=Path(__file__).resolve().parent/'display_driver_uled_option_leaf_pair.c'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(leaf_source),'-o',str(leaf_object)],check=True)
assert sha(selected)==selected_link['output_sha256']
assert sha(display_object)==display_audit['combined_sha256']
assert sha(option_object)==option_audit['combined_sha256']
groups={'selected':set(selected_link['defined_symbols']),
        'display':set(display_audit['defined']),
        'option_service':set(option_audit['defined']),
        'leaf':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(leaf_object)],text=True).splitlines()}}
overlap={f'{a}/{b}':sorted(groups[a]&groups[b]) for a,b in
         (('selected','display'),('selected','option_service'),('display','option_service'),('selected','leaf'),('display','leaf'),('option_service','leaf'))}
assert all(not x for x in overlap.values()),overlap
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(display_object),
                str(option_object),str(leaf_object),'-o',str(candidate)],check=True)
undefined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(candidate)],text=True).splitlines()})
assert len(undefined)==617,len(undefined)
relocations=subprocess.check_output(['arm-none-eabi-readelf','-r',
                                     str(display/'display_driver_uled_options_relocated_four.o')],
                                    text=True)
assert 'contains 4 entries' in relocations,relocations
assert relocations.count('R_ARM_ABS32')==4,relocations
audit={'status':'candidate relocatable link with four source-owned uLED option callback entries',
       'selected_round':604,'selected_object_sha256':sha(selected),
       'display_object_sha256':sha(display_object),
       'option_service_object_sha256':sha(option_object),
       'integrated_object_sha256':sha(candidate),
       'duplicate_definitions':overlap,
       'unresolved_symbols':undefined,'integrated_unresolved_after':len(undefined),
       'option_callback_unique_total':29,
       'option_callback_C_bodies':4,
       'option_callback_relocation_entries':4,
       'option_callback_native_addresses_remaining':25,
       'leaf_object_sha256':sha(leaf_object),
       'source_complete':False,'whole_image_linked':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_OPTION_FOUR_APOLLO_INTEGRATION',len(undefined),4,25)
