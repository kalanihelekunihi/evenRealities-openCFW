from pathlib import Path
import hashlib,json,struct
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';b=fw.read_bytes()[32:];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert hashlib.sha256(b).hexdigest()=='773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
src=R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/st-case-flash-pin/stm32g0xx_hal_flash.c';assert sha(src)=='7080740308fdbf2b270d34469e5a0a45f2740aad10e5105925f855ae762fce4b'
h=R/'g2/analysis/case-uart-receive-closure-2026-10-08/stm32g0b1xx.h';ht=h.read_text();assert 'FLASH_CR_OPTLOCK_Pos                   (30U)' in ht and 'FLASH_CR_LOCK_Pos                      (31U)' in ht
cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);rows=[]
for a,name,keys,offset in [(0x8004b6c,'HAL_FLASH_OB_Unlock',[0x08192a3b,0x4c5d6e7f],12),(0x8004bf4,'HAL_FLASH_Unlock',[0x45670123,0xcdef89ab],8)]:
 code=b[a-0x8000000:a-0x8000000+28];ins=list(cs.disasm(code,a));assert len(ins)==14
 literals=[]
 for i in ins:
  if i.mnemonic=='ldr' and '[pc,' in i.op_str:
   imm=int(i.op_str.split('#')[1].split(']')[0],0);addr=((i.address+4)&~3)+imm;v=struct.unpack_from('<I',b,addr-0x8000000)[0];literals.append({'instruction':hex(i.address),'literal_address':hex(addr),'value':hex(v)})
 assert [int(x['value'],16) for x in literals]==[0x40022000,*keys]
 stores=[i.op_str for i in ins if i.mnemonic=='str'];assert stores==[f'r2, [r1, #{hex(offset) if offset==12 else offset}]']*2
 (O/(name+'-instructions.txt')).write_text('\n'.join(f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in ins)+'\n')
 rows.append({'start':hex(a),'end':hex(a+28),'corrected_name':name,'bytes_sha256':hashlib.sha256(code).hexdigest(),'literals':literals})
(O/'results.json').write_text(json.dumps({'status':'PASS','inputs':{str(p.relative_to(R)):sha(p) for p in [fw,src,h,R/'g2/symbols/case.tsv']},'routines':rows,'original_instruction_execution':False,'source_rebuild':False},indent=2)+'\n');print('PASS: two instruction ranges, six addressed literal reads, HAL field correspondence')
