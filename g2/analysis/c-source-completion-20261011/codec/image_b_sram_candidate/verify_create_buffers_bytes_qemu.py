"""Compare the three full positive-create buffers byte for byte in QEMU."""
from __future__ import annotations
import json
from pathlib import Path
from verify_process_active_qemu import ROOT, QEMU, STOCK, BUILD, OUT, sha, rel, run, tool

BUFFERS=(('forward',0x46574430,2048),
         ('inverse',0x494e5630,3072),
         ('steering',0x53545230,3*257*4))

def one(mode:str,archive:Path)->tuple[Path,dict[str,bytes]]:
    elf=OUT/f'create-buffers-{mode}.elf'
    ld='process_native_oracle.ld' if mode=='original' else 'process_source_oracle.ld'
    args=['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float',
          '-nostdlib','-nostartfiles','-DCREATE_DUMP_BUFFERS',
          '-Wl,-T,'+ld,'-o',rel(elf),
          'process_native_oracle_start.S','create_positive_oracle_main.c']
    if mode=='original':args+=['process_native_oracle_stock.S']
    else:args+=['-DSOURCE_MODE',
                '-Wl,--defsym,gx8002_image_b_dsp_config_2002d7a4=0x2002d7a4',
                rel(archive)]
    tool(args)
    q=run(['docker','run','--rm','--network=none','-v',f'{ROOT}:/repo',
           '-w','/repo','opencfw/qemu-csky-builddeps:20261009t201800',
           'sh','-lc',f'timeout 30s {rel(QEMU)} -M virt -m 1G '
           f'-cpu ck804ef -nographic -monitor none -kernel {rel(elf)} '
           '-d guest_errors -D /tmp/create-buffers.log; '
           'result=$?; cat /tmp/create-buffers.log; exit $result'])
    lines=[s.strip() for s in (q.stdout+q.stderr).splitlines() if s.strip()]
    assert lines and lines[-1]=='csky_exit_write: exit(0)',(mode,lines[-4:])
    words=[int(s[7:])&0xffffffff for s in lines if s.startswith('label: ')]
    result={}
    cursor=0
    for name,marker,size in BUFFERS:
        cursor=words.index(marker,cursor)+1
        section=words[cursor:cursor+size//4]
        assert len(section)==size//4,(mode,name,len(section))
        data=b''.join(w.to_bytes(4,'little') for w in section)
        path=OUT/f'create-{name}-{mode}.bin'
        path.write_bytes(data)
        result[name]=data
        cursor+=size//4
    return elf,result

def main()->None:
    receipt=json.loads(BUILD.read_text())
    assert receipt['source_complete'] is False
    archive=OUT/'source-create-buffers.a'
    tool(['/tool/bin/csky-abiv2-elf-ar','rcs',rel(archive),
          *(rel(Path(u['object'])) for u in receipt['units'])])
    original_elf,original=one('original',archive)
    source_elf,source=one('source',archive)
    evidence={}
    for name,_,size in BUFFERS:
        a,b=original[name],source[name]
        first=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)
        evidence[name]={'bytes_compared':size,'first_difference':first,
                        'original_sha256':sha(OUT/f'create-{name}-original.bin'),
                        'source_sha256':sha(OUT/f'create-{name}-source.bin')}
    passed=all(v['first_difference'] is None for v in evidence.values())
    result={'result':'PASS' if passed else 'DIFFERENCE','buffers':evidence,
            'original_elf_sha256':sha(original_elf),
            'source_elf_sha256':sha(source_elf),
            'source_receipt_sha256':sha(BUILD),'stock_sha256':sha(STOCK),
            'qemu_sha256':sha(QEMU),
            'limit':'One positive GSC create call in QEMU. Three full buffers only; no failure transport, arbitrary input, hardware FP, or final layout proof.'}
    (OUT/'create-buffer-byte-receipt.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert passed,result

if __name__=='__main__':main()
