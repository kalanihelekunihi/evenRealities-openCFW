# SPDX-License-Identifier: MIT
"""Apply reviewable Horner loops and compile source coefficients separately."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_trig_probe import build as probe
from verify_gx8002_analog_source import FLAGS


def build():
    prior=probe();out=ROOT/'build/gx8002-trig-loop-probe';out.mkdir(exist_ok=True)
    (out/'fdlibm.h').write_bytes((ROOT/'build/gx8002-trig-probe/fdlibm.h').read_bytes())
    rows=[];pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    for name in ('sin','cos'):
        source=out/('k_'+name+'.c')
        source.write_bytes((ROOT/'build/gx8002-trig-probe'/source.name).read_bytes())
        patch=ROOT/'components/shared/gx8002'/('newlib-kernel-'+name+'-loop.patch')
        subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=out,check=True)
        text=source.read_text();match=re.search(r'static const double coefficients\[\] = \{([^}]+)\};',text);assert match
        symbol='open_cfw_gx8002_'+name+'_coefficients'
        count=len(match[1].split(','))
        text=text[:match.start()]+f'extern const double coefficients[{count}];'+text[match.end():]
        text=text.replace('coefficients',symbol);source.write_text(text)
        constants=out/(name+'_coefficients.c')
        constants.write_text('/* Constants from the pinned Newlib kernel; original license in '+source.name+'. */\nconst double '+symbol+'[] = {'+match[1]+'};\n')
        for unit in (source,constants):
            obj=out/(unit.name+'.o');command=[pre+'gcc',*FLAGS,'-Os','-mno-high-registers','-fwrapv','-ffp-contract=off','-c',str(unit),'-o',str(obj)]
            subprocess.run(command,check=True);elf=Elf32(obj.read_bytes(),unit.name)
            rows.append({'source':unit.name,'source_sha256':sha(unit.read_bytes()),'patch_sha256':sha(patch.read_bytes()),'command':command,'object_sha256':sha(obj.read_bytes()),'allocated':[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']]})
    result={'upstream_probe':prior,'objects':rows,'source_admitted':False,'limits':['Complete source loops preserve coefficient order and multiply/add expression order. Separate source arrays prevent compiler constant expansion. Link, placement, numerical equivalence and hardware remain pending.']}
    (ROOT/'docs/research/gx8002-trig-loop-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['source'],r['allocated']) for r in build()['objects']])
