#!/usr/bin/env python3
"""Trial-link selected Apollo, display, and uLED vendor C; audit option owners."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'build/c-firmware/root-main-round604'
display=root/'build/c-firmware/root-main-display-driver-round615'
vendor=root/'build/c-firmware/root-main-uled-vendor-round678'
out=root/'build/c-firmware/root-main-display-uled-integration-round679'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((base/'receipt.json').read_text())
selected_link=receipt['images']['apollo_main']['relocatable_link']
display_audit=json.loads((display/'link-audit.json').read_text())
vendor_audit=json.loads((vendor/'link-audit.json').read_text())
selected=base/'apollo_main/candidate.o'
display_object=display/'display-driver-combined.o'
vendor_object=vendor/'uled-vendor-candidate.o'
assert sha(selected)==selected_link['output_sha256']
assert sha(display_object)==display_audit['combined_sha256']
assert sha(vendor_object)==vendor_audit['combined_sha256']
groups={'selected':set(selected_link['defined_symbols']),
        'display':set(display_audit['defined']),
        'vendor':set(vendor_audit['defined'])}
overlap={f'{a}/{b}':sorted(groups[a]&groups[b])
         for a,b in (('selected','display'),('selected','vendor'),('display','vendor'))}
assert all(not x for x in overlap.values()),overlap
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(display_object),
                str(vendor_object),'-o',str(candidate)],check=True)
undefined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(candidate)],text=True).splitlines()})

official=root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob=official.read_bytes()
assert sha(official)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
def option_words(address):
    offset=address-0x438000+32
    return [int.from_bytes(blob[offset+4*i:offset+4*i+4],'little') for i in range(16)]
option_records={'type1':option_words(0x70afe4),'type0':option_words(0x70b024)}
callbacks={kind:[value for value in words if value>1 and value&1]
           for kind,words in option_records.items()}
unique=sorted(set(callbacks['type0'])|set(callbacks['type1']))
assert len(callbacks['type0'])==14 and len(callbacks['type1'])==15
assert len(unique)==29,(len(unique),callbacks)
audit={'status':'candidate relocatable integration; native option callbacks remain unowned',
       'selected_round':604,'selected_object_sha256':sha(selected),
       'display_object_sha256':sha(display_object),
       'vendor_object_sha256':sha(vendor_object),
       'integrated_object_sha256':sha(candidate),
       'duplicate_definitions':overlap,
       'unresolved_symbols':undefined,'integrated_unresolved_after':len(undefined),
       'vendor_defined_symbols':len(groups['vendor']),
       'option_callback_entries':{k:len(v) for k,v in callbacks.items()},
       'option_callback_unique_thumb_addresses':[f'0x{x:08x}' for x in unique],
       'option_callback_source_owned_in_candidate':0,
       'resident_rom_0x40_behavior_proven':False,
       'callback_pointer_relocation_complete':False,
       'source_complete':False,'whole_image_linked':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_DISPLAY_ULED_APOLLO_CANDIDATE',len(groups['vendor']),
      len(undefined),len(unique))
