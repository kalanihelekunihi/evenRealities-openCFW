# SPDX-License-Identifier: MIT
"""Classify only structurally supported findings from the broad address scan."""
import json,subprocess
from analyze_gx8002_double_wrapper_references import analyze
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode

def analyze_context():
    mul=analyze(0x4a790,0x4a990);div=analyze(0x4a990,0x4aaa8)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D',str(wrapper)],text=True))
    classified=[]
    # These four unaligned words straddle a data pool and the next LRW opcode.
    for off,pointer,consumer,pool,loaded in [
        (0x10426,0x20027b60,0x10428,0x1042c,0x20027b60),
        (0x1042e,0x20027b60,0x10430,0x10434,0x20030000),
        (0x3bb8a,0x20017390,0x3bb8c,0x3bb90,0x200167d0),
        (0x42786,0x20017700,0x42788,0x4278c,0x20017700)]:
        assert int.from_bytes(stock[off-2:off+2],'little')==pointer
        assert stock[consumer:consumer+2]==bytes.fromhex('0110')
        assert code[consumer][:2]==('lrw','r0, '+hex(loaded))
        assert code[consumer+2][0]=='rts'
        assert int.from_bytes(stock[pool:pool+4],'little')==loaded
        row=next(r for r in mul['stored_address_words'] if r['offset']==off)
        classified.append(dict(row,classification='unaligned pool/instruction boundary',preceding_data_word=pointer,following_lrw=consumer,following_pool=pool))
    pool_findings=[]
    for report,pool in [(mul,0x4a78c),(div,0x4a98c)]:
        # Preserve raw findings even where the consumer has not been established.
        assert int.from_bytes(stock[pool:pool+4],'little')==0x100155c0
        finding=report['external_literal_pools'];assert finding==[{'pc':pool+2,'pool':pool+4}]
        pool_findings.append({'finding':finding[0],'classification':'linear decoding of upper half of NaN pointer pool','data_offset':pool,'pointer':0x100155c0})
    unresolved=[r for r in mul['stored_address_words'] if r['offset'] not in {x['offset'] for x in classified}]
    from analyze_gx8002_model_command_chain import analyze as commands,START
    chain=commands();model_findings=[]
    for finding in unresolved:
        off=finding['offset']
        command=next(c for c in chain['commands'] if START+c['offset']<=off<START+c['offset']+c['bytes'])
        start=START+command['offset']
        assert command['opcode']==1 and command['sequential'] and command['bytes']==44
        assert off-start==23
        control=int.from_bytes(stock[start+20:start+24],'little')
        following=int.from_bytes(stock[start+24:start+28],'little')
        assert control&15==command['subtype'] and following==0x00100120
        assert stock[off:off+4]==bytes.fromhex('00200110')
        row=dict(finding,classification='unaligned model command field boundary',command_offset=start,operator=command['operator'],control_word=control,following_word=following)
        if 'tensor_operands' in command:
            assert command['tensor_operands']['extents']==[1,1,32]
            row['decoded_extents']=[1,1,32]
        model_findings.append(row)
    result={'model_command_sha256':chain['command_sha256'],'model_field_boundaries':model_findings,'stock_sha256' :IMAGE_SHA,'classified_stored_words':classified,'classified_linear_pools':pool_findings,'unresolved_stored_words':[],'source_admitted':False,'limits':['Classifications describe byte structure, not proof against arbitrary computed or unaligned reads. Model command boundaries and control subtype are authenticated; only the tensor-vector shape is independently decoded here. Activation/batch-normalization payload semantics and model reconstruction remain incomplete.']}
    (ROOT/'docs/research/gx8002-muldiv-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context())
