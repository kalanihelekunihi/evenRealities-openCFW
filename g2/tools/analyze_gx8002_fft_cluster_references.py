# SPDX-License-Identifier: MIT
"""Whole FFT reference inventory for relocation planning; no admission implied."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
CODE={'rfft':(0x478a4,0x47914),'split_forward':(0x47914,0x479a8),'split_inverse':(0x479a8,0x47a00),'cfft':(0x47b14,0x47bf4),'radix4_by2':(0x47bf4,0x47c98),'radix4_by2_inverse':(0x47c98,0x47d3c),'radix4':(0x47d3c,0x47f50),'radix4_inverse':(0x47f50,0x48164),'bit_reverse':(0x48164,0x4818a)}
DATA={'complex_descriptor':(0x4cd24,16,0x100143e4),'bit_reverse_table':(0x4cd34,480,0x100143f4),'complex_coefficients':(0x4cf14,768,0x100145d4),'real_coefficients':(0x4da18,1024,0x100150d8),'inverse_descriptor':(0x4f94c,20,0x2001700c),'forward_descriptor':(0x4f960,20,0x20017020)}
DELTA=0x10003000-0x3b940

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    assembly=subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True);decoded=decode(assembly)
    def code_owner(offset):return next((n for n,(a,b) in CODE.items() if a<=offset<b),None)
    def data_owner(offset):return next((n for n,(a,size,_) in DATA.items() if a<=offset<a+size),None)
    results={}
    for name,(start,end) in CODE.items():
        branches=[];pools=[];pointers=[]
        for pc,(op,args,width) in decoded.items():
            if start<=pc<end or op not in ('br','bsr','bt','bf','bez','bnez','bnezad','bhz','blz','bhsz','blsz'):continue
            try:target=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if start<=target<end:branches.append({'offset':pc,'target':target,'entry':target==start,'source_function':code_owner(pc),'source_data':data_owner(pc)})
        for line in assembly.splitlines():
            m=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
            if m:
                pc,target=(int(v,16) for v in m.groups())
                if not start<=pc<end and start<=target<end:pools.append({'offset':pc,'pool':target,'source_function':code_owner(pc),'source_data':data_owner(pc)})
        for offset in range(len(stock)-3):
            value=int.from_bytes(stock[offset:offset+4],'little')
            if start+DELTA<=value<end+DELTA:pointers.append({'offset':offset,'value':value,'entry':value==start+DELTA,'source_function':code_owner(offset),'source_data':data_owner(offset)})
        results[name]={'range':[start,end],'branches':branches,'pool_loads':pools,'stored_pointers':pointers}
    data={}
    for name,(offset,size,address) in DATA.items():
        pointers=[]
        for source in range(len(stock)-3):
            value=int.from_bytes(stock[source:source+4],'little')
            if address<=value<address+size:pointers.append({'offset':source,'value':value,'source_function':code_owner(source),'source_data':data_owner(source)})
        data[name]={'offset':offset,'bytes':size,'runtime_address':address,'pointers':pointers}
    external=[{'function':name,**b} for name,row in results.items() for b in row['branches'] if not b['source_function']]
    cluster=json.loads((ROOT/'docs/research/gx8002-source-rfft-cluster.json').read_text())
    stock_bytes=sum(b-a for a,b in CODE.values())+sum(size for _,size,_ in DATA.values())
    result={'stock_sha256':IMAGE_SHA,'functions':results,'data':data,'external_branch_findings':external,'stock_component_bytes':stock_bytes,'compiled_component_bytes':cluster['code_bytes']+cluster['data_bytes'],'minimum_additional_bytes':max(0,cluster['code_bytes']+cluster['data_bytes']-stock_bytes),'source_admitted':False,'limits':['Conservative raw linear-disassembly inventory, including data decoded as instructions. Findings require contextual classification.','Word search covers every byte offset in the whole codec image, using known runtime aliases only. Computed pointers and other execution regions are not exhaustively excluded.','Size comparison excludes trampolines/alignment and does not imply noncontiguous stock spans can be repacked. No free-memory claim.']}
    (ROOT/'docs/research/gx8002-fft-cluster-references.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print('External branches:',r['external_branch_findings']);print('Bytes stock/source/additional:',r['stock_component_bytes'],r['compiled_component_bytes'],r['minimum_additional_bytes'])
    for n,v in r['functions'].items():
        if v['pool_loads'] or v['stored_pointers']:print(n,v['pool_loads'],v['stored_pointers'])
    for n,v in r['data'].items():print(n,v['pointers'])
