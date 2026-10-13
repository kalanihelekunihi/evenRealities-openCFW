from pathlib import Path
import json,hashlib,struct,zlib,binascii,re,math,collections,datetime,importlib.util,sys
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();T=json.loads((R/'g2/workflow/target.json').read_text());M=json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text());bundle=(R/T['bundle']['verified_local_path']).read_bytes();assert len(bundle)==T['bundle']['size'] and sha(bundle)==T['bundle']['sha256'];spec=importlib.util.spec_from_file_location('accounting_open_cfw',R/'g2/tools/open_cfw.py');mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod);mod.validate_evenota_image(bundle,M)
compact=json.loads((R/'g2/analysis/coverage-audit-parallel-2026-10-09/dashboard-expanded-2026-10-13/compact-dashboard.json').read_text());oldRes=json.loads((R/'g2/analysis/coverage-audit-parallel-2026-10-09/dashboard-expanded-2026-10-13/resource-evidence.json').read_text());IM={x['id']:x for x in map(json.loads,(R/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines())};payloads={};segments=[{'range':[0,176],'kind':'outer_container_metadata','name':'EVENOTA header, six TOC records and trailer','classification':'confirmed_data','sha256':sha(bundle[:176])}];newEvidence=[];scanReports=[];errors=[];candidates=[];ram=[];conflicts=[];checksum=[]
for i,c in enumerate(M['components']):
 entry,off,n,crc=struct.unpack_from('<IIII',bundle,64+16*i);start=off+128;data=bundle[start:off+n];p=(R/'g2'/c['provider']['path']).read_bytes();assert data==p and sha(data)==c['provider']['sha256'];payloads[c['name']]=data;segments.extend([{'range':[off,start],'kind':'component_transport_header','name':c['name']+'128byte header','classification':'confirmed_data','sha256':sha(bundle[off:start])},{'range':[start,off+n],'kind':'component_payload','component':c['name'],'classification':'nested','payloadTranslation':{'bundleStart':start,'payloadStart':0,'length':len(data)},'sha256':sha(data)}]);checksum.append({'component':c['name'],'tocCRC32C':crc,'computedCRC32C':mod.crc32c_msb(data),'valid':crc==mod.crc32c_msb(data)})
def root_offset(im):
 direct=im.get('candidate_mapping',{}).get('package_component_offset')
 if direct:return direct[0]
 parent=im.get('parent_image_id');return im['source_span'][0]+(root_offset(IM[parent]) if parent else 0)
def evidence(cid,a,b,kind,label,classification,source,confidence='structural/hash validated',extra=None):
 assert 0<=a<b<=len(payloads[cid]);row={'component':cid,'payloadRange':[a,b],'kind':kind,'label':label,'exclusiveClaim':classification,'confidence':confidence,'evidence':source,'sha256':sha(payloads[cid][a:b]),'coordinate':'flash-bound payload offset; translate with component addressSpaces'}
 if extra:row.update(extra)
 newEvidence.append(row)
# Preserve exact resource classification; executable accelerator stream has its own code domain.
for r in oldRes['resourceIntervals']:
 a,b=r['payloadRange'];evidence(r['component'],a,b,r['kind'],r['label'],'suspected' if r['kind']=='accelerator_command_stream' else 'confirmed_data',r['evidencePath'],extra={'format':r['format'],'contentsSummary':r['contentsSummary'],'addressRange':r['addressRange'],'codeDomain':'accelerator command program candidate; GXNPU format unresolved' if r['kind']=='accelerator_command_stream' else None})
for im in IM.values():
 parent=im.get('parent_image_id');cid=im.get('payload_id')
 if cid not in payloads:continue
 content=(R/im['content_path']).read_bytes();assert len(content)==im['size'] and sha(content)==im['content_sha256']
 if 'decoded:' in im['id'] or 'ram-' in im['id']:
  span=im['source_span'];sourceStart=span[0]+(root_offset(IM[parent]) if parent else 0);sourceEnd=sourceStart+span[1]-span[0]
  record={'id':im['id'],'component':cid,'sourcePayloadRange':[sourceStart,sourceEnd],'sourceEncodedBytes':sourceEnd-sourceStart,'decodedBytes':len(content),'decodedSha256':sha(content),'transform':im['transform'],'ramAddressSpaces':im.get('address_spaces',[]),'sourceCoordinate':'flash encoded/copy bytes','decodedCoordinate':'RAM/ITCM image, not extra bundle bytes','classification':'initializer contains data/code/pointers; not globally assumed non-executable'};ram.append(record)
  if im['transform']['kind']=='decoded':
   tr=im['transform']['receipt'];tp=Path(tr['path']);tp=tp if tp.is_absolute() else R/tp;assert sha(tp.read_bytes())==tr['sha256'];evidence(cid,sourceStart,sourceEnd,'compressed_initializer','encoded initializer for '+im['id'],'confirmed_data',str(tp.relative_to(R)),extra={'decodedImage':im['id'],'decodedSize':len(content),'decodedContentsType':'unknown code/data mix; compression is not interpreted as font/file','format':'validated canonical stock initializer encoding'})
  elif 'ram-initialized' in im['id']:evidence(cid,sourceStart,sourceEnd,'initialized_ram_copy','initialized RAM image '+im['id'],'confirmed_data','canonical inventory/images.jsonl',extra={'decodedImage':im['id'],'format':'initialized runtime data copy, not filesystem'})
  elif 'ram-vectors' in im['id']:evidence(cid,sourceStart,sourceEnd,'vector_table','copied interrupt-vector table','confirmed_data','canonical inventory/images.jsonl',extra={'format':'32bit vector pointer table'})
# Additional existing mathematical/rodata tables: verify exact original bytes, no provider work.
crcPath=R/'g2/analysis/tinyframe-checksum-build-gap-20261010-implementation/verification.json';ct=json.loads(crcPath.read_text());addr=int(ct['table_address'],16);off=addr-0x437fe0;assert sha(payloads['apollo_main'][off:off+ct['table_length']])==ct['table_sha256'];evidence('apollo_main',off,off+ct['table_length'],'lookup_table','TinyFrame CRC16/ARC lookup table','confirmed_data',str(crcPath.relative_to(R)),'all256little-endian16bit entries match reflected polynomialA001 in existing independent receipt',{'addressRange':[addr,addr+ct['table_length']],'format':'256xuint16 CRC lookup','contentsSummary':'CRC16/ARC byte update table; mathematical verification, not protocol execution'})
tablePath=R/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z/table-provenance.json';bank=next(c for c in compact['components'] if c['id']=='codec');space=next(s for s in bank['addressSpaces'] if s['id']=='codec:binh_b_stage2')
for x in json.loads(tablePath.read_text()):
 addr=int(x['stock_address_conditional_IRAM'],16);off=addr-space['addressStart']+space['payloadStart'];assert sha(payloads['codec'][off:off+x['bytes']])==x['stock_sha256'];evidence('codec',off,off+x['bytes'],'DSP_table',x['symbol'],'confirmed_data',str(tablePath.relative_to(R)),'exact authenticated rodata correspondence; runtime IRAM bank/load mapping remains conditional',{'addressRange':[addr,addr+x['bytes']],'format':'uint16bit-reversal table' if 'BitRev' in x['symbol'] else 'signedQ15coefficient table','contentsSummary':x['symbol'],'coordinate':'payload bytes confirmed; conditional IRAM runtime address'})

# Full-image search for the exact existing LVGL9 L8 schema (all offsets, not six selected examples).
l8Candidates=[];data=payloads['apollo_main'];runtimeBase=0x437fe0;existingResourceKeys={(e['component'],tuple(e['payloadRange']),e['kind']) for e in newEvidence}
for a in range(0,len(data)-28+1):
 if data[a:a+4]!=b'\x19\x06\x00\x00':continue
 magic,color,flags,w,h,stride,res,size,ptr,storage,handlers=struct.unpack_from('<BBHHHHHIIII',data,a);lo=ptr-runtimeBase
 valid=(magic,color,flags,res,storage,handlers)==(25,6,0,0,0,0) and 0<w<=8192 and 0<h<=8192 and stride==w and size==stride*h and 32<=lo<lo+size<=len(data)
 item={'descriptorPayloadRange':[a,a+28],'descriptorAddress':a+runtimeBase,'fields':{'width':w,'height':h,'stride':stride,'size':size,'pixelPointer':ptr},'accepted':valid,'schemaEvidence':'g2/tools/preserve_l8_resources.py exact28byte LVGL L8 schema'};l8Candidates.append(item)
 if valid:
  if ('apollo_main',(a,a+28),'image_descriptor') not in existingResourceKeys:evidence('apollo_main',a,a+28,'image_descriptor','LVGL L8descriptor@'+hex(a+runtimeBase),'confirmed_data','full payload28byte L8schema validation','complete header/reserved/geometry/pointer consistency; caller/display operation not established',{'format':'LVGL9 L8image descriptor','addressRange':[a+runtimeBase,a+runtimeBase+28],'contentsSummary':f'{w}x{h},stride{stride},pixel buffer{hex(ptr)}'})
  if ('apollo_main',(lo,lo+size),'image') not in existingResourceKeys:evidence('apollo_main',lo,lo+size,'image','L8pixels@'+hex(ptr),'confirmed_data','validated LVGL L8descriptor@'+hex(a+runtimeBase),'format/size/pointer bound by validated image descriptor; semantic icon name/display not inferred',{'format':'raw L8grayscale raster','addressRange':[ptr,ptr+size],'contentsSummary':f'{w}x{h},stride{stride}; raw grayscale, not PNG/JPEG'})

# Initial ARM vector pair: only two validated words, not guessed full vector-table extent.
for cid in ['apollo_main','apollo_bootloader','touch','case']:
 c=next(c for c in compact['components'] if c['id']==cid);sp=c['addressSpaces'][0];off=sp['payloadStart'];stack,reset=struct.unpack_from('<II',payloads[cid],off)
 if 0x20000000<=stack<=0x21000000 and reset&1 and sp['addressStart']<=reset&~1<sp['addressEnd']:evidence(cid,off,off+8,'vector_pair','initial SP/reset vector','confirmed_data','vector pair structure plus canonical address mapping',extra={'stackInitial':stack,'resetEntry':reset&~1,'format':'two little-endian32bit pointers'})
 else:errors.append({'component':cid,'check':'initial vector pair','result':'not accepted','words':[stack,reset]})
# One existing native-executed code-tail contract; classifier is stronger than arbitrary linear decode.
p=R/'g2/analysis/smp-sm-dispatch-tail-20261010/results.json';j=json.loads(p.read_text());start,end=0x56f0ec,0x56f144;off=start-0x437fe0;assert sha(payloads['apollo_main'][32:])==j['raw_sha256'];evidence('apollo_main',off,off+end-start,'native_tested_code_tail','SMP transition dispatcher tail','confirmed_code',str(p.relative_to(R)),'authenticated original tail executed in162bounded comparisons; not hardware proof',{'codeDomain':'Apollo Thumb','format':'machine instructions; literal referenced outside tail'})
# Existing CFG instruction-span table: verify concatenated native byte hashes and exact lengths.
taskRows=[];taskPath=R/'g2/tools/manifests/g2-box-task-entry-bodies.tsv'
import csv
lines=[l for l in taskPath.read_text().splitlines() if l and not l.startswith('#')]
for row in csv.DictReader(lines,delimiter='\t'):
 spans=[];raw=b''
 for token in row['spans'].split(','):
  lo,hi=map(lambda x:int(x,16),token.split('-'));a=lo-0x08000000+32;b=hi-0x08000000+32;assert 0<=a<b<=len(payloads['case']);raw+=payloads['case'][a:b];spans.append([lo,hi])
 assert len(raw)==int(row['instruction_bytes']) and sha(raw)==row['instruction_sha256']
 for lo,hi in spans:evidence('case',lo-0x08000000+32,hi-0x08000000+32,'cfg_reachable_code',row['name'],'confirmed_code',str(taskPath.relative_to(R)),'authenticated existing CFG-reachable instruction spans; not full path/hardware proof',{'codeDomain':'CASE Thumb','format':'reachable decoded instruction bytes, gaps retained'})
 taskRows.append({'entry':int(row['entry'],16),'name':row['name'],'role':row['role'],'instructionBytes':len(raw),'spans':spans,'sha256':sha(raw),'domain':'CASE flash entrypoints; runtime task instances/TCBs/stacks not observed'})
# Recovered LittleFS config geometry fields: read only, no filesystem mount/provider execution.
lfsConfigs=[]
for cid,addr in [('apollo_main',0x6e83a4),('apollo_bootloader',0x431070)]:
 off=addr-(0x437fe0 if cid=='apollo_main' else 0x410000);wanted=[16,256,4096,3008,500,4096,256];observed=list(struct.unpack_from('<7I',payloads[cid],off+20))
 if observed==wanted:
  evidence(cid,off+20,off+48,'configuration_table','LittleFS config geometry fields','confirmed_data','g2/docs/reference/memory-map.md and pinned32bit lfs_config field order','seven independently matching recovered geometry values; leading callback/context pointers not classified by this check',{'addressRange':[addr+20,addr+48],'format':'seven32bit geometry values','contentsSummary':'read16,program256,block4096,count3008,cycles500,cache4096,lookahead256'})
  lfsConfigs.append({'component':cid,'address':addr,'geometryFieldsAddress':[addr+20,addr+48],'values':observed,'validRecoveredGeometry':True})
 else:errors.append({'component':cid,'check':'LittleFS geometry field order','address':addr,'observed':observed,'expected':wanted,'result':'not accepted as data by this check'})

# Validated signature structures, not signature-only assertions. Entire buffers searched at every offset.
def offsets(b,s):
 pos=0
 while True:
  a=b.find(s,pos)
  if a<0:return
  yield a;pos=a+1
def png(b,a):
 pos=a+8;chunks=0;dims=None;seenIDAT=False
 while pos+12<=len(b) and pos-a<16*1024*1024 and chunks<4096:
  n=struct.unpack_from('>I',b,pos)[0];typ=b[pos+4:pos+8];end=pos+12+n
  if n>16*1024*1024 or end>len(b) or binascii.crc32(typ+b[pos+8:pos+8+n])&0xffffffff!=struct.unpack_from('>I',b,pos+8+n)[0]:return None
  if chunks==0:
   if typ!=b'IHDR' or n!=13:return None
   w,h,depth,color,comp,filt,inter=struct.unpack('>IIBBBBB',b[pos+8:pos+21]);
   if not 0<w<=32768 or not 0<h<=32768 or comp!=0 or filt!=0 or inter not in [0,1]:return None
   dims=[w,h,depth,color]
  if typ==b'IDAT':seenIDAT=True
  chunks+=1;pos=end
  if typ==b'IEND':return (pos,{'dimensions':dims,'chunks':chunks}) if n==0 and seenIDAT else None
 return None
def sfnt(b,a):
 if a+12>len(b):return None
 num,search,selector,shift=struct.unpack_from('>HHHH',b,a+4)
 if not 1<=num<=128 or a+12+16*num>len(b):return None
 power=1<<(num.bit_length()-1)
 if search!=16*power or selector!=power.bit_length()-1 or shift!=num*16-search:return None
 tables={};end=a+12+num*16
 for i in range(num):
  tag,ck,off,n=struct.unpack_from('>4sIII',b,a+12+i*16)
  if not all(32<=x<127 for x in tag) or tag in tables or n==0 or off<12+num*16 or a+off+n>len(b):return None
  tables[tag]=(off,n);end=max(end,a+off+n)
 if not {b'head',b'maxp',b'cmap'}<=tables.keys() or not (b'glyf' in tables or b'CFF ' in tables or b'CFF2' in tables):return None
 off,n=tables[b'head']
 if n<54 or struct.unpack_from('>I',b,a+off+12)[0]!=0x5f0f3cf5:return None
 return end,{'tableCount':num,'tags':[t.decode() for t in tables]}
for cid,data in payloads.items():
 report={'component':cid,'bytesVisited':len(data),'sha256':sha(data),'signatures':{},'asciiCandidateCount':0,'entropyWindows':[]}
 for kind,sig,validator in [('PNG',b'\x89PNG\r\n\x1a\n',png),('sfnt-TrueType',b'\x00\x01\x00\x00',sfnt),('sfnt-OpenType',b'OTTO',sfnt)]:
  starts=list(offsets(data,sig));valid=0
  for a in starts:
   hit=validator(data,a)
   if hit:
    b,detail=hit;valid+=1;evidence(cid,a,b,'font' if kind.startswith('sfnt') else 'image',kind+'container','confirmed_data','new validated signature scan',extra={'format':kind,'details':detail})
  report['signatures'][kind]={'candidates':len(starts),'structureAccepted':valid,'rejected':len(starts)-valid}
 starts=list(offsets(data,b'\x1f\x8b\x08'));valid=0
 for a in starts:
  try:
   decoder=zlib.decompressobj(31);out=decoder.decompress(data[a:],8*1024*1024+1)
   if not decoder.eof or len(out)>8*1024*1024:continue
   used=len(data)-a-len(decoder.unused_data);valid+=1;evidence(cid,a,a+used,'compressed_container','gzip member','confirmed_data','gzip header/deflate/CRC/ISIZE parser',extra={'format':'gzip','decodedBytes':len(out),'decodedSha256':sha(out),'decodedContentsType':'unclassified; no code/data assertion'})
  except zlib.error:pass
 report['signatures']['gzip']={'candidates':len(starts),'structureAccepted':valid}
 for m in re.finditer(rb'[\x20-\x7e]{16,}\x00',data):
  report['asciiCandidateCount']+=1;candidates.append({'component':cid,'payloadRange':[m.start(),m.end()],'kind':'possible_ascii_string','contentsPreview':'[sensitive-label preview omitted]' if re.search(rb'(?i)bearer|api[_ -]?key|secret|password|credential',m.group()) else m.group()[:-1][:100].decode('ascii'),'classification':'suspected only; byte pattern does not prove noncode/file','sha256':sha(m.group())})
 report['littlefsMagicOccurrences']=[a for a in offsets(data,b'littlefs')];report['littlefsParse']='not mounted or files inferred: observed magic/strings alone insufficient, target external NOR not in OTA'
 for a in range(0,len(data),4096):
  b=data[a:a+4096];counts=collections.Counter(b);entropy=-sum((n/len(b))*math.log2(n/len(b)) for n in counts.values());report['entropyWindows'].append([a,a+len(b),round(entropy,3),counts[0],counts[255]])
 scanReports.append(report)
# Scan decoded initializer images in their own coordinate domains; never add decoded byte counts to bundle.
decodedScans=[]
for record in ram:
 im=IM[record['id']];data=(R/im['content_path']).read_bytes();entry={'id':record['id'],'coordinate':'decoded-only RAM/ITCM offsets','bytesVisited':len(data),'sha256':sha(data),'validatedStructures':[],'signatureCandidateCounts':{}}
 for kind,sig,validator in [('PNG',b'\x89PNG\r\n\x1a\n',png),('sfnt-TrueType',b'\x00\x01\x00\x00',sfnt),('sfnt-OpenType',b'OTTO',sfnt)]:
  points=list(offsets(data,sig));entry['signatureCandidateCounts'][kind]=len(points)
  for a in points:
   hit=validator(data,a)
   if hit:entry['validatedStructures'].append({'decodedRange':[a,hit[0]],'type':kind,'details':hit[1],'classification':'decoded resource; exact compressed-byte backmapping unavailable'})
 entry['possibleAsciiNulStrings']=sum(1 for _ in re.finditer(rb'[\x20-\x7e]{16,}\x00',data));decodedScans.append(entry)

# Build exclusive classifications; retain all evidence overlaps separately.
CATEGORIES=['confirmed_code','confirmed_data','suspected','unknown'];componentRuns=[];globalRuns=[]
for c in compact['components']:
 cid=c['id'];n=len(payloads[cid]);events={0:[],n:[]};claims=[]
 for e in newEvidence:
  if e['component']==cid:claims.append({'range':e['payloadRange'],'category':e['exclusiveClaim'],'kind':e['kind'],'evidence':e['evidence']})
 for a,b,mask in c['runs']:
  if mask&((1<<0)|(1<<1)|(1<<2)|(1<<3)|(1<<4)|(1<<8)):claims.append({'range':[a,b],'category':'suspected','kind':'possible_code_or_candidate_correspondence','evidence':'preserved orthogonal dashboard stages, not code/data classifier'})
 for e in candidates:
  if e['component']==cid:claims.append({'range':e['payloadRange'],'category':'suspected','kind':e['kind'],'evidence':'new printable/NUL candidate scan'})
 for i,e in enumerate(claims):
  a,b=e['range'];events.setdefault(a,[]).append((i,1));events.setdefault(b,[]).append((i,-1))
 active=set();runs=[];points=sorted(events)
 for ix,a in enumerate(points[:-1]):
  for i,d in events[a]:
   if d==1:active.add(i)
   else:active.remove(i)
  b=points[ix+1];cats={claims[i]['category'] for i in active};cat='confirmed_data' if 'confirmed_data' in cats else 'confirmed_code' if 'confirmed_code' in cats else 'suspected' if 'suspected' in cats else 'unknown'
  if 'confirmed_code' in cats and 'confirmed_data' in cats:conflicts.append({'component':cid,'range':[a,b],'kind':'contradictory confirmed classification','claimIndices':sorted(active)});cat='suspected'
  elif 'confirmed_data' in cats and 'suspected' in cats:conflicts.append({'component':cid,'range':[a,b],'kind':'confirmed resource/data overlaps possible code/string/function envelope','claimIndices':sorted(active)})
  code=CATEGORIES.index(cat)
  if runs and runs[-1][1]==a and runs[-1][2]==code:runs[-1][1]=b
  else:runs.append([a,b,code])
 totals={cat:sum(b-a for a,b,k in runs if k==i) for i,cat in enumerate(CATEGORIES)};assert sum(totals.values())==n;assert runs[0][0]==0 and runs[-1][1]==n and all(a[1]==b[0] for a,b in zip(runs,runs[1:]));componentRuns.append({'component':cid,'bytes':n,'runs':runs,'totals':totals,'claims':claims})
 seg=next(s for s in segments if s.get('component')==cid);off=seg['range'][0];globalRuns += [[off+a,off+b,k] for a,b,k in runs]
for seg in segments:
 if seg['classification']=='confirmed_data':globalRuns.append([seg['range'][0],seg['range'][1],1])
globalRuns.sort();assert globalRuns[0][0]==0 and globalRuns[-1][1]==len(bundle) and all(a[1]==b[0] for a,b in zip(globalRuns,globalRuns[1:]));globalTotals={cat:sum(b-a for a,b,k in globalRuns if k==i) for i,cat in enumerate(CATEGORIES)};assert sum(globalTotals.values())==len(bundle);assert sum(len(p) for p in payloads.values())+944==len(bundle)
fs={'chipDomain':'Apollo external MSPI1 NOR','norOffsetRange':[0,0x2000000],'xipBase':0x80000000,'coordinate':'external chip offsets, not bundle bytes','partitionRanges':[{'range':[0,0x1400000],'name':'uncharacterized20MiB','contentState':'not supplied in locked OTA'},{'range':[0x1400000,0x1fc0000],'name':'LittleFS','blockSize':4096,'blockCount':3008,'readSize':16,'programSize':256,'contentState':'configured geometry only; authenticated partition content unavailable'},{'range':[0x1fc0000,0x1ff8000],'name':'FlashDB sysenv kvdb','contentState':'partition config only'},{'range':[0x1ff8000,0x2000000],'name':'FlashDB factory NVdb','contentState':'partition config only'}],'evidence':'g2/docs/reference/memory-map.md','filesIdentified':0,'filesCountMeaning':'none parsable from supplied OTA; not assertion filesystem empty'}
result={'tools':{'python':sys.version,'zlibRuntime':zlib.ZLIB_RUNTIME_VERSION,'officialContainerValidatorSha256':sha((R/'g2/tools/open_cfw.py').read_bytes()),'scannerSha256':sha(Path(__file__).read_bytes())},'schema':'opencfw-bundle-accounting-v3','asOfUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':T['target_id'],'version':'s200_v2.2.6.10','bundle':{'filename':T['bundle']['verified_local_path'],'bytes':len(bundle),'sha256':sha(bundle),'categories':CATEGORIES,'segments':segments,'exclusiveRuns':globalRuns,'exclusiveTotals':globalTotals,'overheadBytes':944,'componentPayloadBytes':sum(map(len,payloads.values()))},'componentsExclusive':componentRuns,'orthogonalResourceEvidence':newEvidence,'lvglL8FullScan':{'candidateCount':len(l8Candidates),'acceptedCount':sum(x['accepted'] for x in l8Candidates),'candidates':l8Candidates},'signatureScans':scanReports,'unclassifiedStringCandidates':candidates,'runtimeImages':ram,'decodedImageSignatureScans':decodedScans,'externalFilesystemEvidence':fs,'littlefsConfigCorrelations':lfsConfigs,'runtimeTaskEntrypoints':taskRows,'runtimeHeapEvidence':{'chipDomain':'Apollo RAM','documentedConfigTotalHeapSize':0x2f000,'baseAddress':None,'evidence':'g2/docs/reference/memory-map.md','qualification':'configured heap size, no authenticated live heap snapshot; not flash bytes'},'runtimeTableLeads':[{'chipDomain':'Apollo RAM','address':0x20066230,'label':'UI module registry copy','reportedRows':43,'flashSourceStart':0x6a44b0,'byteLength':None,'qualification':'documented table lead; missing row-width/complete original-byte ownership join'},{'chipDomain':'Apollo RAM','range':[0x2004fac8,0x200523c8],'label':'Cordio WSF buffer pools','evidence':'g2/docs/reference/memory-map.md','qualification':'runtime RAM allocation/pool region, not extra update bytes'}],'classificationConflicts':conflicts,'scanErrorsAndRejectedChecks':errors,'checksums':checksum,'preservedDashboard':compact,'limits':['Every supplied bundle byte accounted/scanned, not semantically understood.','suspected includes possible code/function envelopes and plausible data; not confirmed code.','confirmed_code here includes a selected native-tested88byte tail and hash-verified CASE CFG spans; GXNPU program stays suspected until its format is resolved; no global CPU code classifier.','Resource overlap does not silently invalidate original decompiler/disassembly work.','External NOR capacity/config are documented; content bytes absent, not counted in bundle.','Decoded RAM and heaps/tasks are separate domains; no inflated flash denominator.','No padding inferred from zeros/FF/entropy.','Signature scan currently validates PNG/sfnt/gzip structures; not an exhaustive universal file recognizer.']}
(O/'full-accounting.json').write_text(json.dumps(result,separators=(',',':')));(O/'validation.json').write_text(json.dumps({'pass':True,'bundleBytes':len(bundle),'componentBytes':sum(map(len,payloads.values())),'overheadBytes':944,'crc32cAllSixValid':all(x['valid'] for x in checksum),'exclusiveBundleTotals':globalTotals,'exclusiveComponentPartitionsSumExactly':True,'bundlePartitionNoGapsOrOverlaps':True,'payloadHashesVerified':True,'runtimeImageHashesVerified':True,'conflictCount':len(conflicts),'confirmedConflictCount':sum(x['kind']=='contradictory confirmed classification' for x in conflicts),'scannedPayloadBytes':sum(x['bytesVisited'] for x in scanReports),'rawByteScanCoveragePercent':100,'semanticUnderstoodPercent':None},indent=2)+'\n');print((O/'validation.json').read_text());print('signature outcomes',[(x['component'],x['signatures'],x['asciiCandidateCount']) for x in scanReports])
