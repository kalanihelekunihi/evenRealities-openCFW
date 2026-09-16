# SPDX-License-Identifier: MIT
"""Expose the preserved-layout entry as the public source dispatcher symbol."""
import json,subprocess
from build_gx8002_backup_platform_config_preserved import build as preserved,ROOT,Elf32,sha

def build():
    evidence=preserved();original=ROOT/'build/gx8002-backup-platform-config';out=ROOT/'build/gx8002-backup-platform-config-cluster';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    for name in ('config','entry'):
        subprocess.run([pre+'objcopy','--redefine-sym','open_cfw_gx8002_platform_config=open_cfw_gx8002_platform_config_body',str(original/(name+'.o')),str(out/(name+'.o'))],check=True)
    script=(original/'preserved.ld').read_text()+'\nopen_cfw_gx8002_platform_config = open_cfw_gx8002_platform_config_entry;\n'
    (out/'config.ld').write_text(script);path=out/'config.elf';subprocess.run([pre+'ld','-T',str(out/'config.ld'),str(out/'config.o'),str(out/'entry.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'public entry');old=Elf32((original/'preserved.elf').read_bytes(),'preserved')
    for sec in old.sections:
        if not sec['flags']&2 or not sec['size']:continue
        new=next(s for s in elf.sections if s['name']==sec['name']);assert new['address']==sec['address'] and elf.contents(new)==old.contents(sec)
    public=next(s for s in elf.symbols() if s['name']=='open_cfw_gx8002_platform_config');assert public['value']==0x1001574c and public['section'] not in (0,0xfff1)
    report={'preserved':evidence,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Public entry/body symbol split only; bytes unchanged from verified preserved layout. Shared literal gap is not supplied by this component or claimed as source.']}
    (ROOT/'docs/research/gx8002-backup-platform-config-cluster.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
