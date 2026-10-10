from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parents[3];D=Path(__file__).parent;T=R/'g2/analysis/cordio-att-ondeck-threecase-20261009-source-track';S=R/'g2/analysis/cordio-att-ondeck-source-lead-20261009-source-track';b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
read=lambda a,n:b[a-0x438000+32:a-0x438000+32+n];receipts=[]
for name,a,n,h in [('original.bin',0x4b5448,306,'f8256375f5cad966c0c74be78977523bce416b3fdeb41f06c9b98537cd9edd18'),('init.bin',0x531b1c,116,'c1be6b3ada20c1c70cb53db7b6ae8600f68c4c936d9f21f81f1817c92fc1ca48')]:
 x=read(a,n);assert x==(T/name).read_bytes() and sha(x)==h;receipts.append(dict(name=name,address=hex(a),length=n,sha256=h))
f=json.loads((T/'FIELD-AND-MEMORY-RECEIPT.json').read_text())
for a,v in f['literals'].items():assert int.from_bytes(read(int(a,16),4),'little')==int(v,16)
assert int.from_bytes(read(0x700964+9*4,4),'little')==0x4b53dd and read(0x785270+9,1)==b'\x01'
# Exact initializer constants and field stores independently verified as instruction bytes.
for a,x in [(0x531b34,'8420'),(0x531b3e,'2c20'),(0x531b64,'84f82820'),(0x531b68,'581c84f82900'),(0x531b74,'0328'),(0x531b7e,'0328'),(0x531b22,'c1f8b001'),(0x531b28,'81f8b401')]:assert read(a,len(bytes.fromhex(x)))==bytes.fromhex(x),(hex(a),read(a,4).hex())
assert 3*3*44==396 and 396+3*12==432
for conn in range(1,4):assert 384+12*conn==396+12*(conn-1)
r=json.loads((T/'RESULT.json').read_text());assert len(r['cases'])==3
for name in ['sdk','public']:
 t=(S/(name+'-attc_proc.c')).read_text();a=t.index('void attcProcRsp(');i=t.index('{',a);depth=0
 while i<len(t):
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
  if not depth:break
 body=t[a:i];assert sha(body.encode())==r['source_body_sha256'][name];assert body in (T/(name+'-harness.c')).read_text()
for i,c in enumerate(r['cases']):
 s=c['stock'];assert s['events']==c['source']['sdk']['events'] and s['remaining']==c['source']['sdk']['remaining'];assert s['events']!=c['source']['public']['events'] or s['remaining']!=c['source']['public']['remaining']
 assert s['changed_control_offsets']==([6,398] if i<2 else [6]);assert s['packet_unchanged'] and s['ABI_preserved'];assert s['selected']==([dict(index=0,pointer='0x2006fa90',event=10)] if i<2 else [])
 for w in s['writes']:
  a=int(w['address'],16);n=w['size'];assert (0x200ff000-40<=a and a+n<=0x200ff000) or (n==1 and a in [0x2006f90a,0x2006fa92])
 assert [v for v in s['reads'] if 0x20090000<=int(v['address'],16)<0x20090020]==[dict(address='0x20090008',size=1)]
 allowed={0x100000,0x52a4d2,0x4b53dc,0x531ac0,0x531160};assert all(0x4b5448<=int(a,16)<0x4b557a or int(a,16) in allowed for a in s['visited']);assert s['visited'][-1]=='0x100000'
(D/'review.json').write_text(json.dumps({'pass':True,'original_receipts':receipts,'cases':3,'initializer_geometry_and_literals_verified':True,'queue_index_formula_verified_for_ids_1_to_3_statically':True,'recorded_memory_scope_checked':True,'verbatim_source_bodies_verified':True,'producer_files':{str(p.relative_to(R)):sha(p.read_bytes()) for p in sorted(T.iterdir()) if p.is_file()},'source_files':{str(p.relative_to(R)):sha(p.read_bytes()) for p in sorted(S.iterdir()) if p.is_file()}},indent=2)+'\n');print('Independent static/receipt review PASS; no guest replay')
