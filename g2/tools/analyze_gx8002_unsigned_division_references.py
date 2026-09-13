# SPDX-License-Identifier: MIT
"""Classify raw division census findings without hiding mixed-data artifacts."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode

def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    quotient=analyze(0x49ddc,0x4a110,require_entry_only=False)
    remainder=analyze(0x4a110,0x4a434,require_entry_only=False)
    assert [r for r in quotient['external_branches'] if not r['entry']]==[{'pc':0x49bd2,'target':0x49f16,'entry':False}]
    assert len([r for r in quotient['external_branches'] if r['entry']])==1
    assert not quotient['external_literal_pools'] and not quotient['stored_address_words']
    assert len(remainder['external_branches'])==1 and remainder['external_branches'][0]['entry']
    assert remainder['external_literal_pools']==[{'pc':0x4a10e,'pool':0x4a110}]
    assert remainder['stored_address_words']==[{'offset':0x4cdaf,'value':0x20011802,'entry':False}]
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
    assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    assembly=subprocess.check_output([pre,'-D','--start-address=0x49ae0','--stop-address=0x4a110',str(wrapper)],text=True);code=decode(assembly)
    for pool,value,consumers in [(0x49bd0,0x0da24260,[(0x49b6a,'r12'),(0x49b76,'r1'),(0x49b82,'r0')]),(0x4a10c,0x100155d4,[(0x49e02,'r6'),(0x49eaa,'r4'),(0x49eec,'r2')])]:
        assert int.from_bytes(stock[pool:pool+4],'little')==value
        for pc,reg in consumers:
            assert code[pc][:2]==('lrw',f'{reg}, {value:#x}')
            line=next(l for l in assembly.splitlines() if l.strip().startswith(f'{pc:x}:'))
            assert f'// {pool:x} ' in line
    reversal=[]
    for index in range(256):
        reverse=int(f'{index:08b}'[::-1],2)
        if index<reverse:reversal.extend((index*8,reverse*8))
    generated=b''.join(x.to_bytes(2,'little') for x in reversal)
    assert len(generated)==480 and generated==stock[0x4cd34:0x4cf14]
    assert generated[0x4cdaf-0x4cd34:0x4cdaf-0x4cd34+4]==(0x20011802).to_bytes(4,'little')
    result={'stock_sha256':IMAGE_SHA,'raw_quotient':quotient,'raw_remainder':remainder,'classifications':[{'finding_pc':0x49bd2,'literal':0x49bd0,'value':0x0da24260},{'finding_pc':0x4a10e,'literal':0x4a10c,'value':0x100155d4},{'stored_word_offset':0x4cdaf,'mathematical_table_start':0x4cd34,'table_sha256':sha(generated)}],'source_admitted':False,'limits':['All listed raw artifacts have literal-consumer or complete mathematical-table evidence. Computed branches, other mappings and full application execution remain outside scope.']}
    (ROOT/'docs/research/gx8002-unsigned-division-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context()['classifications'])
