from pathlib import Path
import argparse,json,hashlib,shutil,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();m=json.loads((a.snapshot/'input-hashes.json').read_text());objects=[]
for i,row in enumerate(m['inputs']):
 src=a.snapshot/row['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==row['sha256'];dst=a.output.parent/'rebuild-inputs'/str(i)/Path(row['original']).name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);objects.append(str(dst))
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-T',str(a.snapshot/'source/module.ld'),'-o',str(a.output),*objects],check=True)
assert hashlib.sha256(a.output.read_bytes()).hexdigest()==m['elf_sha256'];print('PASS exact frozen-object rebuild',m['elf_sha256'])
