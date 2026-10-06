from pathlib import Path
import hashlib,json
b=Path('g2/build/pseudocode-first/20260930T190500Z');s=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=s.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
a=0x460118;e=0x460128;raw=d[a-0x438000:e-0x438000];assert len(raw)==16
o=b/'analysis/apollo-main-diagnostic-fixed-library-classifier-divisor-and-global-table-literal-pool-18862-map/001';o.mkdir(parents=True,exist_ok=False)
(o/'data.bin').write_bytes(raw)
(o/'words.json').write_text(json.dumps([dict(address=x,bytes=d[x-0x438000:x-0x438000+4].hex(),value=int.from_bytes(d[x-0x438000:x-0x438000+4],'little')) for x in range(a,e,4)],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Shared literal pool460118..460128\nPartial;unaccepted.16 non-code bytes,four alignedlittle-endianwords. Preceding460116BXLR excludesfallthrough;next460128functionexcluded. Prior18850/18852/18854 reference460118 asunsigneddivisor1000000(0x000F4240). 18856/18860 reference46011Cglobaladdress0x200746CC and460120globaladdress0x200746C8. 18858 wrapper references460124fixedtableaddress0x20002928. words.json enumeratesexactbytes/values. No executabledecodingofpool; do not infer tablecontents orcontractsfromaddresses.\nNo C,gate/source admission,whole coverage or hardware/simulator proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=len(raw),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',len(raw))
