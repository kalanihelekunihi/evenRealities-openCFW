from pathlib import Path
import json,struct,re,hashlib,zlib
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();j=json.loads((O/'resources-full.json').read_text());m=json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text());main=(R/'g2'/next(c for c in m['components'] if c['name']=='apollo_main')['provider']['path']).read_bytes();base=0x437fe0;IM=[json.loads(l) for l in (R/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines()];ev={};domains=[{'id':'apollo_main:flash','data':main,'loadedBase':base}];decoded=[]
for im in IM:
 if 'decoded:' not in im['id'] and 'ram-' not in im['id']:continue
 p=Path(im['content_path']);p=p if p.is_absolute() else R/p;b=p.read_bytes();assert sha(b)==im['content_sha256'];ev[str(p.relative_to(R))]=sha(b);maps=im['address_spaces'][0]['mappings'];assert len(maps)==1;domains.append({'id':im['id'],'data':b,'loadedBase':maps[0]['loaded_start']});strings=[]
 for match in re.finditer(rb'[\x20-\x7e]{8,}\0',b):
  if re.search(rb'(?i)password|secret|credential|bearer|api[_ -]?key',match.group()):text='[sensitive preview omitted]'
  else:text=match.group()[:-1].decode('ascii')
  strings.append({'decodedRange':[match.start(),match.end()],'loadedRange':[maps[0]['loaded_start']+match.start(),maps[0]['loaded_start']+match.end()],'encoding':'ASCII NUL byte-pattern candidate','text':text,'sha256':sha(match.group()),'classification':'suspected decoded string, instruction/literal ownership not proven'})
 decoded.append({'id':im['id'],'bytes':len(b),'sha256':sha(b),'asciiCandidates':strings,'sourceDomain':'canonical initialized/decoded RAM; no flash 1:1 backmapping','parsedFilesystemFiles':0})
# Hash-check every disassembled instruction byte in the 3 ABI-consumer functions against locked original.
p=R/'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt';ev[str(p.relative_to(R))]=sha(p.read_bytes());lines=p.read_text().splitlines();tiles=[]
for a,b,label in [(0x4b239c,0x4b2690,'bitmap callback'),(0x4b26a4,0x4b2774,'glyph descriptor callback'),(0x4b2774,0x4b28ee,'cmap resolver')]:
 found={}
 for line in lines:
  mt=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}(?:\s+|$))+)',line)
  if not mt:continue
  addr=int(mt[1],16)
  if not a<=addr<b:continue
  bs=b''.join(struct.pack('<H',int(h,16)) for h in mt[2].split());assert main[addr-base:addr-base+len(bs)]==bs
  for k,v in enumerate(bs):found[addr+k]=v
 assert sorted(found)==list(range(a,b));tiles.append({'addressRange':[a,b],'payloadRange':[a-base,b-base],'sha256':sha(main[a-base:b-base]),'instructionBytesChecked':b-a,'description':label})
for p in ['third-party/upstream/lvgl/src/font/lv_font.h','third-party/upstream/lvgl/src/font/lv_font_fmt_txt.h','third-party/upstream/lvgl/src/font/lv_font_fmt_txt.c','g2/components/audio/uart_thread_source_candidate/display_font_glyph_descriptor.c','g2/components/audio/uart_thread_source_candidate/display_font_glyph_index.c','g2/build/pseudocode-first/20260930T190500Z/reviews/P2-25143-independent-review/001/review.md','g2/build/pseudocode-first/20260930T190500Z/reviews/P2-25153-independent-review/001/review.md']:ev[p]=sha((R/p).read_bytes())
paletteAddress=struct.unpack_from('<I',main,0x4b2694-base)[0];assert paletteAddress==0x786950;assert main[paletteAddress-base:paletteAddress-base+16]==bytes(range(0,256,17))
rootcount=0
for f in j['customFontCandidates']:
 roots=[]
 for d in domains:
  b=d['data'];needle=struct.pack('<I',f['address']);start=0
  while True:
   ptr=b.find(needle,start)
   if ptr<0:break
   start=ptr+1;r=ptr-24
   if r<0 or r+36>len(b):continue
   dsc,bitmap,release,height,baseline=struct.unpack_from('<IIIii',b,r)
   if (dsc,bitmap,release)!=(0x4b26a5,0x4b239d,0) or not 1<=height<=256:continue
   roots.append({'domain':d['id'],'range':[r,r+36],'loadedRange':[d['loadedBase']+r,d['loadedBase']+r+36],'sha256':sha(b[r:r+36]),'getGlyphDescriptorThumb':dsc,'getBitmapThumb':bitmap,'descriptorAddress':f['address'],'lineHeight':height,'baseline':baseline,'format':'36-byte lv_font_t; dsc@24, callbacks@0,4','confidence':'exact original static/decoded struct and hash-verified consumer ABI'})
 f['fontRootRecords']=roots;rootcount+=len(roots);f['consumerStatus']='static font roots reference exact callbacks; ABI corroborated against original instructions' if roots else 'no static/decoded font root found; coherent typed resource only';f['bitmapEncoding']='4-bit high nibble first; aligned stock row stride floor(width/2)+1' if f['format']==3 else '4-bit high nibble first continuous packed stream';f['classification']='corroborated custom font data; orthogonal overlay, exclusive baseline unchanged' if roots else 'strong structural font data candidate; root/consumer join unavailable';f['abiEvidence']={'glyphRecordBytes':16,'cmapRecordBytes':20,'descriptorModeOffset':18,'bppBits':[9,13],'formatBits':[14,16],'fontDescriptorOffset':24,'consumerTiles':tiles}
