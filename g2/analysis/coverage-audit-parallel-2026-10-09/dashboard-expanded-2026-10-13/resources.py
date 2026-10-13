from pathlib import Path
import json,hashlib
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();M=json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text());payloads={};hashes={};rows=[];rejected=[];inputs={}
for c in M['components']:
 p='g2/'+c['provider']['path'];b=(R/p).read_bytes();assert sha(b)==c['provider']['sha256'];payloads[c['name']]=b;hashes[c['name']]=sha(b)
def load(p):
 b=(R/p).read_bytes();inputs[p]=sha(b);return json.loads(b)
def add(cid,a,b,label,kind,typ,summary,evidence,expected=None,address=None):
 assert 0<=a<b<=len(payloads[cid]);digest=sha(payloads[cid][a:b]);ok=expected is None or digest==expected
 r={'component':cid,'payloadRange':[a,b],'addressRange':address,'label':label,'kind':kind,'format':typ,'contentsSummary':summary,'sha256':digest,'payloadSha256':hashes[cid],'evidencePath':evidence,'confidence':'original bytes authenticate against resource receipt' if expected else 'canonical structural/data inventory, original byte hash recorded','isConfirmedNonMCUCode':kind!='accelerator_command_stream','overlapPolicy':'orthogonal resource overlay; instruction/data conflicts require review; never erase underlying evidence'}
 if ok:rows.append(r)
 else:rejected.append({'label':label,'reason':'resource-receipt hash does not match locked original slice','evidence':evidence})
p='g2/tools/manifests/g2-l8-resource-map.json';j=load(p);assert j['payload_sha256']==hashes['apollo_main']
for x in j['assets']:
 a,b=x['pixel_payload_range'];add('apollo_main',a,b,x['asset']+' pixels','image','L8 grayscale raster',f"{x['width']}x{x['height']}, stride{x['stride']}; decoded pixels, not inferred PNG/JPEG file",p,x['pixel_sha256'],x['pixel_runtime_range'])
 a,b=x['descriptor_payload_range'];addr=int(x['descriptor_runtime'],16);add('apollo_main',a,b,x['asset']+' descriptor','image_descriptor','LVGL image descriptor',f"descriptor for{x['width']}x{x['height']}L8pixel asset",p,x['descriptor_sha256'],[addr,addr+b-a])
p='g2/analysis/source-replacement-ledger-2026-10-08-readonly/mapped-readonly-data.json'
for x in load(p):
 a=x['address']-0x410000;n=x['bytes'];add('apollo_bootloader',a,a+n,x.get('symbol','readonly'),'embedded_text' if x.get('text') else 'readonly_table','NUL-terminated embedded string' if x.get('text') else 'recorded readonly data',str(x.get('text',x.get('category','')))[:140],p,x.get('sha256'),[x['address'],x['address']+n])
p='g2/analysis/c-source-completion-20261011/m0/case-semantic-strings.json';j=load(p);assert j['stock_sha256']==hashes['case']
for x in j['rows']:
 addr=int(x['native_address'],16);a=addr-0x08000000+32;n=x['length_with_nul'];add('case',a,a+n,'text@'+x['native_address'],'embedded_text','NUL-terminated embedded string',x['semantic_text'][:140],p,x['sha256_with_nul'],[addr,addr+n])
p='g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl';raw=(R/p).read_bytes();inputs[p]=sha(raw);IM={x['id']:x for x in map(json.loads,raw.decode().splitlines())}
for ident,kind,typ in [('npu_kws_weights','model_weights','NationalChip NPU/KWS weight data'),('npu_kws_command','accelerator_command_stream','NationalChip NPU hardware command stream')]:
 x=IM[ident];a,b=x['candidate_mapping']['package_component_offset'];ib=(R/x['content_path']).read_bytes();assert sha(ib)==x['content_sha256'] and payloads['codec'][a:b]==ib;add('codec',a,b,ident,kind,typ,'Canonical nested accelerator asset; candidate DRAM staging is separate from flash address. Command stream is executable to accelerator, not classified as MCU C.',p,x['content_sha256'])
for c in M['components']:
 for x in c['regions']:
  if x.get('address_status')=='container_only' or x['name']=='record_2_fhdr':add(c['name'],x['file_offset'],x['file_offset']+x['size'],x['name'],'container_metadata','EVENOTA/FWPK/record header','Authenticated package structure; no fabricated runtime address','g2/manifests/g2-2.2.6.10.json')
# Pin known format/provenance lead files even if no precise binary asset endpoints exist.
font_leads=[str(p.relative_to(R)) for p in (R/'g2/analysis/c-source-completion-20261011').rglob('*.json') if 'font' in str(p).lower() or 'bitmap' in str(p).lower()];calibration_leads=[str(p.relative_to(R)) for p in (R/'g2/analysis').glob('touch-calibration*/*.json')];result={'resourceIntervals':rows,'rejectedBindings':rejected,'resourceInputHashes':inputs,'unplacedResourceEvidence':{'fonts_and_bitmap_processing':{'paths':font_leads,'reason':'existing function/processing receipts are not serialized font-file boundary map; not colored as exact font bytes'},'calibration_configuration':{'paths':calibration_leads,'reason':'processing tests do not independently locate full product calibration/config asset'}},'limits':['Only confirmed manifests/byte hashes produce resource spans.','Embedded text is not classified as standalone text files.','Font/image processing C is code, not the resource itself.','NPU command stream is accelerator executable and must not be globally excluded from executable denominator.','Padding not inferred from zero/FF/disassembly gaps.','No whole image exclusive code/noncode partition is claimed.']}
(O/'resource-evidence.json').write_text(json.dumps(result,separators=(',',':')));print('resources',len(rows),'hash rejection',len(rejected),'fonts leads',len(font_leads),'bytes',(O/'resource-evidence.json').stat().st_size)
