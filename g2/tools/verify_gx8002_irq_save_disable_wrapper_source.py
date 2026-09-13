# SPDX-License-Identifier: MIT
"""Experimental admission of IRQ save/disable forwarding entry."""
import json,re,shutil
from verify_gx8002_irq_save_disable_wrapper import verify as core,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();path=ROOT/'build/gx8002-irq-save-disable-wrapper/wrapper.elf';elf=Elf32(path.read_bytes(),'wrapper');section=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(section);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert section['address']==0x10025534 and len(body)==8 and body==stock[0x17548:0x17550]
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-irq-save-disable-wrapper-source-verification.json':continue
        p=ROOT/'docs/research'/name;assert p.exists();r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not(a<0x17550 and 0x17548<a+n),(name,o)
    symbol='open_cfw_gx8002_irq_save_disable_wrapper';row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':8,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x17548,'bytes':8,'sha256':sha(body),'region':'image_a_sram'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'wrapper.elf')
    files=('build_gx8002_irq_save_disable_wrapper.py','verify_gx8002_irq_save_disable_wrapper.py','verify_gx8002_irq_save_disable_wrapper_source.py','compare_gx8002_irq.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission with verified forwarding and decoded callee effects. Descriptive reconstructed symbol used; original public wrapper name remains unknown.','Separate decoder frames and finite register-bank corpus; physical interrupt concurrency and full source reconstruction unfinished.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-irq-save-disable-wrapper-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('IRQ forwarding admission gate passed')
