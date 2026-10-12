"""Compare every native/source product angle-table byte, not just hashes."""
from __future__ import annotations
import json
from pathlib import Path
from verify_process_active_qemu import HERE, ROOT, TOOL, QEMU, STOCK, BUILD, OUT, sha, rel, run, tool

TABLE_BYTES=2*3*257*8
TABLE_WORDS=TABLE_BYTES//4
MARKER=0x54424c45

def build_and_run(mode:str,archive:Path)->tuple[Path,bytes]:
    elf=OUT/f'active-product-table-words-{mode}.elf'
    ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
    args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float',
          '-nostdlib','-nostartfiles','-DACTIVE_PRODUCT_ANGLES',
          '-DACTIVE_INPUT_DC','-DACTIVE_OVERLAP_HISTORY','-DACTIVE_HIGH_GAIN',
          '-DACTIVE_PRODUCT_TABLE_WORDS','-Wl,-T,'+ld,'-o',rel(elf),
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
           '-d guest_errors -D /tmp/process-table-words.log; '
           'result=$?; cat /tmp/process-table-words.log; exit $result'])
    lines=[x.strip() for x in (q.stdout+q.stderr).splitlines() if x.strip()]
    assert lines and lines[-1]=='csky_exit_write: exit(0)',(mode,lines[-4:])
    values=[int(line[7:]) & 0xffffffff for line in lines
            if line.startswith('label: ')]
    start=values.index(MARKER)+1
    words=values[start:start+TABLE_WORDS]
    assert len(words)==TABLE_WORDS,(mode,len(words))
    result=b''.join(word.to_bytes(4,'little') for word in words)
    path=OUT/f'active-product-table-{mode}.bin'
    path.write_bytes(result)
    return elf,result

def main()->None:
    receipt=json.loads(BUILD.read_text())
    assert receipt['source_complete'] is False
    archive=OUT/'source-table-words.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(unit['object'])) for unit in receipt['units'])])
    original_elf,original=build_and_run('original',archive)
    source_elf,source=build_and_run('source',archive)
    first_difference=next((i for i,(a,b) in enumerate(zip(original,source))
                           if a!=b),None)
    result={'result':'PASS' if first_difference is None else 'DIFFERENCE',
            'bytes_compared':len(original),'first_difference':first_difference,
            'original_table_sha256':sha(OUT/'active-product-table-original.bin'),
            'source_table_sha256':sha(OUT/'active-product-table-source.bin'),
            'original_elf_sha256':sha(original_elf),
            'source_elf_sha256':sha(source_elf),
            'source_receipt_sha256':sha(BUILD),'stock_sha256':sha(STOCK),
            'qemu_sha256':sha(QEMU),
            'limit':'One product initialized angle call in QEMU; full table bytes, not arbitrary input, hardware FP, failure transport, or loaded-image placement.'}
    (OUT/'active-product-table-byte-receipt.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert first_difference is None,result

if __name__=='__main__':main()
