from pathlib import Path
import zipfile,struct,json,hashlib
out=Path(__file__).parent
z=zipfile.ZipFile('/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip')
suffix='CMSIS/ARM/Lib/ARM/DSP_LIB_CM55/iar_cortexM55f_math.a'
ar=z.read(next(n for n in z.namelist() if n.endswith(suffix)))
assert hashlib.sha256(ar).hexdigest()=='034dfb178804c3885b73e15c28bd3ff72c34d5fc9800409c44c453061662c772'
raw=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
stock=raw[0x20:];base=0x438000
def sha(b):return hashlib.sha256(b).hexdigest()
def cstr(b,i):return b[i:b.find(b'\0',i)].decode(errors='replace')
members=[];off=8;table=b''
while off<len(ar):
 h=ar[off:off+60];assert h[58:60]==b'`\n';n=int(h[48:58]);name=h[:16].decode().strip();b=ar[off+60:off+60+n];off+=60+n+(n&1)
 if name=='//':table=b;continue
 if name in ('/','/SYM64/'):continue
 if name.startswith('/') and name[1:].isdigit():name=table[int(name[1:]):].split(b'/\n')[0].decode()
 members.append((name.rstrip('/'),b))
inventory=[];selected=[];constants=[]
wanted={'arm_fir_f32','arm_biquad_cascade_df1_f32','arm_biquad_cascade_df2T_f32','arm_rfft_fast_f32','arm_cfft_f32','arm_sin_f32','arm_cos_f32','arm_mat_mult_f32','arm_mat_inverse_f32','arm_fir_q15','arm_fir_q31','arm_biquad_cascade_df1_q31','arm_cfft_q15','arm_cfft_q31','arm_rfft_q15','arm_rfft_q31','arm_mean_f32','arm_var_f32','arm_std_f32','arm_power_f32'}
for name,b in members:
 assert b[:6]==b'\x7fELF\x01\x01'
 shoff=struct.unpack_from('<I',b,32)[0];sz,num,si=struct.unpack_from('<HHH',b,46);ss=[struct.unpack_from('<10I',b,shoff+i*sz) for i in range(num)]
 def data(s):return b[s[4]:s[4]+s[5]]
 names=[cstr(data(ss[si]),s[0]) for s in ss];symtabs={}
 for i,s in enumerate(ss):
  if s[1]==2:symtabs[i]=[{'name':cstr(data(ss[s[6]]),x[0]),'value':x[1],'size':x[2],'info':x[3],'section':x[5]} for x in struct.iter_unpack('<IIIBBH',data(s))]
 rels={}
 for i,s in enumerate(ss):
  if s[1] in (9,4):
   for x in struct.iter_unpack('<II' if s[1]==9 else '<IIi',data(s)):
    rels.setdefault(s[7],[]).append({'offset':x[0],'type':x[1]&255,'symbol':symtabs[s[6]][x[1]>>8]['name']})
 for tab in symtabs.values():
  for sym in tab:
   sec=sym['section'];n=sym['size']
   if name=='CommonTables.o' and sym['name'] in {'sinTable_f32','twiddleCoef_4096','armBitRevTable','twiddleCoef_16','twiddleCoef_rfft_32','twiddleCoef_rfft_4096'} and sec<len(ss) and n>=256 and not(ss[sec][2]&4):
    cb=data(ss[sec])[sym['value']:sym['value']+n];assert len(cb)==n
    cr=[x for x in rels.get(sec,[]) if sym['value']<=x['offset']<sym['value']+n];hits=[]
    if not cr:
     i=stock.find(cb)
     while i>=0:hits.append(hex(base+i));i=stock.find(cb,i+1)
    constants.append({'object':name,'symbol':sym['name'],'size':n,'sha256':sha(cb),'relocations':cr,'complete_data_hits':hits})
   if sym['info']&15!=2 or not n or sec>=len(ss) or not(ss[sec][2]&4):continue
   st=sym['value']&~1;body=data(ss[sec])[st:st+n];assert len(body)==n
   r=[x for x in rels.get(sec,[]) if st<=x['offset']<st+n]
   rec={'object':name,'object_sha256':sha(b),'symbol':sym['name'],'section':names[sec],'section_bytes':ss[sec][5],'start':st,'size':n,'body_sha256':sha(body),'relocations':r}
   inventory.append(rec)
   if sym['name'] not in wanted:continue
   # Conservative eight-byte exclusion at each relocation, never mask bytes.
   spans=[];pos=0
   for x in sorted(r,key=lambda x:x['offset']):
    rp=x['offset']-st
    if rp>pos:spans.append((pos,rp))
    pos=max(pos,rp+8)
   if pos<n:spans.append((pos,n))
   probes=sorted((x for x in spans if x[1]-x[0]>=64),key=lambda x:x[1]-x[0],reverse=True)[:3]
   rec=dict(rec);rec['eligible_size_at_least_128']=n>=128;rec['probes']=[]
   if n>=128:
    for a,e in probes:
     needle=body[a:e];hits=[];i=stock.find(needle)
     while i>=0:
      hits.append({'span_address':hex(base+i),'implied_function_address':hex(base+i-a)});i=stock.find(needle,i+1)
     rec['probes'].append({'offset':a,'length':e-a,'sha256':sha(needle),'stock_hits':hits})
    rec['raw_complete_function_hits']=[];i=stock.find(body)
    while i>=0:rec['raw_complete_function_hits'].append(hex(base+i));i=stock.find(body,i+1)
   selected.append(rec)
result={'archive_path':suffix,'archive_sha256':sha(ar),'stock_package_sha256':sha(raw),'stock_payload_base':hex(base),'member_count':len(members),'inventoried_function_count':len(inventory),'requested_symbols':sorted(wanted),'selected':selected,'missing_requested_symbols':sorted(wanted-{x['symbol'] for x in selected}),'method':'complete sized ELF function extents; three longest unchanged relocation-free spans >=64 bytes per selected function >=128 bytes; conservatively exclude eight bytes at each relocation; no masking, downloaded code execution or linker substitution','limits':'raw span misses do not exclude functions compiled differently, linker-relaxed bodies, other functions, other SDK revisions or other payloads'}
(out/'CONSTANT-CHECK.json').write_text(json.dumps(constants,indent=2)+'\n');(out/'FUNCTION-INVENTORY.json').write_text(json.dumps(inventory,indent=2)+'\n');(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('Constant checks:',json.dumps(constants))
print(json.dumps({'functions':len(inventory),'selected':len(selected),'eligible':sum(x['eligible_size_at_least_128'] for x in selected),'probes':sum(len(x['probes']) for x in selected),'span_hits':sum(len(y['stock_hits']) for x in selected for y in x['probes']),'complete_hits':sum(len(x.get('raw_complete_function_hits',[])) for x in selected),'missing':result['missing_requested_symbols']},indent=2))
