# SPDX-License-Identifier: MIT
"""Run Q15 public entries from the combined LTO artifact against stock."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,Elf32,sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_fill_q15_decoded import execute as fill
from verify_gx8002_backup_copy_q15_decoded import execute as copy
from verify_gx8002_backup_maxabs_q15_decoded import execute as maxabs
from verify_gx8002_shift_buffer_decoded import execute as shift

def verify(tail_layout=False):
    report_path=ROOT/'docs/research/gx8002-fft-q15-cluster-lto-probe.json';report=json.loads(report_path.read_text())
    selected=next(r for r in report['variants'] if r['lto'])
    for source in selected['sources']:assert sha((ROOT/source['source']).read_bytes())==source['sha256']
    path=ROOT/'build/gx8002-fft-q15-cluster-lto-probe/cluster-1.elf';assert sha(path.read_bytes())==selected['elf_sha256']
    if tail_layout:
        from build_gx8002_fft_q15_tail_layout import build
        layout=build();report_path=ROOT/'docs/research/gx8002-fft-q15-tail-layout.json'
        path=ROOT/'build/gx8002-fft-q15-tail-layout/component.elf'
        selected={'elf_sha256':layout['elf_sha256']}
        assert sha(path.read_bytes())==selected['elf_sha256']
    elf=Elf32(path.read_bytes(),'combined');symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    compiled=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
    assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47a00','--stop-address=0x47b14',str(wrapper)],text=True))
    entries={n:symbols['open_cfw_gx8002_backup_'+n+'_q15'] for n in ('shift','maxabs','copy','fill')};cases=dict.fromkeys(entries,0)
    if tail_layout:entries['copy']=symbols['source_copy_entry']
    for count in range(33):
        for value in (0,1,0x7fff,0x8000,0xffff,0x12345678,0x80000000,0xffffffff):
            assert fill(original,0x47aec,value,count)==fill(compiled,entries['fill'],value,count);cases['fill']+=1
        for delta in (-16,-8,-4,0,4,8,16,256):
            assert copy(original,0x47ac0,count,delta)==copy(compiled,entries['copy'],count,delta);cases['copy']+=1
            for amount in (-0x80000000,-33,-32,-16,-1,0,1,15,16,31):
                values=bytes((i*73+19)&255 for i in range(512))
                assert shift(original,0x47a00,values,amount,count,delta)==shift(compiled,entries['shift'],values,amount,count,delta);cases['shift']+=1
        values=[((i*1937)&65535)-32768 for i in range(count)]
        for alias in ([None,0,count-1] if count else [None]):
            assert maxabs(original,0x47a74,values,alias)==maxabs(compiled,entries['maxabs'],values,alias);cases['maxabs']+=1
    result={'tail_layout':tail_layout,'public_entries':entries,'probe_report_sha256':sha(report_path.read_bytes()),'elf_sha256':selected['elf_sha256'],'stock_sha256':IMAGE_SHA,'cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Bounded direct stock comparisons using actual combined LTO public entries. Fill/copy/shift compare ordered memory traces, maxabs compares final memory and input-read/output-write ordering.','Physical placement, full domains, bus atomicity and extreme positive-zero shifts remain unqualified.']}
    (ROOT/('docs/research/gx8002-q15-tail-layout-verification.json' if tail_layout else 'docs/research/gx8002-q15-combined-lto-verification.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['cases'])
