"""Compare all 4096 caller-output bytes for one active product DSP call."""
from __future__ import annotations
import json
from pathlib import Path
from verify_process_active_qemu import ROOT, QEMU, STOCK, BUILD, OUT, sha, rel, run, tool

MARKER=0x4f555450
LENGTH=4096

def one(mode:str,archive:Path)->tuple[Path,bytes]:
    elf=OUT/f'active-product-output-{mode}.elf'
    ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
    args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float',
          '-nostdlib','-nostartfiles','-DACTIVE_PRODUCT_ANGLES',
          '-DACTIVE_INPUT_DC','-DACTIVE_OVERLAP_HISTORY','-DACTIVE_HIGH_GAIN',
          '-DACTIVE_DUMP_OUTPUT_WORDS','-Wl,-T,'+ld,'-o',rel(elf),
          'process_native_oracle_start.S','process_active_oracle_main.c']
    if mode=='original':args+=['process_native_oracle_stock.S']
    else:args+=['-DSOURCE_MODE',
                '-Wl,--defsym,gx8002_image_b_dsp_config_2002d7a4=0x2002d7a4',
                rel(archive)]
    tool(args)
    q=run(['docker','run','--rm','--network=none','-v',f'{ROOT}:/repo',
           '-w','/repo','opencfw/qemu-csky-builddeps:20261009t201800',
           'sh','-lc',f'timeout 30s {rel(QEMU)} -M virt -m 1G '
           f'-cpu ck804ef -nographic -monitor none -kernel {rel(elf)} '
           '-d guest_errors -D /tmp/process-output.log; '
           'result=$?; cat /tmp/process-output.log; exit $result'])
    lines=[s.strip() for s in (q.stdout+q.stderr).splitlines() if s.strip()]
    assert lines and lines[-1]=='csky_exit_write: exit(0)',(mode,lines[-4:])
    values=[int(s[7:])&0xffffffff for s in lines if s.startswith('label: ')]
    start=values.index(MARKER)+1
    words=values[start:start+LENGTH//4]
    assert len(words)==LENGTH//4,(mode,len(words))
    data=b''.join(w.to_bytes(4,'little') for w in words)
    (OUT/f'active-product-output-{mode}.bin').write_bytes(data)
    return elf,data

def main()->None:
    receipt=json.loads(BUILD.read_text())
    assert receipt['source_complete'] is False
    archive=OUT/'source-process-output.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(u['object'])) for u in receipt['units'])])
    native_elf,native=one('original',archive)
    source_elf,source=one('source',archive)
    first=next((i for i,(x,y) in enumerate(zip(native,source)) if x!=y),None)
    result={'result':'PASS' if first is None else 'DIFFERENCE',
            'bytes_compared':LENGTH,'first_difference':first,
            'original_output_sha256':sha(OUT/'active-product-output-original.bin'),
            'source_output_sha256':sha(OUT/'active-product-output-source.bin'),
            'original_elf_sha256':sha(native_elf),
            'source_elf_sha256':sha(source_elf),
            'source_receipt_sha256':sha(BUILD),'stock_sha256':sha(STOCK),
            'qemu_sha256':sha(QEMU),
            'limit':'One nonzero active product call in QEMU; exact caller output only, not all internal state, arbitrary input, hardware FP, or final layout.'}
    (OUT/'active-product-output-byte-receipt.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert first is None,result

if __name__=='__main__':main()
