#!/usr/bin/env python3
"""Build the distinct CASE startup/vector C object without stock data."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[4]
SOURCES=sorted((ROOT/'g2/components/case/startup_candidate_20261011').glob('*.c'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
parser.add_argument('--opt',choices=('Os','Oz','Oz-except-divmod'),default='Os',help='target size optimization level')
args=parser.parse_args();output=Path(args.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
flags=['--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb',
       '-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections',
       '-Wall','-Wextra','-Werror']
with tempfile.TemporaryDirectory() as directory:
    objects=[]
    for source in SOURCES:
        target=Path(directory)/(source.stem+'.o')
        selected_opt = 'Os' if args.opt == 'Oz-except-divmod' and source.name in {
            'application_policy_idle_candidate.c',
            'application_policy_no_reply_candidate.c',
        } else ('Oz' if args.opt == 'Oz-except-divmod' else args.opt)
        subprocess.run(['/usr/bin/clang',*flags,'-'+selected_opt,'-c',str(source),'-o',str(target)],check=True)
        objects.append(target)
    subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-r',*[str(x) for x in objects],'-o',str(output)],check=True)
nm=subprocess.run(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(output)],capture_output=True,text=True,check=True)
imports=sorted(line.split()[-1] for line in nm.stdout.splitlines() if line.strip())
receipt={'status':'compiled_relocatable_only','sources':[{'path':str(x.relative_to(ROOT)),'sha256':sha(x)} for x in SOURCES],
         'compiler':'/usr/bin/clang',
         'compiler_sha256':sha(Path('/usr/bin/clang')),'flags':flags,'opt_selection':args.opt,
         'output':str(output),'output_sha256':sha(output),
         'undefined_symbols':imports,
         'limits':'Separate startup source candidate. Typed CRT initializer fields reconstruct the 420-byte initialized RAM region; source placement, whole-body coverage and physical behavior remain unproved.'}
Path(str(output)+'.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'output':str(output),'sha256':receipt['output_sha256'],'undefined_count':len(imports)},indent=2))
