#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Record compiler ABI and authenticated SDK stack definitions, not capacity proof."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha

def analyze():
    compiler=ROOT/'build/upstream-csky-toolchain-build/gcc/gcc/config/csky/csky.h'
    source=compiler.read_text()
    macro=source.split('#define CALL_REALLY_USED_REGISTERS',1)[1].split('}',1)[0].split('{',1)[1]
    macro=re.sub(r'/\*.*?\*/','',macro,flags=re.S)
    values=[int(x) for x in re.findall(r'\b[01]\b',macro)][:32]
    if len(values)!=32 or values[16:18]!=[0,0]:raise ValueError('GPR ABI changed')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';dependencies=[];texts={}
    for relative in ('arch/soc/grus/link.ld','arch/soc/grus/include/soc_config.h','arch/cpu/csky/ck804/start.S','configs/github_grus_gx8002b_dev_erji_english.config'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
        data=authenticated_blob(sdk/relative,blob);texts[relative]=data.decode()
        dependencies.append({'path':relative,'git_blob':blob,'sha256':sha(data)})
    if 'CONFIG_STAGE2_DRAM_BASE + CONFIG_STAGE2_DRAM_SIZE - 4' not in texts['arch/soc/grus/include/soc_config.h']:raise ValueError('stack-top expression changed')
    if 'CONFIG_MCU_MAIN_STACK_SIZE * 1024' not in texts['arch/soc/grus/link.ld']:raise ValueError('stack reservation changed')
    report={'compiler_header_sha256':sha(compiler.read_bytes()),'gpr_call_really_used':values,
            'callee_preserved_general_registers':[f'r{i}' for i in range(32) if not values[i]],
            'sdk_commit':SDK_COMMIT,'sdk_dependencies':dependencies,
            'sdk_stack_top':'CONFIG_STAGE2_DRAM_BASE + CONFIG_STAGE2_DRAM_SIZE - 4',
            'sdk_linker_reservation':'CONFIG_MCU_MAIN_STACK_SIZE * 1024 after BSS',
            'source_admitted':False,'limits':['Compiler metadata establishes local compiler register convention, not compliance of arbitrary retained assembly handlers.',
              'r16/r17 corruption in the existing stress model is deliberately stronger than the C ABI requires. Extra saves may be conservative rather than mandatory.',
              'SDK example configuration is not the shipped G2 configuration. BSS-to-SP distance is not evidence of callback stack budget, mainline usage, nesting depth or complete physical allocation.']}
    (ROOT/'docs/research/gx8002-irq-stack-contract.json').write_text(json.dumps(report,indent=2)+'\n');print(report['callee_preserved_general_registers']);return report
if __name__=='__main__':analyze()
