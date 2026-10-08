from pathlib import Path
import hashlib,json,struct
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
components=[];templates=[]
for n,lit,addr,raw in [(21250,0x47d8fc,0x78eddc,'0300010000000000'),(21252,0x47d904,0x78ede4,'0600010000000000'),(21254,0x47d908,0x78edec,'0500010000000000')]:
 ps=list((b/'analysis').glob('*'+str(n)+'-map/001'));assert len(ps)==1;p=ps[0];r=json.loads((p/'receipt.json').read_text());assert r['input_sha256']==h(d)
 for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
 assert struct.unpack_from('<I',d,lit-0x438000)[0]==addr
 actual=d[addr-0x438000:addr-0x438000+8];assert actual.hex()==raw
 templates.append(dict(pointer_literal=lit,start=addr,end=addr+8,bytes=raw,consumer=str(p),consumer_receipt_sha256=h((p/'receipt.json').read_bytes())))
start=0x78eddc;end=0x78edf4;assert len(d[start-0x438000:end-0x438000])==24
assert struct.unpack_from('<I',d,0x47d900-0x438000)[0]==0x20075043
o=b/'analysis/review-isolated-P2-20859/fresh';o.mkdir(parents=True,exist_ok=True)
(o/'data.json').write_text(json.dumps(dict(start=start,end=end,bytes=d[start-0x438000:end-0x438000].hex(),templates=templates,flag_runtime_address=0x20075043),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted:24 exact locked bytes,three eight-byte templates at78EDDC/78EDE4/78EDEC with first words00010003/00010006/00010005. Pointer and mapped consumer hashes verified. Templatebytes4..7 zero initially; mapped helper updatesbytes4/5 andconditionallybyte6. Runtimeflag pointer20075043 lies outsideflash anditscontentscannotbeclaimedfromthisartifact. Other consumers/wholedataownership remainunproven. No C/freezechanges.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={x.name:h(x.read_bytes()) for x in o.iterdir()}),indent=2)+'\n');print('PASS',end-start,len(templates))
