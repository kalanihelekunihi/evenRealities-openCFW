# SPDX-License-Identifier: MIT
"""Inventory backup tick dependencies and literal/state evidence without extraction."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/lvp_mode_denoise.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    upstream=subprocess.check_output(['git','-C',str(sdk),'cat-file','blob',blob])
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oracle=Elf32(wrapper.read_bytes(),'stock')
    assert sha(oracle.contents(next(s for s in oracle.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    disasm=subprocess.check_output([pre,'-D','--start-address=0x44298','--stop-address=0x44550',str(wrapper)],text=True)
    out=ROOT/'build/gx8002-backup-denoise-tick';out.mkdir(exist_ok=True)
    (out/'stock.disassembly.txt').write_text(disasm)
    code=decode(disasm);cluster_path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf';elf=Elf32(cluster_path.read_bytes(),'cluster')
    targets={};fields=[];float_ops=[]
    for pc,(op,args,width) in sorted(code.items()):
        if op=='bsr':targets.setdefault(int(args,0),[]).append(pc)
        if op in ('ld.w','st.w','flds'):
            match=re.search(r'\(r5, (0x[0-9a-f]+)\)',args)
            if match:fields.append({'pc':pc,'operation':op,'base_register':'r5','offset':int(match[1],0)})
        if op.startswith('f'):float_ops.append({'pc':pc,'operation':op,'operands':args})
    rows=[]
    for target,sites in sorted(targets.items()):
        address=target-0x38940+0x10000000
        names=[s['name'] for s in elf.symbols() if s['value']==address and s['section'] not in (0,0xfff1) and s['type']==2 and s['name']]
        rows.append({'package_target':target,'runtime_target':address,'call_sites':sites,'allocated_function_symbols':names})
    result={'stock_sha256':IMAGE_SHA,'package_entry':0x44298,'runtime_entry':0x1000b958,'instruction_span_bytes':0x44550-0x44298,'envelope_bytes':0x44584-0x44298,
            'sdk_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'upstream_sha256':sha(upstream),'cluster_sha256':sha(cluster_path.read_bytes()),
            'direct_calls':rows,'source_target_count':sum(bool(r['allocated_function_symbols']) for r in rows),'target_count':len(rows),
            'r5_relative_word_accesses':fields,'floating_point_instructions':float_ops,'source_admitted':False,
            'limits':['Direct-call census is not transitive closure or execution qualification. Symbol aliases may name the same function.',
                      'r5-relative access list records syntax; full register/dataflow and field semantics still require reconstruction.',
                      'Pinned upstream tick is a structural reference only: backup adds reinitialization and algorithm-specific processing branches.']}
    (ROOT/'docs/research/gx8002-backup-denoise-tick-analysis.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print(r['source_target_count'],r['target_count']);print([(hex(x['package_target']),x['allocated_function_symbols']) for x in r['direct_calls']])
