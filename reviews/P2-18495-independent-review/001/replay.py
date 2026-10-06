from pathlib import Path
import hashlib,json
b=Path('g2/build/pseudocode-first/20260930T190500Z');s=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=s.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
a=0x46061a;e=0x460638;raw=d[a-0x438000:e-0x438000];assert len(raw)==30 and raw[:2]==bytes(2)
o=b/'analysis/apollo-main-diagnostic-fixed-library-global-wrapper-common-diagnostic-literal-pool-18896-map/001';o.mkdir(parents=True,exist_ok=False)
(o/'data.bin').write_bytes(raw)
(o/'words.json').write_text(json.dumps([dict(address=x,bytes=d[x-0x438000:x-0x438000+4].hex(),value=int.from_bytes(d[x-0x438000:x-0x438000+4],'little')) for x in range(a+2,e,4)],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Wrapper literal pool46061A..460638\nPartial;unaccepted.30 non-code bytes:twozeroalignmentbytes46061A..61C thensevenalignedlittle-endianwords46061C..638. Preceding460618POPPC excludesfallthrough;next460638functionexcluded. References18866/18868/18870 corroborate46061Cglobaladdress0x200746E4,460620/624firstwrapperdiagnostics,460630/634secondwrapperdiagnostics. 460628/62Ccommonarguments referencedalso18880/18882/18888/18890/18892/18894. words.json exactbytes/values. Forceddisassemblymnemonicsnotexecutableevidence;no pointercontract inferred.\nNo C,gate/source admission,whole coverage or hardware/simulator proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=len(raw),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',len(raw))
