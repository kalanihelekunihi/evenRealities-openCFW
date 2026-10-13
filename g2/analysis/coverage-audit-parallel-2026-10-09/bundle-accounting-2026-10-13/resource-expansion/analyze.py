from pathlib import Path
import json,hashlib,struct,re,zlib,collections
R=Path.cwd();O=Path(__file__).parent;B=O.parent;sha=lambda b:hashlib.sha256(b).hexdigest();inputs={};errors=[]
def read(p):
 p=Path(p);p=p if p.is_absolute() else R/p;b=p.read_bytes();inputs[str(p.relative_to(R))]=sha(b);return b
def load(p):return json.loads(read(p))
j=load(B/'full-accounting.json');v3=load(B/'full-v3.json');manifest=load('g2/manifests/g2-2.2.6.10.json');payload={c['name']:read('g2/'+c['provider']['path']) for c in manifest['components']}
for c in manifest['components']:assert sha(payload[c['name']])==c['provider']['sha256']
bundle=read(j['bundle']['filename']);assert sha(bundle)==j['bundle']['sha256']
# Read the complete declared baseline evidence set; immutable file hashes record actual snapshot.
for p in sorted(B.glob('*')):
 if p.is_file():read(p)
for p in ['AGENTS.md','g2/workflow/README.md','g2/workflow/PROCEDURE.md','g2/workflow/CONTRACTS.md','docs/tooling.md','g2/docs/reference/memory-map.md','g2/docs/reference/libraries.md','g2/config-recovered/lvgl/g2-config/lvgl_g2_abi.json','third-party/upstream/lvgl/src/font/lv_font_fmt_txt.h','third-party/upstream/lvgl/src/draw/lv_image_dsc.h','third-party/tools/rea/skill-src/reverse-engineer-anything/SKILL.md','g2/analysis/coverage-audit-parallel-2026-10-09/dashboard-expanded-2026-10-13/resource-evidence.json']:read(p)
for x in j['orthogonalResourceEvidence']:
 p=x['evidence']
 if isinstance(p,str) and (R/p).is_file():read(p)
# All prior noncode resources: retain fields, add transport/address mappings. Never alter partition.
translations={s['component']:s['range'][0] for s in j['bundle']['segments'] if s.get('component')}
spaces={c['id']:c['addressSpaces'] for c in j['preservedDashboard']['components']};resources=[]
for x in j['orthogonalResourceEvidence']:
 if x['kind'] in ('cfg_reachable_code','native_tested_code_tail','accelerator_command_stream'):continue
 x=dict(x);cid=x['component'];a,b=x['payloadRange'];assert sha(payload[cid][a:b])==x['sha256'];x['bundleRange']=[a+translations[cid],b+translations[cid]];x['length']=b-a;x['payloadSha256']=sha(payload[cid]);x['addressMappings']=[]
 for s in spaces[cid]:
  if s['payloadStart']<=a<b<=s['payloadEnd']:x['addressMappings'].append({'space':s['id'],'kind':s['kind'],'range':[s['addressStart']+a-s['payloadStart'],s['addressStart']+b-s['payloadStart']]})
 resources.append(x)
# LE aligned pointer occurrences are xref candidates; without CFG they are not consumer proof.
data=payload['apollo_main'];base=0x437fe0;pointers=collections.defaultdict(list)
for a in range(0,len(data)-3,4):pointers[struct.unpack_from('<I',data,a)[0]].append(a)
images=[]
for c in j['lvglL8FullScan']['candidates']:
 if not c['accepted']:continue
 d0,d1=c['descriptorPayloadRange'];f=c['fields'];p0=f['pixelPointer']-base;p1=p0+f['size'];assert struct.unpack_from('<BBHHHHHIIII',data,d0)==(25,6,0,f['width'],f['height'],f['stride'],0,f['size'],f['pixelPointer'],0,0)
 refs=pointers[c['descriptorAddress']];images.append({'id':f'l8-{c["descriptorAddress"]:08x}','descriptorPayloadRange':[d0,d1],'descriptorBundleRange':[d0+translations['apollo_main'],d1+translations['apollo_main']],'descriptorAddress':c['descriptorAddress'],'pixelPayloadRange':[p0,p1],'pixelBundleRange':[p0+translations['apollo_main'],p1+translations['apollo_main']],'pixelAddressRange':[base+p0,base+p1],'width':f['width'],'height':f['height'],'stride':f['stride'],'pixelFormat':'L8 unsigned 8-bit grayscale','pixelSha256':sha(data[p0:p1]),'descriptorSha256':sha(data[d0:d1]),'pointerReferenceCandidates':[{'payloadOffset':a,'bundleOffset':a+translations['apollo_main'],'address':base+a} for a in refs],'consumerStatus':'aligned pointer references only; instruction/literal/table ownership unresolved','semanticContent':'uninspected','confidence':'confirmed layout and bounds; semantic identity unknown'})
