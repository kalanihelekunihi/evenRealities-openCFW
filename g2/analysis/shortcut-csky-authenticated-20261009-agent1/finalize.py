from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent; repo=root.parents[2]
campaign=repo/'g2/build/pseudocode-first/20260930T190500Z'
identity=json.loads((campaign/'identity.json').read_text())
images={x['id']:x for x in map(json.loads,(campaign/'inventory/images.jsonl').open())}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
bound=[]
for record in [identity['bundle'],identity['components']['codec']]:
    p=repo/record['path']; assert p.stat().st_size==record['size'];assert sha(p)==record['sha256'];bound.append(record)
payload=(repo/identity['components']['codec']['path']).read_bytes()
bodies=[]
for image,base,start,end,name in [('binh_a_stage1',0x0fffffe8,0x10000acc,0x10000af4,'spl_board_init_r_candidate'),('binh_a_stage2_sram',0x10023400,0x10023500,0x1002351e,'reset_handler_candidate'),('binh_a_stage2_sram',0x10023400,0x10023528,0x10023540,'clear_bss_candidate'),('binh_a_stage2_sram',0x10023400,0x1002354c,0x100235e2,'system_init_candidate')]:
    rec=images[image];p=repo/rec['content_path']; data=p.read_bytes(); assert sha(p)==rec['content_sha256'];lo,hi=rec['mapping_model']['source']['component_span'];assert data==payload[lo:hi]
    a,b=start-base,end-base
    bodies.append({'image_id':image,'name':name,'runtime_span_conditional':[start,end],'child_span':[a,b],'codec_span':[lo+a,lo+b],'bytes':b-a,'sha256':hashlib.sha256(data[a:b]).hexdigest(),'state':'partial_callee_effects_or_external_premises','file_to_runtime_addend':base})
paths=[campaign/'identity.json',campaign/'inventory/images.jsonl',campaign/'receipts/G1-target-and-inventory-107/receipt.json',repo/'third-party/upstream/nationalchip-lvp-kws/arch/cpu/csky/ck804/start.S',repo/'third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/system.c',repo/'third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/spl/spl.c',repo/'third-party/upstream/nationalchip-lvp-kws/include/spl/spl.h',repo/'third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include/csi_gcc.h',repo/'third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include/core_ck804.h',repo/'third-party/tools/ghidra-csky/C-SKY/data/languages/32b_priv.sinc',campaign/'tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump',root/'ExportStartup.java',root/'run.py',root/'validate_mfcr.py']
(root/'authentication-and-bodies.json').write_text(json.dumps({'schema_version':1,'campaign_id':identity['campaign_id'],'target_sha256':identity['target_sha256'],'authenticated_artifacts':bound,'bodies':bodies,'input_hashes':{str(p.relative_to(repo)):sha(p) for p in paths},'unique_scoped_instruction_bytes':sum(x['bytes'] for x in bodies),'qualification':'Local analysis only; independent review and full effects remain outstanding; canonical mapping/gates unchanged.'},indent=2)+'\n')
print('authenticated whole bundle, codec, canonical slices, and four body hashes')
