# SPDX-License-Identifier: MIT
"""Bind observed Q15 callers and preserved entries to the composed container."""
import json, subprocess
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode


def verify():
    from analyze_gx8002_shift_q15_references import analyze as shift
    from analyze_gx8002_maxabs_q15_references import analyze as maxabs
    from analyze_gx8002_copy_q15_references import analyze as copy
    from analyze_gx8002_fill_q15_references import analyze as fill
    refs={name:fn() for name,fn in [('shift',shift),('maxabs',maxabs),('copy',copy),('fill',fill)]}
    out=ROOT/'build/gx8002-fft-q15-tail-integration-experiment'
    report_path=out/'build-report.json'; report=json.loads(report_path.read_text())
    image=(out/'firmware_codec.unadmitted.bin').read_bytes(); assert sha(image)==report['firmware_sha256']
    stock=IMAGE.read_bytes(); assert sha(stock)==IMAGE_SHA
    wrapper=out/'clock-container.elf'; elf=Elf32(wrapper.read_bytes(),'container')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==image
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True))
    checked=[]
    for name,evidence in refs.items():
        start,end=evidence['stock_range']
        assert not evidence['external_literal_pools'] and not evidence['stored_address_words']
        for branch in evidence['external_branches']:
            pc=branch['pc']; assert branch['entry'] and branch['target']==start
            op,args,width=code[pc]
            assert op=='bsr' and int(args,0)==start
            assert image[pc:pc+width]==stock[pc:pc+width]
            checked.append({'function':name,'pc':pc,'entry':start,'width':width})
        owner=next(r for r in report['ownership'] if r['offset']==start)
        assert owner['kind']==('compiled_assembly' if name=='copy' else 'compiled_c')
    op,args,width=code[0x47ac0]
    assert op=='br' and width==4
    target=int(args,0)
    owner=next(r for r in report['ownership'] if r['offset']==target)
    assert owner['kind']=='compiled_c'
    result={'integration_report_sha256':sha(report_path.read_bytes()),'firmware_sha256':sha(image),
            'callers':checked,'copy_body_offset':target,'source_admitted':False,'hardware_qualified':False,
            'limits':['All direct callers found by bounded stock Q15 reference scans retain their exact branch bytes and target source entries in the composed container.',
                      'Computed references and other address mappings remain outside this census; this does not prove global control-flow closure.']}
    (ROOT/'docs/research/gx8002-q15-integration-entries.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
