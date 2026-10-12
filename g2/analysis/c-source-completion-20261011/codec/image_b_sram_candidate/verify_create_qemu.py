"""Finite GSC create original/source QEMU comparison with real fenv provider."""
from __future__ import annotations
import json
import os
from pathlib import Path
from verify_process_active_qemu import HERE, ROOT, QEMU, STOCK, BUILD, OUT, sha, rel, run, tool

def main()->None:
    receipt=json.loads(BUILD.read_text())
    archive=OUT/'source-trig-corrected.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(u['object'])) for u in receipt['units'])])
    detail_mode=os.environ.get('IMAGE_B_CREATE_DETAIL','')
    details=bool(detail_mode)
    cases={'create_positive':(['-DCREATE_KERNEL_DETAIL']+
            (['-DCREATE_KERNEL_ORDERED'] if detail_mode=='ordered' else []))
           if details else []}
    if not details:
        cases['create_single_mic_8khz']=['-DCREATE_VARIANT_SINGLE_MIC']
    observed={}
    for name,defines in cases.items():
        pair={}
        for mode in ('original','source'):
            elf=OUT/f'{name}-trig-{mode}.elf'
            ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
            args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float',
                  '-nostdlib','-nostartfiles',*defines,'-Wl,-T,'+ld,'-o',rel(elf),
                  'process_native_oracle_start.S','create_positive_oracle_main.c']
            if mode=='original': args+=['process_native_oracle_stock.S']
            else: args+=['-DSOURCE_MODE',
                    '-Wl,--defsym,gx8002_image_b_dsp_config_2002d7a4=0x2002d7a4',
                    rel(archive)]
            tool(args)
            q=run(['docker','run','--rm','--network=none','-v',f'{ROOT}:/repo',
                   '-w','/repo','opencfw/qemu-csky-builddeps:20261009t201800',
                   'sh','-lc',f'timeout 15s {rel(QEMU)} -M virt -m 1G '
                   f'-cpu ck804ef -nographic -monitor none -kernel {rel(elf)} '
                   '-d guest_errors -D /tmp/create-trig.log; '
                   'result=$?; cat /tmp/create-trig.log; exit $result'])
            lines=[x.strip() for x in (q.stdout+q.stderr).splitlines() if x.strip()]
            assert lines and lines[-1]=='csky_exit_write: exit(0)',(name,mode,lines)
            pair[mode]={'elf_sha256':sha(elf),'trace':lines}
        if not details:
            assert pair['original']['trace']==pair['source']['trace'],(name,pair)
        observed[name]=pair
    result={'result':('PASS' if pair['original']['trace']==pair['source']['trace']
                      else 'DIFFERENCE'),'stock_sha256':sha(STOCK),
            'source_receipt_sha256':sha(BUILD),'qemu_sha256':sha(QEMU),
            'cases':observed,
            'limit':'Finite positive path only. Native final temporary-allocation failure enters the diagnostic transport and timed out in an uninitialized QEMU peripheral state; host chunk fixture separately covers request/null/log behavior. Initial context allocation failure is a native fault, not asserted as a recoverable API return.'}
    receipt_name=('create-ordered-kernel-receipt.json' if detail_mode=='ordered'
                  else 'create-kernel-detail-receipt.json' if details
                  else 'create-trig-receipt.json')
    (OUT/receipt_name).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
