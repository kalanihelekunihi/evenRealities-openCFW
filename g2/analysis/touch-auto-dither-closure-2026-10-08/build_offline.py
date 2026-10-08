"""Build only scratch offline comparators; public PDL object is an explicit input."""
from pathlib import Path
import argparse,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--public-object',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];touch=root/'g2/components/touch';a.output.mkdir(parents=True,exist_ok=True)
link=a.output/'link.ld';link.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
common=['all_slot_offline/slots.c','frame_generation_offline/generator.c','base_frame_offline/base.c','auto_dither_offline/dither.c','mode_offline/mode.c','mode_offline/cpu.c','pin_control_offline/pins.c','config_bootstrap_offline/bootstrap.c'];receipt={}
for name,sources,roots in [('base',['base_frame_offline/base.c'],[]),('dither',common,['touch_prepare_auto_dither','touch_switch_dither_dependency','touch_configure_auto_dither'])]:
 flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections',*['-Wl,-u,'+r for r in roots]]
 if name=='base':flags+=['-Wl,-u,touch_generate_base','-Wl,-u,touch_generate_modes','-Wl,-u,touch_generate_pin_functions']
 elf=a.output/(name+'.elf');cmd=[str(a.gcc),*flags,'-T',str(link),'-I'+str(touch/'eeprom_offline'),'-I'+str(touch/'eeprom_init_offline'),*[str(touch/s) for s in sources]]
 if name=='dither':cmd.append(str(a.public_object))
 subprocess.run([*cmd,'-lgcc','-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();receipt[name]={'elf':str(elf),'elf_sha256':h(elf),'sources':{str(touch/s):h(touch/s) for s in sources},'flags':flags}
receipt['public_object']={'path':str(a.public_object),'sha256':h(a.public_object),'pdl_pin':'35f1714623cfea682d5e285af80d50416b4c7bbc'};receipt['gcc']={'path':str(a.gcc),'sha256':h(a.gcc),'version':subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0]};(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Built base and dither offline comparators')
