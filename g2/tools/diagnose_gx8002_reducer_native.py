# SPDX-License-Identifier: MIT
"""Compare native macOS compilation of pinned reducers with decoded C-SKY output."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha


def diagnose():
    upstream=ROOT/'build/upstream-newlib-math';receipt=json.loads((upstream/'receipt.json').read_text())
    out=ROOT/'build/gx8002-reducer-native';out.mkdir(exist_ok=True)
    for name,target in [('newlib_double_compat.h','newlib_double_compat.h'),('newlib_reduction_compat.h','fdlibm.h')]:
        data=(ROOT/'components/shared/gx8002'/name).read_bytes()
        if target=='fdlibm.h':data+=b'\ndouble copysign(double,double);\n'
        (out/target).write_bytes(data)
    sources=[];pins=[]
    for name in ('e_rem_pio2.c','k_rem_pio2.c','s_fabs.c','s_floor.c','s_scalbn.c','s_copysign.c'):
        row=next(r for r in receipt['files'] if r['path'].endswith('/'+name))
        data=(upstream/name).read_bytes();assert sha(data)==row['sha256']
        path=out/name;path.write_bytes(data);sources.append(str(path));pins.append(row)
    report_path=ROOT/'docs/research/gx8002-reducer-execution.json';report=json.loads(report_path.read_text())
    inputs=[int(r['input'],16) for r in report['cases']]
    driver=out/'driver.c';driver.write_text('#include <stdint.h>\n#include <stdio.h>\nextern int __ieee754_rem_pio2(double,double*);\nint main(void){ uint64_t inputs[]={'+','.join('UINT64_C(0x%x)'%x for x in inputs)+'}; for(unsigned i=0;i<sizeof(inputs)/sizeof(inputs[0]);i++){ union{double d;uint64_t u;}x={.u=inputs[i]},hi,lo;double y[2];int n=__ieee754_rem_pio2(x.d,y);hi.d=y[0];lo.d=y[1];printf("%016llx %016llx %d\\n",(unsigned long long)hi.u,(unsigned long long)lo.u,n); }return 0;}\n')
    exe=out/'native';command=['xcrun','clang','-std=c11','-O2','-ffreestanding','-fno-builtin','-fwrapv','-ffp-contract=off',*sources,str(driver),'-o',str(exe)]
    subprocess.run(command,check=True)
    output=subprocess.check_output([str(exe)],text=True);rows=[];differences=[]
    for old,line in zip(report['cases'],output.splitlines()):
        h,l,n=line.split();new={'input':old['input'],'high':hex(int(h,16)),'low':hex(int(l,16)),'quadrant_integer':int(n)}
        rows.append(new)
        if new!=old:differences.append({'csky':old,'native':new})
    assert len(rows)==len(inputs)
    result={'commit':receipt['commit'],'sources':pins,'compile_command':command,'driver_sha256':sha(driver.read_bytes()),'native_executable_sha256':sha(exe.read_bytes()),'execution_report_sha256':sha(report_path.read_bytes()),'cases':rows,'differences':differences,'source_admitted':False,'limits':['Same pinned algorithm and helper sources compiled for native macOS, separate hardware arithmetic from decoded C-SKY. Agreement diagnoses sampled behavior only; does not prove full-domain accuracy or firmware correctness.']}
    (ROOT/'docs/research/gx8002-reducer-native.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=diagnose();print(len(r['cases']),len(r['differences']),r['differences'][:2])
