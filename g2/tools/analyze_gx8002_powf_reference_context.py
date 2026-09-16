# SPDX-License-Identifier: MIT
"""Preserve power reference findings and classify proven instruction-overlap hits."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode

def character_flags(c):
    if c<32:return 8|(32 if 9<=c<=13 else 0)
    if c==127:return 8
    if 128<=c<160:return 0
    if c in (32,160):return 0xa0
    if 48<=c<=57:return 4
    if 65<=c<=90:return 1|(64 if c<=70 else 0)
    if 97<=c<=122:return 2|(64 if c<=102 else 0)
    if 192<=c<=222 and c!=215:return 1
    if 223<=c<=255 and c!=247:return 2
    return 16

def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x489fc,0x490a8,require_entry_only=False)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    starts={0x1e87:(0x1e86,'movih','r1, 256'),0x5401:(0x5400,'movih','r1, 256'),0x5467:(0x5466,'movih','r1, 256'),0x3bcdd:(0x3bcdc,'movih','r1, 256'),0x40267:(0x40266,'movi','r16, 256'),0x4445b:(0x4445a,'movi','r2, 256'),0x4782b:(0x4782a,'fcmpzhss','fr0')}
    table=bytes(character_flags(c) for c in range(256))
    assert stock[0x8ad8:0x8bd8]==table
    classified_data=[]
    classified=[];unresolved=[]
    for row in raw['stored_address_words']:
        off=row['offset'];assert int.from_bytes(stock[off:off+4],'little')==row['value']
        if off in (0x8b30,0x8bac):
            classified_data.append({'raw':row,'table_start':0x8ad8,'table_size':256,'table_sha256':sha(table),'character_indices':list(range(off-0x8ad8,off-0x8ad8+4)),'classification':'Four character-classification flags inside fully regenerated table.'})
            continue
        if off not in starts:unresolved.append(row);continue
        pc,op,args=starts[off]
        text=subprocess.check_output([pre,'-D','--start-address='+hex(pc),'--stop-address='+hex(pc+8),str(wrapper)],text=True)
        code=decode(text);assert code[pc]==(op,args,4)
        assert off==pc+1 and pc+4 in code
        classified.append({'raw':row,'instruction_start':pc,'instruction':code[pc],'following_instruction':code[pc+4],'classification':'Byte-offset scan overlaps a complete four-byte instruction and the next instruction; not a pointer literal at this execution boundary.'})
    branch=next(r for r in raw['external_branches'] if not r['entry'])
    assert branch=={'pc':0x489c8,'target':0x48b96,'entry':False}
    text=subprocess.check_output([pre,'-D','--start-address=0x487fc','--stop-address=0x48804',str(wrapper)],text=True)
    assert decode(text)[0x487fc][:2]==('lrw','r2, 0x3e2404e7') and '489c8' in text
    assert int.from_bytes(stock[0x489c8:0x489cc],'little')==0x3e2404e7
    branch_context={'raw':branch,'literal_offset':0x489c8,'literal_value':0x3e2404e7,'consumer':0x487fc,'classification':'Apparent branch decodes the low halfword of a consumed numeric literal.'}
    from analyze_g2_codec_stage2_sections import analyze as section_map,SEG2_OFF,KWS_CMD_SIZE
    mapping=section_map()
    command_start=SEG2_OFF+0xf804
    command=stock[command_start:command_start+KWS_CMD_SIZE]
    assert sha(command)==mapping['kws_model_payload']['cmd']['sha256']
    from analyze_gx8002_model_command_chain import analyze as command_chain
    chain=command_chain();assert chain['command_sha256']==sha(command)
    inventory=json.loads((ROOT/'docs/research/gx8002-gxdnn-cmodel-inventory.json').read_text())
    member=next(m for m in inventory['members'] if m['name']=='cmd_parse.o')
    parser=ROOT/'build/gxdnn-analysis/cmd_parse.o';assert sha(parser.read_bytes())==member['sha256']
    parser_text=subprocess.check_output(['xcrun','llvm-objdump','-d','--disassemble-symbols=parse_op_active_cmd,parse_op_format_cmd',str(parser)],text=True)
    for name in ('active','format'):
        body=parser_text.split('<parse_op_'+name+'_cmd>:')[1].split('Disassembly of section')[0]
        assert '8b 50 14' in body and 'c1 ea 14' in body and '81 e2 ff 0f 00 00' in body and '0f b6 50 14' in body
    parser_evidence={'upstream_commit':inventory['commit'],'object_sha256':member['sha256'],'disassembly_sha256':sha(parser_text.encode()),'shape_payload_offset':20,'shape_fields':'word >> 20, (word >> 8) & 0xfff, byte at offset 20'}
    model_context=[];remaining=[]
    for row in unresolved:
        off=row['offset'];assert command_start<=off<command_start+KWS_CMD_SIZE and off%4==3
        aligned=off&~3
        record=next(r for r in chain['commands'] if r['offset']<=off-command_start<r['offset']+r['bytes'])
        payload_start=command_start+record['offset']+4
        assert record['sequential'] and off==payload_start+19
        if record['operator']=='tensor_tensor':
            assert record['tensor_operands']['extents']==[1,1,2]
            classified_data.append({'raw':row,'command':record,'classification':'Crosses tensor-operation control word and packed shape, not operand-address fields.'})
        elif record['operator'] in ('active','format'):
            shape=int.from_bytes(stock[payload_start+20:payload_start+24],'little')
            extents=[shape>>20,(shape>>8)&0xfff,shape&255];assert extents==[1,1,2]
            classified_data.append({'raw':row,'command':record,'extents':extents,'parser_evidence':parser_evidence,'classification':'Crosses final control-word byte and packed shape bytes; parser consumes shape numerically, not as pointer.'})
        else:remaining.append(row)
        model_context.append({'command':record,'payload_relative_offset':off-payload_start,'raw':row,'command_relative_offset':off-command_start,'aligned_word_offsets':[aligned,aligned+4],'aligned_words':[int.from_bytes(stock[p:p+4],'little') for p in (aligned,aligned+4)],'classification':'Unresolved command-stream bytes; apparent pointer crosses aligned words.'})
    result={'model_command_context':model_context,'command_region':{'offset':command_start,'size':KWS_CMD_SIZE,'sha256':sha(command)},'classified_data':classified_data,'branch_context':branch_context,'stock_sha256':IMAGE_SHA,'raw':raw,'classified_instruction_overlaps':classified,'unresolved_stored_words':remaining,'unresolved_branches':[],'source_admitted':False,'limits':['Local authenticated instruction-boundary classification only. Data candidates require further evidence. Computed targets and alternate instruction entry points are not closed.']}
    (ROOT/'docs/research/gx8002-powf-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze_context();print(len(r['classified_instruction_overlaps']),len(r['unresolved_stored_words']),len(r['unresolved_branches']))