# finite custom-font hypothesis: 20-byte little-endian descriptor, short enums, inline small glyphs.
font=[];tested=0
for a in range(0,len(data)-20,4):
 tested+=1;bm,gd,cm,kern,scale,bits=struct.unpack_from('<IIIIHH',data,a);count=bits&511;bpp=(bits>>9)&15;fmt=bits>>14
 if not(1<=count<=16 and bpp in (1,2,3,4,8) and fmt in (0,3) and all(base<=p<base+len(data) for p in (bm,gd,cm)) and (kern==0 or base<=kern<base+len(data))):continue
 cmoff=cm-base;maps=[];ok=True
 for i in range(count):
  off=cmoff+i*20
  if off+20>len(data):ok=False;break
  start,n,gid,ul,gl,ll,typ,pad=struct.unpack_from('<IHHIIHBB',data,off)
  if not(0<start<=0x10ffff and n>0 and start+n<=0x110000 and gid>0 and typ<=3 and (ul==0 or base<=ul<base+len(data)) and (gl==0 or base<=gl<base+len(data))):ok=False;break
  if typ==2 and (ul or gl or ll):ok=False;break
  maps.append({'unicodeRange':[start,start+n],'glyphIdStart':gid,'type':typ,'listLength':ll})
 if ok:font.append({'payloadRange':[a,a+20],'address':base+a,'sha256':sha(data[a:a+20]),'bitmapPointer':bm,'glyphDescriptorPointer':gd,'cmapsPointer':cm,'bpp':bpp,'format':fmt,'cmaps':maps,'classification':'suspected; ABI hypothesis and missing proven consumer/full glyph extents prevent promotion'})
# Existing strings are candidates only; collect font/path/config references without semantic inflation.
texts=[]
for x in j['unclassifiedStringCandidates']:
 a,b=x['payloadRange'];raw=payload[x['component']][a:b]
 if re.search(rb'(?i)\.(?:ttf|otf|bmp|png|bin|json|cfg)|font|littlefs|sysenv|nvdb',raw):
  row=dict(x);row['encoding']='ASCII NUL terminated byte pattern';row['bundleRange']=[a+translations[x['component']],b+translations[x['component']]];texts.append(row)
# Render 24 evenly spaced descriptors as contact sheet, PGM samples exact and PNG via zlib only.
def png(w,h,pixels):
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pixels[y*w:(y+1)*w] for y in range(h))))+chunk(b'IEND',b'')
selected=[images[round(i*(len(images)-1)/23)] for i in range(24)];W=768;H=512;canvas=bytearray([80])*(W*H);samples=[]
for index,x in enumerate(selected):
 a,b=x['pixelPayloadRange'];raw=data[a:b];name=x['id']+'.pgm';pgm=f'P5\n{x["width"]} {x["height"]}\n255\n'.encode()+raw;(O/name).write_bytes(pgm);x['samplePath']=str((O/name).relative_to(R));samples.append({'index':index,'id':x['id'],'samplePath':x['samplePath'],'sha256':sha(pgm),'pixelSha256':sha(raw)})
 w,h=x['width'],x['height'];scale=min(120/w,120/h);dw=max(1,int(w*scale));dh=max(1,int(h*scale));ox=(index%6)*128+(128-dw)//2;oy=(index//6)*128+(128-dh)//2
 for y in range(dh):
  for xx in range(dw):canvas[(oy+y)*W+ox+xx]=raw[min(h-1,int(y/scale))*w+min(w-1,int(xx/scale))]
(O/'contact-sheet.png').write_bytes(png(W,H,canvas));
result={'schema':'opencfw-resource-expansion-v1','bundle':{'bytes':len(bundle),'sha256':sha(bundle)},'baselineExclusiveTotals':j['bundle']['exclusiveTotals'],'partitionPolicy':'unchanged baseline; resource overlays never add byte counts','resources':resources,'images':images,'customFontCandidates':font,'textPathCandidates':texts,'compressedResources':j['runtimeImages'],'externalStorage':j['externalFilesystemEvidence'],'preservedConflicts':j['classificationConflicts'],'coverage':{'baselineDeclaredFilesRead':len(list(B.glob('*.*'))),'baselineResourcesValidated':len(resources),'L8DescriptorsRevalidated':len(images),'newFontHypothesisAlignedOffsetsTested':tested,'fontHypothesis':'20-byte LVGL fmt_txt descriptor / 20-byte short-enum cmap; large glyph ABI and other fonts not covered','fontCandidatesAcceptedAsConfirmed':0,'imageSamplesRendered':len(samples),'semanticInspectionPending':True},'samples':samples,'provenanceHashes':inputs,'errors':errors,'providerAvailability':'no advertised Ghidra-MCP or REA tool; prior outputs reused; no installation/network diagnostic','exportStatus':'local only; predecessor exact Library upload remains denied pending owner approval'}
(O/'resources-full.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
compact={k:result[k] for k in ('schema','bundle','baselineExclusiveTotals','partitionPolicy','coverage','externalStorage','exportStatus')};compact['imageSummary']={'count':len(images),'dimensions':dict(collections.Counter(f'{x["width"]}x{x["height"]}' for x in images)),'pointerReferencedDescriptors':sum(bool(x['pointerReferenceCandidates']) for x in images),'sampleManifest':samples};compact['resourceKinds']=dict(collections.Counter(x['kind'] for x in resources));compact['fontCandidates']=font;compact['textPathCandidates']=texts;compact['fullEvidencePath']=str((O/'resources-full.json').relative_to(R));(O/'dashboard-resources.json').write_text(json.dumps(compact,separators=(',',':'))+'\n')
print(json.dumps(compact['coverage']));print('font candidates',len(font),'text leads',len(texts),'compact bytes',(O/'dashboard-resources.json').stat().st_size)
