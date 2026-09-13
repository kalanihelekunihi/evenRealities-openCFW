# SPDX-License-Identifier: MIT
"""Independent LTO link probe using the source FFT manifest."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha

def probe():
    base=ROOT/'build/gx8002-source-rfft-double-shared-cluster';out=ROOT/'build/gx8002-fft-lto-probe';out.mkdir(exist_ok=True)
    manifest=json.loads((ROOT/'docs/research/gx8002-source-rfft-double-shared-cluster.json').read_text());pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');objects=[]
    for row in manifest['sources']:
        source=ROOT/row['source'];assert sha(source.read_bytes())==row['sha256']
        obj=out/(row['name']+'.o');objects.append(str(obj))
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*row['extra_flags'],'-flto','-I',str(base),'-c',str(source),'-o',str(obj)],check=True)
    path=out/'cluster.elf'
    result=subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-flto','-nostdlib','-Wl,--gc-sections','-Wl,-T,'+str(base/'cluster.ld'),*objects,'-o',str(path)],capture_output=True,text=True)
    report={'source_manifest_sha256':sha((ROOT/'docs/research/gx8002-source-rfft-double-shared-cluster.json').read_bytes()),'exit_code':result.returncode,'diagnostics':result.stderr,'source_admitted':False}
    if result.returncode==0:
        e=Elf32(path.read_bytes(),'LTO probe');report['sections']=[{'name':s['name'],'bytes':s['size']} for s in e.sections if s['flags']&2 and s['size']]
        report['elf_sha256']=sha(path.read_bytes());report['undefined_symbols']=[s['name'] for s in e.symbols() if s['name'] and s['section']==0]
        (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report['limits']=['LTO build/size probe only; symbol preservation, linked execution and firmware placement not qualified.']
    (ROOT/'docs/research/gx8002-fft-lto-probe.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(probe(),indent=2))
