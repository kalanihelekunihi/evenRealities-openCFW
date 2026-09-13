# SPDX-License-Identifier: MIT
"""Measure whole-source exponential variants; no binary splitting or fast math."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,FLAGS

def probe():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_exp.c'
    out=ROOT/'build/gx8002-exp-size-probe';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    variants=[[],['-fno-caller-saves'],['-fno-tree-loop-optimize'],['-fno-if-conversion'],['-fno-if-conversion2'],['-finline-small-functions'],['-fno-schedule-insns'],['-fno-schedule-insns2'],['-O2']]
    rows=[]
    for i,flags in enumerate(variants):
        obj=out/(str(i)+'.o');cmd=[pre+'gcc','-Os',*FLAGS[1:],'-ffp-contract=off',*flags,'-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True)
        elf=Elf32(obj.read_bytes(),'exp');sections=[{'name':s['name'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
        rows.append({'flags':flags,'sections':sections,'total_bytes':sum(s['bytes'] for s in sections),'object_sha256':sha(obj.read_bytes()),'command':cmd})
    text=source.read_text()
    helper="""static inline double exp_signed_constant(double value, uint32_t sign)
{
    union { double d; uint64_t u; } bits = { .d = value };
    bits.u |= (uint64_t)sign << 63;
    return bits.d;
}

"""
    text=text.replace('double open_cfw_gx8002_backup_exp(',helper+'double open_cfw_gx8002_backup_exp(',1)
    for old,new in [('ln2HI[xsb]','exp_signed_constant(ln2HI[0], xsb)'),('ln2LO[xsb]','exp_signed_constant(ln2LO[0], xsb)'),('halF[xsb]','exp_signed_constant(0.5, xsb)')]:
        assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace('\tstatic const double halF[2] = { 0.5, -0.5 };\n','')
    variant=out/'signed-constants.c';variant.write_text(text)
    obj=out/'signed-constants.o';cmd=[pre+'gcc','-Os',*FLAGS[1:],'-ffp-contract=off','-c',str(variant),'-o',str(obj)]
    subprocess.run(cmd,check=True)
    elf=Elf32(obj.read_bytes(),'signed constants');sections=[{'name':s['name'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
    rows.append({'source_variant':'signed constants','source_sha256':sha(variant.read_bytes()),'flags':[],'sections':sections,'total_bytes':sum(s['bytes'] for s in sections),'object_sha256':sha(obj.read_bytes()),'command':cmd})
    result={'source_sha256':sha(source.read_bytes()),'variants':rows,'stock_envelope':712,'source_admitted':False,'limits':['Compile-only size measurements. No fast-math options. Changed objects need linking and target validation before use.']}
    (ROOT/'docs/research/gx8002-exp-size-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['flags'],r['total_bytes']) for r in probe()['variants']])
