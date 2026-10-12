"""Finite native-vs-selected-runtime binary64 helper calls in CK804EF QEMU."""
from __future__ import annotations
import json
from pathlib import Path
from verify_process_active_qemu import HERE, ROOT, QEMU, STOCK, BUILD, OUT, sha, rel, run, tool

def main()->None:
    receipt=json.loads(BUILD.read_text())
    archive=OUT/'source-trig-corrected.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(u['object'])) for u in receipt['units'])])
    pair={}
    for mode in ('original','source'):
        elf=OUT/f'kernel-arithmetic-{mode}.elf'
        ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
        args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float',
              '-nostdlib','-nostartfiles','-Wl,-T,'+ld,'-o',rel(elf),
              'process_native_oracle_start.S','kernel_arithmetic_oracle_main.c']
        if mode=='original': args+=['process_native_oracle_stock.S']
        else: args+=['-DSOURCE_MODE',rel(archive)]
        tool(args)
        q=run(['docker','run','--rm','--network=none','-v',f'{ROOT}:/repo',
               '-w','/repo','opencfw/qemu-csky-builddeps:20261009t201800',
               'sh','-lc',f'timeout 15s {rel(QEMU)} -M virt -m 1G '
               f'-cpu ck804ef -nographic -monitor none -kernel {rel(elf)} '
               '-d guest_errors -D /tmp/kernel-arithmetic.log; '
               'result=$?; cat /tmp/kernel-arithmetic.log; exit $result'])
        lines=[x.strip() for x in (q.stdout+q.stderr).splitlines() if x.strip()]
        assert lines and lines[-1]=='csky_exit_write: exit(0)',lines
        pair[mode]={'elf_sha256':sha(elf),'trace':lines}
    result={'result':'PASS' if pair['original']['trace']==pair['source']['trace'] else 'DIFFERENCE',
            'stock_sha256':sha(STOCK),'source_receipt_sha256':sha(BUILD),
            'qemu_sha256':sha(QEMU),'pair':pair,
            'limit':'Finite explicit binary64 helper operands only, not whole kernel or hardware FP equivalence.'}
    (OUT/'kernel-arithmetic-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
