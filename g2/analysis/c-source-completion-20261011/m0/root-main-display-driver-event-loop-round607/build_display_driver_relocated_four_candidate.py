#!/usr/bin/env python3
"""Build a relocatable display-driver object and compare imports to selected Apollo."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
analysis=Path(__file__).resolve().parent
callbacks=analysis.parent/'root-main-display-driver-callbacks-round605'
out=root/'build/c-firmware/root-main-display-driver-relocated-four-round683'
out.mkdir(parents=True,exist_ok=True)
sources=[callbacks/n for n in ('display_driver_callbacks.c','display_driver_attributes.c')]+[
 analysis/n for n in ('display_driver_event_loop.c','display_driver_aux.c',
                     'display_driver_timer_init.c','display_driver_timer_callback.c',
                     'display_buffer_unlock.c','display_driver_uled_status.c',
                     'display_driver_uled_init.c','display_driver_uled_identify.c',
                     'display_driver_brightness_convert.c','display_driver_max_lum.c',
                     'display_driver_ratio_cell.c','display_driver_case3_prelude.c',
                     'display_driver_position_setters.c','display_driver_submit_window.c',
                     'display_driver_prepare_update.c','display_driver_frame_prepare.c',
                     'display_driver_gpu_mode_wrappers.c','display_driver_gpu_mode_lower.c',
                     'display_driver_gpu_clear.c','display_driver_nema_select_clear.c',
                     'display_driver_settings_live.c','display_driver_dispatch_gate.c',
                     'display_driver_wear_detect.c','display_driver_case_status.c',
                     'display_driver_gpu_position.c',
                     'display_driver_nema_float_translate.c',
                     'display_driver_uled_options_relocated_four.c',
                     'display_driver_uled_work_buffer.c',
                     'display_driver_gpu_blit.c',
                     'display_driver_nema_mode_helpers.c',
                     'display_driver_nema_mode_tables.c',
                     'display_driver_nema_mode.c',
                     'display_driver_uled_row_callback.c')]
objects=[]
for source in sources:
 obj=out/(source.stem+'.o')
 flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
        '-std=c11','-ffreestanding','-fno-builtin','-O2']
 if source.name in ('display_driver_gpu_position.c','display_driver_nema_float_translate.c'):
  flags+=['-mfpu=fpv5-d16','-mfloat-abi=softfp']
 subprocess.run([*flags,'-c',str(source),'-o',str(obj)],check=True)
 objects.append(obj)
combined=out/'display-driver-combined.o'
subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(combined)],check=True)
undefined=[line.split()[-1] for line in subprocess.check_output(
 ['arm-none-eabi-nm','-u',str(combined)],text=True).splitlines()]
defined=[line.split()[-1] for line in subprocess.check_output(
 ['arm-none-eabi-nm','--defined-only',str(combined)],text=True).splitlines()]
receipt=json.loads((root/'build/c-firmware/root-main-round604/receipt.json').read_text())
selected=set(receipt['images']['apollo_main']['relocatable_link']['defined_symbols'])
result={'combined_object':str(combined.relative_to(root)),'combined_sha256':hashlib.sha256(combined.read_bytes()).hexdigest(),
 'sources':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
 'defined':sorted(set(defined)),'undefined':sorted(set(undefined)),
 'selected_provider_imports':sorted(set(undefined)&selected),
 'missing_helper_imports':sorted(set(undefined)-selected),
 'selected_source_complete':False}
(out/'link-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS_DISPLAY_DRIVER_COMBINED_LINK',len(result['defined']),len(result['selected_provider_imports']),len(result['missing_helper_imports']))
