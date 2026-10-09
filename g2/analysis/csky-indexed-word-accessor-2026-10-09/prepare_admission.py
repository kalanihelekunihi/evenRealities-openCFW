from pathlib import Path
import json,hashlib,re
O=Path(__file__).resolve().parent;R=O.parents[2]
C=R/'g2/build/pseudocode-first/20260930T190500Z'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:str(p.relative_to(R))
pin=lambda p:{'path':rel(p),'sha256':sha(p)}
result=json.loads((O/'results.json').read_text())
review=R/'g2/analysis/coverage-audit-parallel-2026-10-09/CSKY-REVIEW.md'
inputs=[O/'results.json',O/'body.objdump.txt',O/'pseudocode.md',O/'verify.py',O/'ownership-scan.json',review,R/'g2/analysis/coverage-audit-parallel-2026-10-09/CSKY-VERIFICATION.json',C/'analysis/csky-recovery-5316/001/full-xip.objdump.txt',C/'analysis/csky-recovery-5316/001/decoder-receipt.json',C/'reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin',R/'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin']
identity={'schema_version':1,'campaign_id':'20260930T190500Z','target_sha256':'f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa','component':'codec','image_id':'binh_a_stage2_xip','address_space':'conditional_stage2_xip_10203004','isa_mode':'C-SKY_ABIv2','function_id':'codec:binh_a_stage2_xip:conditional_stage2_xip_10203004:270555316:csky_abiv2','entry':0x102058b4,'runtime_range':[0x102058b4,0x102058c4],'child_range':[0x28b0,0x28c0],'payload_range':[0xee40,0xee50],'runtime_base':0x10203004,'component_payload_offset':0xc590,'body_sha256':result['body_sha256'],'countable_body_bytes':16,'direct_inputs':[pin(p) for p in inputs]}
instructions=[]
for line in (O/'body.objdump.txt').read_text().splitlines():
 m=re.match(r'^([0-9a-f]+):\s+([0-9a-f]+)\s+(.*)',line)
 if m:instructions.append({'address':int(m[1],16),'bytes':len(m[2])//2,'decoder_word':m[2],'instruction':m[3]})
proposal={**identity,'record_kind':'review_ready_adoption_proposal_not_campaign_admission','owner':'current_reconstruction_execution_track','exclusive_output_path':rel(O),'required_gate_receipt':pin(C/'receipts/G1-target-and-inventory-107/receipt.json'),'instruction_correspondence':instructions,'edges':[{'from':0x102058bc,'to':0x102055ec,'kind':'direct_call','shared_dependency_not_counted':True},{'from':0x10205b2a,'to':0x102058b4,'kind':'observed_direct_caller'},{'from':0x102058c2,'kind':'return'}],'independent_review':{'reviewer':'parallel_coverage_audit_track','record':pin(review),'decision':'bounded_static_supported_coordinator_consideration_pending'},'accepted':False,'coverage_update_performed':False,'unresolved':['conditional live mapping','formal ABI and memory/device identity','coordinator serialization and adoption','global ownership and code-data reconciliation']}
(O/'adoption-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
proposal['author_task_id']='01a0f4a0-6c2a-70e7-8394-b1e0c936f028'
proposal['independent_review']['reviewer_task_id']='01a120b1-9d22-7596-9ee5-a6d93342c014'
proposal['independent_review']['proposal_review']=pin(R/'g2/analysis/coverage-audit-parallel-2026-10-09/PROPOSAL-REVIEW.md')
(O/'adoption-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
prior=C/'analysis/csky-recovery-5316/001/source-map.json';contract=C/'tasks/P2-csky-recovery-5316.json'
correction={'schema_version':1,'campaign_id':identity['campaign_id'],'target_sha256':identity['target_sha256'],'record_kind':'additive_prior_mapping_correction_proposal','original_inputs':[pin(prior),pin(contract)],'child_range':[0x28a0,0x28b0],'component_payload_offset':0xc590,'reported_payload_range':[0xf430,0xf440],'correct_payload_range':[0xee30,0xee40],'offset_error':0x600,'evidence':[pin(review),pin(C/'reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin'),pin(R/'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin')],'originals_changed':False,'downstream_coverage_correction_performed':False,'remaining_action':'coordinator inspect dependent payload coverage rows before admission'}
(O/'prior-mapping-correction-proposal.json').write_text(json.dumps(correction,indent=2)+'\n')
print('review-ready identity, instruction correspondence, inputs and correction proposal written; no admission')
