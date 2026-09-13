# SPDX-License-Identifier: MIT
"""Compile upstream-derived exp; inventory unresolved dependencies, never hide them."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,FLAGS
from analyze_gx8002_backup_exp_provenance import analyze

def build():
    provenance=analyze()
    out=ROOT/'build/gx8002-backup-exp-probe';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_exp.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    path=out/'exp.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-ffp-contract=off','-c',str(source),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'exp probe')
    dependencies=sorted({s['name'] for s in elf.symbols() if s['name'] and s['section']==0})
    assert dependencies==sorted(['__adddf3','__divdf3','__fixdfsi','__floatsidf','__gtdf2','__ltdf2','__muldf3','__subdf3'])
    sections=[{'name':s['name'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
    (out/'exp.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-dr',str(path)],text=True))
    result={'provenance':provenance,'source_sha256':sha(source.read_bytes()),'object_sha256':sha(path.read_bytes()),'sections':sections,'unresolved_dependencies':dependencies,
            'source_admitted':False,'limits':['macOS compile-only probe. Not linked, not stock-equivalent, not a firmware replacement. Compiler binary64 arithmetic dependencies must be implemented from source and qualified; special paths follow observed stock call shapes.']}
    (ROOT/'docs/research/gx8002-backup-exp-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(build(),indent=2))
