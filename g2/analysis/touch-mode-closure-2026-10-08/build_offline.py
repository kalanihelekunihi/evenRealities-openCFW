"""Build additive offline comparators. No Git or production mutations."""
from pathlib import Path
import argparse,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--pdl',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];touch=root/'g2/components/touch';a.output.mkdir(parents=True,exist_ok=True)
public=a.output/'public';subprocess.run([str(Path('/Users/kalani/.local/share/opencfw/venv/bin/python')),str(D.parent/'touch-msclp-attribution-2026-10-08/build_public.py'),'--gcc',str(a.gcc),'--pdl',str(a.pdl),'--output',str(public)],check=True)
link=a.output/'link.ld';link.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');common=['mode_offline/mode.c','mode_offline/cpu.c','config_bootstrap_offline/bootstrap.c'];configs={
 'mode':(common+['mode_offline/init.c'],['touch_switch_mode','touch_cap_init_fields','touch_wait_mrss','touch_switch_saturation_dependency']),
 'pins':(['pin_control_offline/pins.c'],['touch_config_pin','touch_config_electrodes','touch_config_shields','touch_config_cmod']),
 'init':(common+['mode_offline/init.c','mode_offline/capture.c'],['touch_cap_init','touch_capture_default']),
 'regular':(common+['mode_offline/regular.c','pin_control_offline/pins.c'],['touch_switch_regular_dependency']),
 'scan-mode':(common+['saturated_scan_offline/scan.c','max_raw_offline/max_raw.c','scan_watchdog_offline/watchdog.c','scan_frame_offline/frame.c'],['touch_execute_saturated','touch_switch_saturation_dependency']),
 'generator':(['frame_generation_offline/generator.c'],['touch_frame_mask','touch_adjust_divider','touch_generate_sensor','touch_generate_cdac','touch_generate_sensor_closed'])}
receipts={}
for name,(sources,roots) in configs.items():
 flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections',*['-Wl,-u,'+x for x in roots]];elf=a.output/(name+'.elf');args=[str(a.gcc),*flags,'-T',str(link),*[str(touch/x) for x in sources],'-I'+str(touch/'eeprom_offline'),'-I'+str(touch/'eeprom_init_offline')]
 if name in ['init','regular']:args.append(str(public/'public.o'))
 subprocess.run([*args,'-lgcc','-o',str(elf)],check=True);receipts[name]={'elf_path':str(elf),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'source_hashes':{str(touch/x):hashlib.sha256((touch/x).read_bytes()).hexdigest() for x in sources},'flags':flags}
(a.output/'receipt.json').write_text(json.dumps(receipts,indent=2)+'\n');print('Built6 offline comparator ELFs; use matching verify scripts. New layouts can have different ELF hashes.')
