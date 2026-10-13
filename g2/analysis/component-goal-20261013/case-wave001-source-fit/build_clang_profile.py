#!/usr/bin/env python3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'clang-profile');args=parser.parse_args();OUT=args.output.resolve();OUT.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=ROOT/'g2/analysis/component-goal-20261013/case-wave002-call-contracts/command-evidence/receipt.json';sel=json.loads(manifest.read_text());sources=[ROOT/x['source'] for x in sel['sources']]+sorted((ROOT/'g2/components/case/startup_candidate_20261011').glob('*.c'))+[HERE/'compiler_memory.c']
for x in sel['sources']:assert sha(ROOT/x['source'])==x['sha256']
def compile_one(item):
 i,p=item;o=OUT/(f'{i:03d}-'+p.stem+'.o');dep=o.with_suffix('.d');before=sha(p);opt='Os' if p.name in ['application_policy_idle_candidate.c','application_policy_no_reply_candidate.c'] else 'Oz';cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-mfloat-abi=soft','-std=c11','-'+opt,'-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-MD','-MF',str(dep),'-c',str(p),'-o',str(o)];run=subprocess.run(cmd,capture_output=True,text=True);assert sha(p)==before;assert run.returncode==0,run.stderr
 deps=dep.read_text().replace('\\\n',' ').split(':',1)[1].split();return {'source':str(p.relative_to(ROOT)),'sha256':before,'command':cmd,'object':str(o.relative_to(ROOT)),'object_sha256':sha(o),'dependencies':{str(Path(x).relative_to(ROOT)):sha(Path(x)) for x in deps if Path(x).is_relative_to(ROOT)},'diagnostics':run.stdout+run.stderr}
with ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(compile_one,enumerate(sources)))
b=json.loads((HERE/'build-receipt.json').read_text());force=[x for x in b['roots'] if x!='case_early_hook_84ae']+['case_vformat','case_crt_init_known_defaults'];elf=OUT/'case.elf';cmd=['arm-none-eabi-ld','-T',str(HERE/'layout.ld'),'--gc-sections',*['-u'+x for x in force],*map(lambda x:str(ROOT/x['object']),rows),'-o',str(elf)];run=subprocess.run(cmd,capture_output=True,text=True);(OUT/'link.log').write_text(run.stdout+run.stderr)
r={'status':'MATCHED_CURRENT_CLANG_SOURCE_PROFILE_LINKED' if run.returncode==0 else 'MATCHED_CURRENT_CLANG_PROFILE_FAILED','returncode':run.returncode,'sources':rows,'link_command':cmd,'compiler_sha256':sha(Path('/usr/bin/clang')),'limits':['Diagnostic source-size profile; full native behavior/placement/hardware gates remain open.','Two previously documented divmod-introducing units retained at Os.']}
if run.returncode==0:r['elf_sha256']=sha(elf)
(OUT/'build-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status']);print(run.stderr[-1500:])
