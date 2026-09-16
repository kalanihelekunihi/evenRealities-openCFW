# SPDX-License-Identifier: MIT
"""Link reconstructed DRC constructor with pinned source log/exp dependencies."""
import json,re,subprocess
from build_gx8002_drc_stage1_initialize import build as stage_build,ROOT
from build_gx8002_log_exp_placed import build as math_build
from build_gx8002_backup_log_exp_wrappers import build as wrappers_build
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha

def build():
    evidence={'stage':stage_build(),'math':math_build(),'wrappers':wrappers_build()}
    stage=ROOT/'build/gx8002-drc-stage1-initialize';math=ROOT/'build/gx8002-log-exp-placed';wrappers=ROOT/'build/gx8002-backup-log-exp-wrappers'
    out=ROOT/'build/gx8002-drc-stage1-cluster';out.mkdir(exist_ok=True)
    script=(stage/'spectrums.ld').read_text().replace('*(',str(stage/'spectrums.o')+'(')
    for symbol in ('drc_logf','drc_expf'):script=re.sub(symbol+r' = 0x[0-9a-f]+;','',script)
    script+='drc_logf = open_cfw_gx8002_logf;\ndrc_expf = open_cfw_gx8002_expf;\n'
    wrapper_script=(wrappers/'wrapper.ld').read_text().replace('*(',str(wrappers/'wrapper.o')+'(')
    for symbol in ('__ieee754_logf','__ieee754_expf'):wrapper_script=re.sub(symbol+r' = 0x[0-9a-f]+;','',wrapper_script)
    script+=wrapper_script+(math/'math.ld').read_text()
    (out/'cluster.ld').write_text(script);target=out/'cluster.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(out/'cluster.ld'),str(stage/'spectrums.o'),str(wrappers/'wrapper.o'),str(ROOT/'build/gx8002-log-exp-probe/ef_log.c.o'),str(math/'exp.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),'cluster')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for original in (stage/'spectrums.elf',wrappers/'wrapper.elf',math/'math.elf'):
        component=Elf32(original.read_bytes(),'component')
        for sec in component.sections:
            if sec['flags']&2 and sec['size']:
                linked=next(s for s in elf.sections if s['name']==sec['name'])
                assert linked['address']==sec['address'] and elf.contents(linked)==component.contents(sec)
    for name in ('drc_logf','drc_expf','__ieee754_logf','__ieee754_expf'):
        assert next(s for s in elf.symbols() if s['name']==name)['section'] not in (0,0xfff1)
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'components':evidence,'elf_sha256':sha(target.read_bytes()),'source_admitted':False,'limits':['Source constructor and math wrappers/cores linked with exact component bytes and addresses.','Memset remains an address binding; startup integration and composed execution pending. No complete DRC or hardware qualification.']}
    (ROOT/'docs/research/gx8002-drc-stage1-cluster.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['elf_sha256'])
