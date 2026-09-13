# SPDX-License-Identifier: MIT
"""Measure source-authored exponential helper boundaries, never binary cuts."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32
from probe_gx8002_exp_size import probe

def run():
    evidence=probe();base=ROOT/'build/gx8002-exp-size-probe/signed-constants.c'
    text=base.read_text();assert sha(base.read_bytes())==evidence['variants'][-1]['source_sha256']
    out=ROOT/'build/gx8002-exp-helper-probe';out.mkdir(exist_ok=True)
    variants={
      'overflow':('''static __attribute__((noinline)) double exp_overflow(void)
{
    volatile double operand = 1.0e300;
    return operand * operand;
}
''','''\t\t\tvolatile double operand = hugeval;
\t\t\treturn operand * operand;''','\t\t\treturn exp_overflow();'),
      'tiny':('''static __attribute__((noinline)) double exp_tiny(double x)
{
    if (1.0e300 + x > 1.0) return 1.0 + x;
    return 1.0;
}
''','''\t\tif (hugeval + x > one)
\t\t\treturn one + x;\t\t\t\t/* trigger inexact */
\t\treturn one;''','\t\treturn exp_tiny(x);')}
    scale_start=text.index('\tGET_HIGH_WORD(hx, y);')
    scale_body=text[scale_start:text.rfind('}')]
    scale_helper='static __attribute__((noinline)) double exp_scale(double y, int32_t k)\n{\n    uint32_t hx;\n    const double twom1000 = 0x1p-1000;\n'+scale_body+'}\n'
    variants['scale']=(scale_helper,scale_body,'\treturn exp_scale(y, k);\n')
    variants['tiny_scale']=variants['scale']
    records=[]
    for name,(helper,old,new) in variants.items():
        assert text.count(old)==1
        changed=text.replace(old,new).replace('double open_cfw_gx8002_backup_exp(',helper+'\ndouble open_cfw_gx8002_backup_exp(',1)
        if name in ('scale','tiny_scale'):
            changed='\n'.join(line for line in changed.split('\n') if 'static const double twom1000' not in line)
        if name=='tiny_scale':
            h,o,n=variants['tiny'];assert changed.count(o)==1
            changed=changed.replace(o,n).replace('double open_cfw_gx8002_backup_exp(',h+'\ndouble open_cfw_gx8002_backup_exp(',1)
        source=out/(name+'.c');source.write_text(changed);obj=out/(name+'.o')
        cmd=[str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'),'-Os',*FLAGS[1:],'-ffp-contract=off','-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True)
        elf=Elf32(obj.read_bytes(),name);sections=[{'name':s['name'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
        records.append({'variant':name,'source_sha256':sha(source.read_bytes()),'object_sha256':sha(obj.read_bytes()),'sections':sections,'command':cmd})
    result={'variants':records,'source_admitted':False,'limits':['Compile-only complete C helper sections; execution and physical placement pending.']}
    (ROOT/'docs/research/gx8002-exp-helper-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(run())
