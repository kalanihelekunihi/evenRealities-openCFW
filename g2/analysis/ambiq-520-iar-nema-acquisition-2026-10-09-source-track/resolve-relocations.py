from pathlib import Path
import struct,json,hashlib
p=Path(__file__).parent
ns={};exec((p/'compare-static.py').read_text().split('stockp=')[0].replace('p=Path(__file__).parent',f'p=Path({str(p)!r})'),ns)
body=bytearray(ns['body']);base=0x5143d4;target=0x4b127c;lit=0x514b78;rows=[]
def branch(offset,address,link):
 old=bytes(body[offset:offset+4]);d=address-(base+offset+4);assert d%2==0 and -(1<<24)<=d<(1<<24)
 bits=d&0x1ffffff;s=bits>>24;j1=1^((bits>>23)&1)^s;j2=1^((bits>>22)&1)^s
 h1=0xf000|(s<<10)|((bits>>12)&0x3ff);h2=(0xd000 if link else 0x9000)|(j1<<13)|(j2<<11)|((bits>>1)&0x7ff)
 body[offset:offset+4]=struct.pack('<HH',h1,h2)
 rows.append({'type':'R_ARM_THM_CALL' if link else 'R_ARM_THM_JUMP24','offset':offset,'original':old.hex(),'inplace_addend':-4,'P':hex(base+offset),'S':hex(address),'displacement_from_PC_plus4':d,'resolved':bytes(body[offset:offset+4]).hex()})
branch(110,target,False);old=bytes(body[114:118]);pc=(base+114+4)&~3;delta=lit-pc;assert 0<=delta<4096
h1,h2=struct.unpack('<HH',old);h1=(h1|0x80);h2=(h2&0xf000)|delta;body[114:118]=struct.pack('<HH',h1,h2);rows.append({'type':'R_ARM_THM_PC12','offset':114,'original':old.hex(),'inplace_addend':-4,'P':hex(base+114),'aligned_architectural_PC':hex(pc),'DataTable12_binding':hex(lit),'displacement':delta,'resolved':bytes(body[114:118]).hex(),'table_R_ARM_ABS32_symbol':'nema_context','table_original_addend':0,'stock_cell_value':'0x20074efc'})
branch(172,target,True)
raw=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();stock=raw[base-0x437fe0:0x5144ba-0x437fe0]
r={'bindings':rows,'linked_candidate_length':len(body),'linked_candidate_sha256':hashlib.sha256(body).hexdigest(),'stock_extent_length':len(stock),'exact_linked_equality':bytes(body)==stock,'stock_extra_block':{'address':'0x514476','size':8,'instructions':['ldr r2,[r0,#24]','bic.w r2,r2,#32','str r2,[r0,#24]'],'candidate_corresponding_point':'object .text+0x416: movs r0,#0; no flags-bit-clear block'},'stock_last8_are_executable':True,'canonical_target_names_status':'historical Nema provenance; canonical symbol seed Unverified','remaining_binding_limit':'nema_set_error and nema_context names are inferred candidate bindings from agreeing stock branch/literal sites, not independently closed global-symbol identity','linker_relaxation_not_simulated':True}
(p/'RELOCATION-CLOSURE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
