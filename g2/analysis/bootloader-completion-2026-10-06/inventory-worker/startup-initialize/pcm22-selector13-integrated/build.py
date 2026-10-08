"""Build a separate three-slot successor from pinned objects and six owned sources."""
from pathlib import Path
import json,hashlib,shutil,subprocess
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
base=ROOT/'g2/build/bootloader-completion/pcm22-selector9-integrated/7ffc7b0eafdf7e6fd13eaaeaacac1c1ea3826f7f1f32d52d73604d17ae84e651'
m=json.loads((base/'input-hashes.json').read_text());t=Path('/tmp/opencfw-pcm22-selector13-successor');t.mkdir(exist_ok=True);objects=[]
for i,row in enumerate(m['inputs']):
 src=base/row['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==row['sha256'];o=t/'inputs'/str(i)/Path(row['original']).name;o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,o);objects.append(str(o))
flags=['--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=softfp','-O1','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fshort-enums','-mfpu=fpv5-sp-d16']
for n in ['initialized_data','pcm22_sequence13']:
 o=t/(n+'.o');subprocess.run(['clang',*flags,'-I',str(ROOT/'g2/components/bootloader/initializer_callbacks'),'-I',str(ROOT/'g2/components/bootloader/platform_control'),'-c',str(HERE/(n+'.c')),'-o',str(o)],check=True)
 if n=='initialized_data':
  idx=next(i for i,x in enumerate(objects) if Path(x).name==n+'.o');shutil.copy2(o,objects[idx])
 else:objects.append(str(o))
elf=t/'candidate.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-T',str(HERE/'module.ld'),'-o',str(elf),*objects],check=True)
h=hashlib.sha256(elf.read_bytes()).hexdigest();(HERE/'build-inputs.json').write_text(json.dumps(dict(base=str(base),flags=flags,objects=objects,elf=str(elf),sha256=h),indent=2)+'\n');print(h,len(objects))
