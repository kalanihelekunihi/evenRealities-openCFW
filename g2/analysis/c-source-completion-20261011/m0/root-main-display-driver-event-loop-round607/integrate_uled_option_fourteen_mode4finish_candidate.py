#!/usr/bin/env python3
"""Trial-link eight source-owned option callbacks into Apollo-main display C."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'build/c-firmware/root-main-round604'
display=root/'build/c-firmware/root-main-display-driver-relocated-fourteen-round699'
option=root/'build/c-firmware/root-main-uled-option-service-round681'
out=root/'build/c-firmware/root-main-uled-option-fourteen-mode4finish-integration-round700'
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
setup_source=Path(__file__).resolve().parent/'display_driver_uled_option_setup_pair.c'
enable_source=Path(__file__).resolve().parent/'display_driver_uled_option_enable_pair_bothfinishbound.c'
setup_object=out/'display_driver_uled_option_setup_pair.o'
enable_object=out/'display_driver_uled_option_enable_pair.o'
pin_source=Path(__file__).resolve().parent/'display_driver_uled_option_pin_prepare_pair.c'
pin_object=out/'display_driver_uled_option_pin_prepare_pair.o'
pre_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_pre.c'
pre_object=out/'display_driver_uled_option_type1_pre.o'
power_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_power_pmicbound.c'
power_object=out/'display_driver_uled_option_type1_power_pmicbound.o'
pmic_source=Path(__file__).resolve().parent/'display_driver_uled_option_pmic_helpers.c'
pmic_object=out/'display_driver_uled_option_pmic_helpers.o'
transport_source=Path(__file__).resolve().parent/'display_driver_uled_option_pmic_transport.c'
transport_object=out/'display_driver_uled_option_pmic_transport.o'
type0_pre_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_pre.c'
type0_pre_object=out/'display_driver_uled_option_type0_pre.o'
mode4_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mode4.c'
mode4_object=out/'display_driver_uled_option_type0_mode4.o'
ldo_find_source=Path(__file__).resolve().parent/'display_driver_uled_option_ldo_find.c'
ldo_find_object=out/'display_driver_uled_option_ldo_find.o'
ldo_helpers_source=Path(__file__).resolve().parent/'display_driver_uled_option_ldo_helpers.c'
ldo_helpers_object=out/'display_driver_uled_option_ldo_helpers.o'
frame_source=Path(__file__).resolve().parent/'display_driver_uled_option_frame_start_pair.c'
frame_object=out/'display_driver_uled_option_frame_start_pair.o'
finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_finish.c'
finish_object=out/'display_driver_uled_option_type1_finish.o'
buck_source=Path(__file__).resolve().parent/'display_driver_uled_option_buck0_enable.c'
buck_object=out/'display_driver_uled_option_buck0_enable.o'
bus_source=Path(__file__).resolve().parent/'display_driver_uled_flash_bus_prepare.c'
bus_object=out/'display_driver_uled_flash_bus_prepare.o'
type0_finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_finish.c'
type0_finish_object=out/'display_driver_uled_option_type0_finish.o'
mode4_finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mode4_finish.c'
mode4_finish_object=out/'display_driver_uled_option_type0_mode4_finish.o'
for source,obj in ((setup_source,setup_object),(enable_source,enable_object),(pin_source,pin_object),(pre_source,pre_object),(power_source,power_object),(pmic_source,pmic_object),(transport_source,transport_object),(type0_pre_source,type0_pre_object),(mode4_source,mode4_object),(ldo_find_source,ldo_find_object),(ldo_helpers_source,ldo_helpers_object),(frame_source,frame_object),(finish_source,finish_object),(buck_source,buck_object),(bus_source,bus_object),(type0_finish_source,type0_finish_object),(mode4_finish_source,mode4_finish_object)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(source),'-o',str(obj)],check=True)
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(leaf_source),'-o',str(leaf_object)],check=True)
assert sha(selected)==selected_link['output_sha256']
assert sha(display_object)==display_audit['combined_sha256']
assert sha(option_object)==option_audit['combined_sha256']
groups={'selected':set(selected_link['defined_symbols']),
        'display':set(display_audit['defined']),
        'option_service':set(option_audit['defined']),
        'leaf':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(leaf_object)],text=True).splitlines()},
        'setup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(setup_object)],text=True).splitlines()},
        'enable':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(enable_object)],text=True).splitlines()},
        'pin_prepare':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_object)],text=True).splitlines()},
        'type1_pre':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pre_object)],text=True).splitlines()},
        'type1_power':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(power_object)],text=True).splitlines()},
        'pmic_helpers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pmic_object)],text=True).splitlines()},
        'pmic_transport':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transport_object)],text=True).splitlines()},
        'type0_pre':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_pre_object)],text=True).splitlines()},
        'mode4':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mode4_object)],text=True).splitlines()},
        'ldo_find':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ldo_find_object)],text=True).splitlines()},
        'ldo_helpers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ldo_helpers_object)],text=True).splitlines()},
        'frame_start':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(frame_object)],text=True).splitlines()},
        'type1_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(finish_object)],text=True).splitlines()},
        'buck0_enable':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buck_object)],text=True).splitlines()},
        'flash_bus':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(bus_object)],text=True).splitlines()},
        'type0_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_finish_object)],text=True).splitlines()},
        'mode4_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mode4_finish_object)],text=True).splitlines()}}
overlap={f'{a}/{b}':sorted(groups[a]&groups[b]) for i,a in enumerate(groups) for b in list(groups)[i+1:]}
assert all(not x for x in overlap.values()),overlap
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(display_object),
                str(option_object),str(leaf_object),str(setup_object),str(enable_object),str(pin_object),str(pre_object),str(power_object),str(pmic_object),str(transport_object),str(type0_pre_object),str(mode4_object),str(ldo_find_object),str(ldo_helpers_object),str(frame_object),str(finish_object),str(buck_object),str(bus_object),str(type0_finish_object),str(mode4_finish_object),'-o',str(candidate)],check=True)
undefined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(candidate)],text=True).splitlines()})
assert len(undefined)>=617,len(undefined)
relocations=subprocess.check_output(['arm-none-eabi-readelf','-r',
                                     str(display/'display_driver_uled_options_relocated_fourteen.o')],
                                    text=True)
assert 'contains 14 entries' in relocations,relocations
assert relocations.count('R_ARM_ABS32')==14,relocations
audit={'status':'candidate relocatable link with fourteen source-owned uLED option callback entries',
       'selected_round':604,'selected_object_sha256':sha(selected),
       'display_object_sha256':sha(display_object),
       'option_service_object_sha256':sha(option_object),
       'integrated_object_sha256':sha(candidate),
       'duplicate_definitions':overlap,
       'unresolved_symbols':undefined,'integrated_unresolved_after':len(undefined),
       'option_callback_unique_total':29,
       'option_callback_C_bodies':14,
       'option_callback_relocation_entries':14,
       'option_callback_native_addresses_remaining':15,
       'leaf_object_sha256':sha(leaf_object),
       'setup_object_sha256':sha(setup_object),
       'enable_object_sha256':sha(enable_object),
       'pin_prepare_object_sha256':sha(pin_object),
       'type1_pre_object_sha256':sha(pre_object),
       'type1_power_object_sha256':sha(power_object),
       'pmic_helpers_object_sha256':sha(pmic_object),
       'pmic_transport_object_sha256':sha(transport_object),
       'type0_pre_object_sha256':sha(type0_pre_object),
       'mode4_object_sha256':sha(mode4_object),
       'ldo_find_object_sha256':sha(ldo_find_object),
       'ldo_helpers_object_sha256':sha(ldo_helpers_object),
       'frame_start_object_sha256':sha(frame_object),
       'type1_finish_object_sha256':sha(finish_object),
       'buck0_enable_object_sha256':sha(buck_object),
       'flash_bus_object_sha256':sha(bus_object),
       'type0_finish_object_sha256':sha(type0_finish_object),
       'mode4_finish_object_sha256':sha(mode4_finish_object),
       'source_complete':False,'whole_image_linked':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_OPTION_FOURTEEN_MODE4FINISH_APOLLO_INTEGRATION',len(undefined),14,15)
