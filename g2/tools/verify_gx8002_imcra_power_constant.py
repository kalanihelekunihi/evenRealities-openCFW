# SPDX-License-Identifier: MIT
"""Check existing source power implementation at the observed IMCRA arguments."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from gx8002_binary32_rational import operation,fused_operation
from verify_gx8002_powf_general import reference

def verify(cluster=False):
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    # Immediate load at 46d2a and literal at 47074, observed before 46d40 call.
    assert stock[0x47074:0x47078]==bytes.fromhex('9a9919bf')
    x,y=0x41200000,0xbf19999a
    path=ROOT/'build/gx8002-powf-placed/power.elf';report=json.loads((ROOT/'docs/research/gx8002-powf-placed.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    if cluster:path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x489fc','--stop-address=0x49c14',str(wrapper)],text=True));results=[]
    for name,arithmetic in [('separate_rounding',operation),('fused_rounding',fused_operation)]:
        args=[x,y]+[0x76540000+i for i in range(2,16)]
        actual=execute(code,0x100100a4 if cluster else 0x100100bc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        original=execute(old,0x489fc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        assert actual==original
        expected=reference(x,y);assert abs(actual-expected)<=1
        results.append({'accumulator_model':name,'result_bits':hex(actual),'reference_bits':hex(expected),'ulp_error':abs(actual-expected)})
    evidence={'cluster_wrapper_executed':cluster,'executed_elf_sha256':sha(path.read_bytes()),'power_elf_sha256':report['elf_sha256'],'stock_sha256':IMAGE_SHA,'input_bits':[hex(x),hex(y)],'results':results,'source_admitted':False,'limits':['One observed initializer call, using complete decoded source and stock power bodies. Tests both modeled accumulator policies; physical FPU behavior and complete initializer execution remain unqualified.']}
    (ROOT/('docs/research/gx8002-imcra-power-cluster.json' if cluster else 'docs/research/gx8002-imcra-power-constant.json')).write_text(json.dumps(evidence,indent=2)+'\n');return evidence
if __name__=='__main__':print(verify())
