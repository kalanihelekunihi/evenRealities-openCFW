#!/usr/bin/env python3
"""Compose distinct CASE command and startup C objects without stock data."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
args=parser.parse_args();output=Path(args.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
command=output.with_name(output.stem+'.command.o');startup=output.with_name(output.stem+'.startup.o')
subprocess.run([sys.executable,str(HERE/'build_full_experiment.py'),'--output',str(command)],check=True,capture_output=True)
subprocess.run([sys.executable,str(HERE/'build_startup_candidate.py'),'--output',str(startup)],check=True,capture_output=True)
linker='/opt/homebrew/bin/arm-none-eabi-ld'
subprocess.run([linker,'-r',str(command),str(startup),'-o',str(output)],check=True)
nm=subprocess.run(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(output)],capture_output=True,text=True,check=True)
imports=sorted(line.split()[-1] for line in nm.stdout.splitlines() if line.strip())
receipt={'status':'relocatable_experiment_only','output':str(output),'sha256':sha(output),
         'command_sha256':sha(command),'startup_sha256':sha(startup),'linker_sha256':sha(Path(linker)),
         'undefined_symbols':imports,
         'limits':'Relocatable source graph only. Typed product CRT defaults reconstruct the 420-byte initialized RAM region, while whole-native-body coverage, stock layout and physical effects remain unproved.'}
Path(str(output)+'.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'output':str(output),'sha256':receipt['sha256'],'undefined_count':len(imports)},indent=2))
