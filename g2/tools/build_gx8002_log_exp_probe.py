# SPDX-License-Identifier: MIT
"""Compile pinned Newlib log/exp with binary32 compatibility constants."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha
from verify_gx8002_analog_source import FLAGS

def build():
    upstream=ROOT/'build/upstream-newlib-math';receipt=json.loads((upstream/'receipt.json').read_text())
    assert receipt['commit']=='4aa696c8d6294897411cf78cae87f7f4680e9687'
    out=ROOT/'build/gx8002-log-exp-probe';out.mkdir(exist_ok=True)
    header=(ROOT/'components/shared/gx8002/newlib_math_compat.h').read_text()
    # IEEE infinity and gradual-underflow branches of pinned fdlibm.h.
    header+='\n#define FLT_UWORD_LOG_MAX 0x42b17217\n#define FLT_UWORD_LOG_MIN 0x42cff1b5\n'
    (out/'fdlibm.h').write_text(header)
    rows=[];pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    for name in ('ef_log.c','ef_exp.c'):
        data=(upstream/name).read_bytes();pin=next(r for r in receipt['files'] if r['path'].endswith('/'+name));assert sha(data)==pin['sha256']
        source=out/name;source.write_bytes(data);obj=out/(name+'.o')
        command=[pre+'gcc',*FLAGS,'-fwrapv','-ffp-contract=off','-c',str(source),'-o',str(obj)]
        subprocess.run(command,check=True)
        rows.append({'source':pin,'command':command,'object_sha256':sha(obj.read_bytes())})
    result={'commit':receipt['commit'],'header_sha256':sha(header.encode()),'objects':rows,'source_admitted':False,'limits':['Complete upstream compilation only. Linking, provenance comparison with stock, numerical verification and integration pending.']}
    (ROOT/'docs/research/gx8002-log-exp-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
