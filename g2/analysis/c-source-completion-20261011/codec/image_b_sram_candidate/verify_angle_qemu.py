"""Finite native/source whole-call angle comparison; stock bytes only in oracle ELF."""
from __future__ import annotations
import json
import os
from pathlib import Path
from verify_process_active_qemu import HERE, ROOT, TOOL, QEMU, STOCK, BUILD, OUT, sha, rel, run, tool

def main()->None:
    receipt=json.loads(BUILD.read_text())
    archive=OUT/'source-trig-corrected.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(u['object'])) for u in receipt['units'])])
    cases={
        'angle_one':['-DANGLE_ONE'],
        'angle_three':['-DANGLE_THREE'],
        'angle_ready':['-DANGLE_ONE','-DANGLE_READY'],
        'angle_frame':['-DANGLE_ONE','-DANGLE_FRAME'],
        'geometry_one':['-DANGLE_ONE','-DANGLE_GEOMETRY'],
        'geometry_frame':['-DANGLE_ONE','-DANGLE_GEOMETRY','-DANGLE_FRAME'],
        'angle_product':['-DANGLE_PRODUCT'],
        'angle_product_geometry':['-DANGLE_PRODUCT_GEOMETRY'],
        'angle_product_three_mics':['-DANGLE_PRODUCT_THREE_MICS'],
        'angle_product_geometry_three_mics':['-DANGLE_PRODUCT_GEOMETRY_THREE_MICS'],
    }
    observed={}
    only=os.environ.get('ANGLE_ONLY')
    if only:
        cases={only:cases[only]}
    for name,defines in cases.items():
        pair={}
        for mode in ('original','source'):
            elf=OUT/f'{name}-trig-{mode}.elf'
            ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
            args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float',
                  '-nostdlib','-nostartfiles',*defines,'-Wl,-T,'+ld,'-o',rel(elf),
                  'process_native_oracle_start.S','angle_positive_oracle_main.c']
            if mode=='original': args+=['process_native_oracle_stock.S']
            else: args+=['-DSOURCE_MODE',
                    '-Wl,--defsym,gx8002_image_b_dsp_config_2002d7a4=0x2002d7a4',
                    rel(archive)]
            tool(args)
            q=run(['docker','run','--rm','--network=none','-v',f'{ROOT}:/repo',
                   '-w','/repo','opencfw/qemu-csky-builddeps:20261009t201800',
                   'sh','-lc',f'timeout 15s {rel(QEMU)} -M virt -m 1G '
                   f'-cpu ck804ef -nographic -monitor none -kernel {rel(elf)} '
                   '-d guest_errors -D /tmp/angle-trig.log; '
                   'result=$?; cat /tmp/angle-trig.log; exit $result'])
            lines=[x.strip() for x in (q.stdout+q.stderr).splitlines() if x.strip()]
            assert lines and lines[-1]=='csky_exit_write: exit(0)',(name,mode,lines)
            pair[mode]={'elf_sha256':sha(elf),'trace':lines}
        assert pair['original']['trace']==pair['source']['trace'],(name,pair)
        observed[name]=pair
    result={'result':'PASS','stock_sha256':sha(STOCK),
            'source_receipt_sha256':sha(BUILD),'qemu_sha256':sha(QEMU),
            'cases':observed,
            'limit':'Finite one-angle, three-angle, ready, one-frame, and two/three-microphone two-frame nonzero-phase fixtures; no arbitrary callback, hardware FP, initialized data, or layout equivalence proof.'}
    (OUT/'angle-trig-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
