from pathlib import Path
import argparse, subprocess,json,hashlib
D=Path(__file__).resolve().parent;S=D.parent/'dependency-followup-2026-10-08/touch-source';p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
pdl=S/'mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc';core=S/'core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-fshort-enums','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections'];inc=['-I'+str(x) for x in [D,S,S/'cmsis',pdl/'drivers/include',pdl/'devices/include',core/'include']];objs=[]
for src in [D/'report_publish.c',pdl/'drivers/source/cy_scb_i2c.c']:
 o=a.output/(src.stem+'.o');subprocess.run([str(a.gcc),*flags,*inc,'-c',str(src),'-o',str(o)],check=True);objs.append(o)
elf=a.output/'publish.elf';subprocess.run([str(a.gcc.with_name('arm-none-eabi-ld')),'--gc-sections','-Ttext=0x100000','-e','touch_report_publish_slice',*[str(o) for o in objs],'-o',str(elf)],check=True)
r={'compiler':subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0],'flags':flags,'source_sha256':hashlib.sha256((D/'report_publish.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'public_source_provenance':'../dependency-followup-2026-10-08/source-provenance.json'};(a.output/'publish-build.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
