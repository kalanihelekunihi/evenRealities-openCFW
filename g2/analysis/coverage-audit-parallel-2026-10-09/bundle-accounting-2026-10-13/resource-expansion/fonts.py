from pathlib import Path
import json,struct,hashlib,zlib
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();j=json.loads((O/'resources-full.json').read_text());m=json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text());data=(R/'g2'/next(c for c in m['components'] if c['name']=='apollo_main')['provider']['path']).read_bytes();base=0x437fe0;trans=j['images'][0]['pixelBundleRange'][0]-j['images'][0]['pixelPayloadRange'][0];results=[]
def span(a,b,kind):
 assert 0<=a<=b<=len(data)
 return {'payloadRange':[a,b],'bundleRange':[a+trans,b+trans],'addressRange':[base+a,base+b],'length':b-a,'sha256':sha(data[a:b]),'kind':kind}
def png(w,h,pixels):
 def c(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+c(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0,0,0,0))+c(b'IDAT',zlib.compress(b''.join(b'\0'+pixels[y*w:(y+1)*w] for y in range(h))))+c(b'IEND',b'')
for f in j['customFontCandidates']:
 f=dict(f);mapped={};spans=[span(*f['payloadRange'],'font_descriptor')];cm=f['cmapsPointer']-base;spans.append(span(cm,cm+20*len(f['cmaps']),'cmaps'))
 try:
  for i,x in enumerate(f['cmaps']):
   start,n,gid,ul,gl,ll,typ,pad=struct.unpack_from('<IHHIIHBB',data,cm+i*20);assert pad==0
   if typ in (1,3):
    assert ul and ll>0 and ul-base+2*ll<=len(data);u=list(struct.unpack_from('<'+'H'*ll,data,ul-base));assert u==sorted(set(u)) and u[-1]<n;spans.append(span(ul-base,ul-base+ll*2,'unicode_relative_list'));rcps=u
   else:assert ul==0;rcps=list(range(n))
   if typ in (0,1):
    assert gl;sz=1 if typ==0 else 2;assert gl-base+sz*len(rcps)<=len(data);ofs=list(data[gl-base:gl-base+len(rcps)]) if sz==1 else list(struct.unpack_from('<'+'H'*len(rcps),data,gl-base));spans.append(span(gl-base,gl-base+sz*len(rcps),'glyph_offsets'))
   else:assert gl==0;ofs=list(range(len(rcps)))
   for r,o in zip(rcps,ofs):
    if typ==0 and o==0 and r!=0:continue
    assert start+r not in mapped;mapped[start+r]=gid+o
  maxid=max(mapped.values());gd=f['glyphDescriptorPointer']-base;bm=f['bitmapPointer']-base;assert gd+(maxid+1)*16<=len(data);glyphs=[struct.unpack_from('<IIHHhh',data,gd+i*16) for i in range(maxid+1)];assert glyphs[0]==(0,0,0,0,0,0);last=0;end=0
  for idx,advance,w,h,x,y in glyphs:
   assert idx>=last and w<=256 and h<=256 and advance<=65536;size=(w//2+1)*h if f['format']==3 else (w*h*f['bpp']+7)//8;assert bm+idx+size<=len(data);last=idx;end=max(end,idx+size)
  spans.extend([span(gd,gd+(maxid+1)*16,'large_glyph_descriptors'),span(bm,bm+end,'bounded_glyph_bitmap_store')]);f.update({'structuralValidation':'all cmap lists, Unicode/glyph bounds, reserved zero glyph, monotone bitmap indices and bounded 16-byte large glyph records pass','glyphCountIncludingReserved':maxid+1,'mappedCodepointCount':len(mapped),'codepoints':sorted(mapped),'validatedSpans':spans,'glyphLayout':'LV_FONT_FMT_TXT_LARGE=1, <IIHHhh, 16 bytes','bitmapEncoding':'4-bit grayscale; byte-aligned rows' if f['format']==3 else '4-bit grayscale; continuous packed bits','consumerStatus':'static descriptor pointer candidates; no independent CFG consumer validation','classification':'strongly supported custom font resource; kept suspected pending consumer/ABI corroboration; no exclusive partition promotion'})
  refs=[];needle=struct.pack('<I',f['address'])
  for a in range(0,len(data)-3,4):
   if data[a:a+4]==needle:refs.append({'payloadOffset':a,'address':a+base,'bundleOffset':a+trans})
  f['pointerReferenceCandidates']=refs;samplecodes=[c for c in (65,48,63,0x1f600) if c in mapped] or [c for c in sorted(mapped) if glyphs[mapped[c]][2]>0][:1];samples=[]
  for cp in samplecodes:
   idx,adv,w,h,x,y=glyphs[mapped[cp]]
   if not w*h:continue
   raw=data[bm+idx:];pix=bytearray(w*h)
   for yy in range(h):
    for xx in range(w):
     bit=yy*(w//2+1)*8+xx*4 if f['format']==3 else (yy*w+xx)*4;pix[yy*w+xx]=((raw[bit//8]>>(4 if bit%8==0 else 0))&15)*17
   name=f'font-{f["address"]:08x}-u{cp:06x}.png';(O/name).write_bytes(png(w,h,pix));samples.append({'codepoint':cp,'glyphId':mapped[cp],'width':w,'height':h,'advance16ths':adv,'offset':[x,y],'file':str((O/name).relative_to(R)),'sha256':sha((O/name).read_bytes()),'contents':'pending visual inspection'})
  f['samples']=samples
 except (AssertionError,struct.error,IndexError) as e:f['structuralValidation']='rejected full chain';f['error']=type(e).__name__
 results.append(f)
j['customFontCandidates']=results;j['coverage']['fullFontChainsValidated']=sum('pass' in f['structuralValidation'] for f in results);j['provenanceHashes'][str((O/'fonts.py').relative_to(R))]=sha(Path(__file__).read_bytes());(O/'resources-full.json').write_text(json.dumps(j,separators=(',',':'))+'\n');c=json.loads((O/'dashboard-resources.json').read_text());c['coverage']=j['coverage'];c['fontCandidates']=results;(O/'dashboard-resources.json').write_text(json.dumps(c,separators=(',',':'))+'\n');print([(hex(f['address']),f['structuralValidation'],f.get('mappedCodepointCount'),len(f.get('samples',[]))) for f in results])