j['decodedResourceExpansion']=decoded;j['fontConsumerEvidence']={'tiles':tiles,'opacityPalette':{'addressRange':[paletteAddress,paletteAddress+16],'payloadRange':[paletteAddress-base,paletteAddress-base+16],'sha256':sha(main[paletteAddress-base:paletteAddress-base+16]),'contents':'16 unsigned alpha values 0,17,...255; bound by callback literal at 0x4B2694'},'sourceHashes':ev,'fontRootCount':rootcount,'staticAndDecodedDomainsScanned':len(domains),'qualification':'all 11 roots bind callbacks statically; no live rendering or calling UI proven; decoded coordinates have no compressed byte backmapping','rowStrideCorrection':'stock 4-bit loop leaves i nonzero at row exit even for even widths, then advances pointer: floor(width/2)+1','cmapCorrection':'FORMAT0_FULL offset zero is absent except relative codepoint zero'};j['provenanceHashes'].update(ev);j['coverage']['fontResourceChainsCorroborated']=11;j['coverage']['fontCandidatesAcceptedAsConfirmed']=0;j['coverage']['fontHypothesis']='32-bit/short-enum fmt_txt ABI corroborated: 20-byte descriptor, 20-byte cmap, 16-byte LARGE glyph; other font layouts outside scope';j['coverage']['fontRootRecordsValidated']=rootcount;j['coverage']['fontChainsWithConsumerJoin']=sum(bool(f['fontRootRecords']) for f in j['customFontCandidates']);j['coverage']['decodedDomainsScanned']=len(decoded);j['coverage']['decodedBytesScanned']=sum(d['bytes'] for d in decoded);j['coverage']['decodedAsciiCandidates']=sum(len(d['asciiCandidates']) for d in decoded);(O/'resources-full.json').write_text(json.dumps(j,separators=(',',':'))+'\n');c=json.loads((O/'dashboard-resources.json').read_text());c['coverage']=j['coverage'];c['fontCandidates']=j['customFontCandidates'];c['decodedSummary']=[{'id':d['id'],'bytes':d['bytes'],'asciiCandidateCount':len(d['asciiCandidates'])} for d in decoded];c['fontConsumerEvidence']=j['fontConsumerEvidence'];(O/'dashboard-resources.json').write_text(json.dumps(c,separators=(',',':'))+'\n');print('roots',rootcount,[(hex(f['address']),[(r['domain'],hex(r['loadedRange'][0])) for r in f['fontRootRecords']]) for f in j['customFontCandidates']]);print('decoded',j['coverage']['decodedBytesScanned'],j['coverage']['decodedAsciiCandidates'])
# Build a numbered-by-manifest enlarged font sample sheet, all generated glyph PNGs (filter-zero own encoder).
W,H=640,512;canvas=bytearray([64])*(W*H);manifest=[]
for index,s in enumerate(s for f in j['customFontCandidates'] for s in f['samples']):
 b=(R/s['file']).read_bytes();p=8;compressed=b''
 while p<len(b):
  n=struct.unpack_from('>I',b,p)[0];typ=b[p+4:p+8];body=b[p+8:p+8+n]
  if typ==b'IHDR':w,h=struct.unpack_from('>II',body)
  if typ==b'IDAT':compressed+=body
  p+=12+n
 raw=zlib.decompress(compressed);pix=b''.join(raw[y*(w+1)+1:(y+1)*(w+1)] for y in range(h));scale=min(112/w,112/h);dw=int(w*scale);dh=int(h*scale);ox=(index%5)*128+(128-dw)//2;oy=(index//5)*128+(128-dh)//2
 for y in range(dh):
  for x in range(dw):canvas[(oy+y)*W+ox+x]=pix[min(h-1,int(y/scale))*w+min(w-1,int(x/scale))]
 manifest.append({'index':index,'file':s['file'],'codepoint':s['codepoint'],'width':w,'height':h})
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(O/'glyph-contact-sheet.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+canvas[y*W:(y+1)*W] for y in range(H))))+chunk(b'IEND',b''));(O/'glyph-sheet-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
