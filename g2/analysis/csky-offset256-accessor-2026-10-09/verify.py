from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
C = ROOT / 'g2/build/pseudocode-first/20260930T190500Z'
start, end, base = 0x102058C4, 0x102058D4, 0x10203004
image = C / 'reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin'
tool = C / 'tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(image) == '49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584'
assert sha(tool) == '7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
contracts = []
overlaps = []
for p in sorted((C / 'tasks').glob('*.json')):
    d = json.loads(p.read_text())
    scope = d.get('scope', '')
    if not isinstance(scope, str): scope = json.dumps(scope)
    ranges = [(int(a,16),int(b,16)) for a,b in re.findall(r'\[\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)',scope)]
    hit = any(a < end and start < b for a,b in ranges)
    # Explicit candidate/entry references are also conservative overlap leads.
    reference = any(x in scope.lower() for x in ('0x102058c4','0x102058d4'))
    contracts.append({'path':str(p.relative_to(ROOT)), 'sha256':sha(p), 'ranges':ranges, 'overlap':hit, 'boundary_reference':reference})
    if hit: overlaps.append(str(p.relative_to(ROOT)))
assert not overlaps, overlaps
body = image.read_bytes()[start-base:end-base]
payload = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin'
assert sha(payload) == 'b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0'
assert payload.read_bytes().find(image.read_bytes()) == 0xc590
assert payload.read_bytes()[0xee50:0xee60] == body
assert body.hex() == 'd114076dff20ffe391fe00b491140000'.replace(' ','')
argv = [str(tool),'-D','--disassemble-zeroes','-b','binary','-m','csky','-EL',f'--adjust-vma={base:#x}',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(image)]
run = subprocess.run(argv,capture_output=True,text=True,check=True)
(OUT/'body.objdump.txt').write_text(run.stdout)
lines = [x for x in run.stdout.splitlines() if re.match(r'^102058[c-d][0-9a-f]:',x)]
assert len(lines)==7, lines
assert ['push','mov','addi','bsr','st.w','pop','bkpt'] == [re.split(r'\s+',x.strip())[2] for x in lines]
caller_disassembly = C/'analysis/csky-recovery-5316/001/full-xip.objdump.txt'
full = caller_disassembly.read_text()
callers = [x for x in full.splitlines() if re.search(r'\bbsr\s+0x102058c4\b',x)]
assert len(callers)==1 and callers[0].startswith('10205b34:'),callers
helper=image.read_bytes()[0x102055ec-base:0x102055f0-base]
assert helper.hex()=='00903c78'
# Semantic fixture checks, not instruction execution or hardware tests.
fixtures=[]
for ptr,value in [(0x1000,0),(0x1000,0x12345678),(0xfffffff8,0xffffffff),(0xffffff00,7)]:
    effective=(ptr+256)&0xffffffff
    memory={effective:value}; output=memory[effective]
    assert output==value
    fixtures.append({'base':ptr,'effective_address':effective,'output_word':output,'return_r0':output})
receipt={'status':'partial_unreviewed','accepted':False,'runtime_mapping':'conditional XIP only','extent':[hex(start),hex(end)],'bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'image':str(image.relative_to(ROOT)),'image_sha256':sha(image),'child_offsets':[hex(start-base),hex(end-base)],'codec_payload_offsets':[hex(0xc590+start-base),hex(0xc590+end-base)],'tool_sha256':sha(tool),'contracts_scanned':len(contracts),'overlaps':overlaps,'callers':callers,'static_checks':'PASS bytes, helper, decoder tiling, direct caller census','semantic_fixtures':fixtures,'instruction_execution':False,'physical_state_claim':False}
receipt['codec_payload_sha256'] = sha(payload)
receipt.update({'schema_version':1,'campaign_id':'20260930T190500Z','target_sha256':'f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa','component':'codec','image_id':'binh_a_stage2_xip','address_space':'conditional_stage2_xip_10203004','isa_mode':'C-SKY_ABIv2','entry':start,'runtime_range':[start,end],'child_range':[start-base,end-base],'payload_range':[0xee50,0xee60],'decoder_argv':argv,'decoder_exit_code':run.returncode,'author_task_id':'01a0f4a0-6c2a-70e7-8394-b1e0c936f028','coverage_count_pending_admission':14,'trailing_bkpt_bytes':2})
receipt['consumed_caller_disassembly'] = {'path':str(caller_disassembly.relative_to(ROOT)), 'sha256':sha(caller_disassembly)}
receipt['payload_mapping_validation'] = 'complete child image match at 0xC590 plus exact body comparison'
review_root=ROOT/'g2/analysis/coverage-audit-parallel-2026-10-09'
receipt['independent_review']={'reviewer_task_id':'01a120b1-9d22-7596-9ee5-a6d93342c014','records':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (review_root/'OFFSET256-REVIEW.md',review_root/'OFFSET256-VERIFICATION.json')],'decision':'bounded_static_supported_not_admission'}
receipt['accounting']={'returned_body_range':[0x102058c4,0x102058d2],'returned_body_bytes':14,'trailing_bkpt_range':[0x102058d2,0x102058d4],'trailing_bkpt_bytes':2,'ordinary_return_reaches_bkpt':False,'executed_bytes_verified':False}
(OUT/'ownership-scan.json').write_text(json.dumps(contracts,indent=2)+'\n')
(OUT/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
