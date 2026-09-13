# SPDX-License-Identifier: MIT
"""Inventory both SRAM aliases of original FFT ranges before source admission."""
import json,subprocess
from analyze_gx8002_fft_cluster_references import CODE,DATA
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True))
    spans=[(name,a,b,'code') for name,(a,b) in CODE.items()]+[(name,a,a+size,'data') for name,(a,size,_) in DATA.items()]
    def owner(off):return next((name for name,a,b,_ in spans if a<=off<b),None)
    rows=[];unresolved_literals={}
    for name,start,end,kind in spans:
        for base in (0x10003000,0x20003000):
            low,high=start-0x3b940+base,end-0x3b940+base
            words=[];literals=[]
            for off in range(len(stock)-3):
                v=int.from_bytes(stock[off:off+4],'little')
                if low<=v<high:words.append({'offset':off,'value':v,'source_component':owner(off)})
            for pc,(op,args,width) in code.items():
                if op=='lrw':
                    try:value=int(args.split(',')[-1].strip(),0)
                    except ValueError:
                        unresolved_literals[pc]=args;continue
                    if low<=value<high:literals.append({'pc':pc,'value':value,'source_component':owner(pc)})
            rows.append({'target':name,'kind':kind,'package_range':[start,end],'alias_range':[low,high],'stored_words':words,'loaded_literals':literals})
    external=[{'target':r['target'],'alias':r['alias_range'][0],'form':form,**item} for r in rows for form,key in [('word','stored_words'),('literal','loaded_literals')] for item in r[key] if item['source_component'] is None]
    instruction_matches=[]
    for item in external:
        if item['target']=='radix4' and item['form']=='word' and item['offset'] in code:
            pc=item['offset'];op,args,width=code[pc]
            assert op=='flds' and width==4,(hex(pc),op,args,width)
            instruction_matches.append({'offset':pc,'word_value':item['value'],'operation':op,'arguments':args,'classification':'Complete 32-bit floating-point load encoding at a decoded instruction boundary; numeric match is not an immediate address operand.'})
    assert len(instruction_matches)==34
    result={'scan_range':[0x3b940,0x4f9cc],'unresolved_literal_decodes':unresolved_literals,'instruction_encoding_matches':instruction_matches,'stock_sha256':IMAGE_SHA,'ranges':rows,'external_findings':external,'source_admitted':False,
            'limits':['Every byte offset scanned for known-alias pointer words; backup text scanned for resolved lrw values.','Raw matches require contextual classification. Arithmetic pointers, code outside backup text and other mappings are not exhaustively covered.']}
    (ROOT/'docs/research/gx8002-fft-alias-references.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print(json.dumps(r['external_findings'],indent=2))
