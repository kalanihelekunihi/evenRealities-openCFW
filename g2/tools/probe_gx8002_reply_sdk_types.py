# SPDX-License-Identifier: MIT
"""Stage SDK packet-field rewrites; measure fit without changing registered code."""
import json,subprocess
from build_gx8002_reply_defaults import build,ROOT,sha,Elf32
from verify_gx8002_analog_source import FLAGS


def probe():
    candidate=build();out=ROOT/'build/gx8002-reply-sdk-types';out.mkdir(parents=True,exist_ok=True)
    sources=ROOT/'components/shared/gx8002';prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for name,envelope in (('app_reply',60),('i2s_ack',44)):
        original=(sources/('runtime_gx8002_'+name+'.c')).read_text();text=original
        p=out/(name+'.c');p.write_text(text)
        subprocess.run([prefix+'gcc','-Os',*FLAGS[1:],'-fno-store-merging','-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/common'),'-c',str(p),'-o',str(out/(name+'.o'))],check=True)
        script=ROOT/'build'/('gx8002-'+name.replace('_','-'))/'candidate.ld';elfpath=out/(name+'.elf')
        subprocess.run([prefix+'ld','-T',str(script),str(out/(name+'.o')),'-o',str(elfpath)],check=True)
        elf=Elf32(elfpath.read_bytes(),name);section=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(section)
        (out/(name+'.disassembly.txt')).write_text(subprocess.check_output([prefix+'objdump','-d',str(elfpath)],text=True))
        rows.append({'name':name,'original_source_sha256':sha(original.encode()),'staged_source_sha256':sha(text.encode()),'compiled_bytes':len(body),'envelope_bytes':envelope,'fits':len(body)<=envelope,'compiled_sha256':sha(body)})
    contract=(out/'app_reply.c').read_text()+'\n'+(out/'i2s_ack.c').read_text()+'\n'+(sources/'runtime_gx8002_reply_defaults.c').read_text()
    (out/'type_contract.c').write_text(contract)
    subprocess.run([prefix+'gcc','-Os',*FLAGS[1:],'-fno-store-merging','-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/common'),'-fsyntax-only',str(out/'type_contract.c')],check=True)
    return {'candidate':candidate,'type_contract_sha256':sha(contract.encode()),'helpers':rows,'source_admitted':False,'limits':['SDK field rewrite probe only. Removing prior member volatile qualifiers may change access order, and packed bitfield writes may change widths. Requires decoded memory/order/ABI qualification before promotion. Registered inputs unchanged.']}
if __name__=='__main__':
    r=probe();(ROOT/'docs/research/gx8002-reply-sdk-types-probe.json').write_text(json.dumps(r,indent=2)+'\n');print(r['helpers'])
