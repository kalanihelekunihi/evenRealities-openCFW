# SPDX-License-Identifier: MIT
"""Execute clock lookup decoded from the complete FFT/Q15 container experiment."""
import json, struct, subprocess
from compare_gx8002_backup_clock_lookup import execute
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode


def verify():
    out=ROOT/'build/gx8002-fft-q15-tail-integration-experiment'
    report_path=out/'build-report.json'; report=json.loads(report_path.read_text())
    path=out/'firmware_codec.unadmitted.bin'; image=path.read_bytes()
    assert sha(image)==report['firmware_sha256']
    stock=IMAGE.read_bytes(); assert sha(stock)==IMAGE_SHA
    body=next(r for r in report['ownership'] if r['offset']==0x3be20)
    assert body['kind']=='compiled_c' and body['size']==160
    assert sha(image[0x3be20:0x3bec0])==body['sha256']
    tail=next(r for r in report['ownership'] if r['offset']==0x3bec0)
    assert tail['kind']=='compiled_c' and tail['size']==20
    assert sha(image[0x3bec0:0x3bed4])==tail['sha256']
    table=next(r for r in report['ownership'] if r['offset']==0x4f2dc)
    assert table['kind']=='generated_source_data' and table['size']==416
    assert sha(image[0x4f2dc:0x4f47c])==table['sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    wrapper=out/'clock-container.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(path),str(wrapper)],check=True)
    wrapped=bytearray(wrapper.read_bytes()); struct.pack_into('<I',wrapped,36,0x21006009); wrapper.write_bytes(wrapped)
    elf=Elf32(wrapper.read_bytes(),'container')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==image
    code=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3be20','--stop-address=0x3bec0',str(wrapper)],text=True))
    original=[struct.unpack_from('<I',image,0x4f2dc+i*16)[0] for i in range(26)]
    variants=[original,list(range(26)),list(reversed(range(26))),[0xffffffff]*26]
    variants += [[m if i in (j,25) else 0xffffffff for i in range(26)] for m in range(26) for j in range(26)]
    cases=0
    for ids in variants:
        for module in [*range(28),0x7fffffff,0x80000000,0xffffffff]:
            for pointer in (0,0x1000):
                expected=[0xa5a5a5a5]*6; writes=[]; result=0xffffffff
                if pointer and module<26:
                    expected[0]=0; writes=[(pointer,0)]
                    index=module if ids[module]==module else next((i for i,v in enumerate(ids) if v==module),None)
                    if index is not None:
                        base=0xa0010000 if module<10 else 0xa0300000
                        expected=[0x2001699c+index*16,base,base+(0x8c if module<10 else 0x88),base+24,base+28,base+32]
                        writes += [(pointer+i*4,v) for i,v in enumerate(expected)]; result=0
                assert execute(code,0x3be20,module,pointer,ids)==(result,expected,writes)
                cases+=1
    result={'integration_report_sha256':sha(report_path.read_bytes()),'firmware_sha256':sha(image),
            'clock_body_sha256':body['sha256'],'adjacent_wrapper_sha256':tail['sha256'],
            'cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Clock instructions decoded from composed container; actual generated table IDs and adversarial table variants tested against independent result/write oracle.',
                      'Execution map excludes reused tail, so any attempted clock instruction fetch into that region fails. Finite cases do not prove global computed-reference closure.',
                      'Existing decoded instruction model, ordinary nonoverlapping RAM output, no concurrent mutation or hardware/timing qualification.']}
    (ROOT/'docs/research/gx8002-fft-q15-combined-clock.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
