#!/usr/bin/env python3
"""Build an independent CASE C ELF for linker diagnostics, never flashing."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args();output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
reloc=output.with_name(output.stem+'.reloc.o');layout=H/'case_clean_experimental_layout.ld'
subprocess.run([sys.executable,str(H/'build_case_command_startup_experiment.py'),'--output',str(reloc)],check=True,capture_output=True)
ld='/opt/homebrew/bin/arm-none-eabi-ld'
subprocess.run([ld,'-T',str(layout),str(reloc),'-o',str(output)],check=True)
nm=subprocess.run(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(output)],capture_output=True,text=True,check=True)
assert not nm.stdout.strip(),nm.stdout
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt={'status':'EXPERIMENTAL_ABSOLUTE_C_ELF_LINKED','output':str(output),'output_sha256':sha(output),
 'relocatable_object':str(reloc),'relocatable_sha256':sha(reloc),
 'layout':str(layout),'layout_sha256':sha(layout),'linker':ld,'linker_sha256':sha(ld),
 'undefined_symbols':[],
 'limits':['Source graph and relocations link at an experimental placement only.',
           'The text extent exceeds the official CASE payload; section order, native entry addresses, checksums and packaging are not stock-equal.',
           'No device, flash, peripheral timing or physical policy proof.']}
Path(str(output)+'.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'sha256':receipt['output_sha256'],'undefined_count':0},indent=2))
