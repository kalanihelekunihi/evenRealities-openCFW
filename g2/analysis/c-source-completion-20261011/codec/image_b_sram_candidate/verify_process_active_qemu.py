"""Bounded stock/source image-B process calls after authenticated CRT data copy.

The stock byte image is linked only into the original test ELF. The source
test ELF uses the selected 226 C units. Neither ELF is a firmware image.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
TOOL=ROOT/'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
QEMU=ROOT/'g2/build/offline-xuantie-csky-dsp-20261009T201800Z/qemu-system-cskyv2'
STOCK=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
BUILD=HERE/os.environ.get('IMAGE_B_BUILD_RECEIPT',
    'build-angle-geometry-orientation-round/receipt.json')
OUT=HERE/'native-oracle-run'

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p:Path)->str: return '/repo/'+str(p.relative_to(ROOT))
def run(cmd:list[str])->subprocess.CompletedProcess[str]:
    p=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
    if p.returncode:
        raise RuntimeError(f'{cmd}: exit {p.returncode}\n{p.stdout}\n{p.stderr}')
    return p
def tool(args:list[str])->None:
    run(['docker','run','--rm','--network=none','--platform','linux/amd64',
         '-v',f'{ROOT}:/repo','-v',f'{TOOL}:/tool:ro',
         '-w',rel(HERE),'opencfw/iar-base:10.10.2-local',*args])

def main()->None:
    receipt=json.loads(BUILD.read_text())
    assert receipt['source_complete'] is False
    assert receipt['image_sha256']==sha(STOCK)
    assert len(receipt['units'])>=226
    archive=OUT/'source-fenv.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(u['object'])) for u in receipt['units'])])
    cases={'active_zero':[], 'active_short':['-DSHORT_ACTIVE_BAND'],
           'active_impulse':['-DACTIVE_INPUT_IMPULSE'],
           'active_dc':['-DACTIVE_INPUT_DC'],
           'active_history':['-DACTIVE_OVERLAP_HISTORY'],
           'active_history_gain':['-DACTIVE_OVERLAP_HISTORY','-DACTIVE_HIGH_GAIN']}
    cases['active_repeat']=['-DACTIVE_OVERLAP_HISTORY','-DACTIVE_HIGH_GAIN',
                            '-DACTIVE_INPUT_DC','-DACTIVE_REPEAT']
    cases['active_product']=['-DACTIVE_PRODUCT_ANGLES','-DACTIVE_INPUT_DC',
                             '-DACTIVE_OVERLAP_HISTORY','-DACTIVE_HIGH_GAIN']
    cases['active_product_slices']=cases['active_product']+[
        '-DACTIVE_PRODUCT_TABLE_SLICES']
    cases['active_product_existing_state']=cases['active_product']+[
        '-DACTIVE_INITIAL_STATE']
    if os.environ.get('IMAGE_B_CASE'):
        key=os.environ['IMAGE_B_CASE']
        cases={key:cases[key]}
    observations={}
    for name,defines in cases.items():
        traces={}
        for mode in ('original','source'):
            elf=OUT/f'{name}-{mode}.elf'
            ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
            args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef',
                  '-mhard-float','-nostdlib','-nostartfiles',*defines,
                  '-Wl,-T,'+ld,'-o',rel(elf),
                  'process_native_oracle_start.S','process_active_oracle_main.c']
            if mode=='original': args+=['process_native_oracle_stock.S']
            else:
                args+=['-DSOURCE_MODE',
                       '-Wl,--defsym,gx8002_image_b_dsp_config_2002d7a4=0x2002d7a4',
                       rel(archive)]
                if os.environ.get('IMAGE_B_BOUND_PROCESS')=='1':
                    args+=['-DSOURCE_BOUND_CORE',
                           '-Wl,--defsym,gx8002_image_b_process_energy_first_use_2002d79c=0x2002d79c',
                           '-Wl,--defsym,gx8002_image_b_process_ring_counter_2002d7a0=0x2002d7a0']
            tool(args)
            q=run(['docker','run','--rm','--network=none','-v',f'{ROOT}:/repo',
                   '-w','/repo','opencfw/qemu-csky-builddeps:20261009t201800',
                   'sh','-lc',f'timeout 15s {rel(QEMU)} -M virt -m 1G '
                   f'-cpu ck804ef -nographic -monitor none -kernel {rel(elf)} '
                   '-d guest_errors -D /tmp/process-active.log; '
                   'result=$?; cat /tmp/process-active.log; exit $result'])
            lines=[x.strip() for x in (q.stdout+q.stderr).splitlines() if x.strip()]
            assert lines and lines[-1]=='csky_exit_write: exit(0)',lines
            traces[mode]={'elf_sha256':sha(elf),'trace':lines}
        if os.environ.get('IMAGE_B_TRACE_DIAGNOSTIC')!='1':
            assert traces['original']['trace']==traces['source']['trace'],(name,traces)
        observations[name]=traces
    all_equal=all(v['original']['trace']==v['source']['trace']
                  for v in observations.values())
    result={'result':'PASS' if all_equal else 'DIFFERENCE','stock_sha256':sha(STOCK),
            'source_receipt_sha256':sha(BUILD),'qemu_sha256':sha(QEMU),
            'cases':observations,
            'limit':'Finite initialized-data QEMU paths only; output is zero in these fixtures. No complete numerical, FP hardware, failure-branch, ABI, data-placement, or image equivalence proof.'}
    out_name='active-bound-core-receipt.json' if os.environ.get(
        'IMAGE_B_BOUND_PROCESS')=='1' else 'active-diagnostic-receipt.json' if os.environ.get(
        'IMAGE_B_TRACE_DIAGNOSTIC')=='1' else 'active-receipt.json'
    (OUT/out_name).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
