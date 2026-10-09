from pathlib import Path
import itertools,json,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
rows=[];expected=struct.pack('<5I',0,0,0,32768,12000000)
assert raw[0x77d8f8-0x438000:0x77d90c-0x438000]==expected
for pattern,mask,user in itertools.product([0,255],[0,1],[0,52,56]):
 u=machine();u.mem_write(0x200001cc,bytes([pattern])*24);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.mem_write(0x20073324,b'\0'*56);u.emu_start(0x4c2b07,0x4c2b18,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x4c2b18;assert u.reg_read(UC_ARM_REG_R0)==0;assert bytes(u.mem_read(0x200001cc,20))==expected;assert bytes(u.mem_read(0x200001e0,4))==bytes([pattern])*4
 before=bytes(u.mem_read(0x20073324,56)).hex();u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,user);u.emu_start(0x4c3d9f,0x2007f000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==7;assert bytes(u.mem_read(0x20073324,56)).hex()==before;assert u.reg_read(UC_ARM_REG_PRIMASK)==mask
 rows.append(dict(pattern=pattern,primask=mask,user=user,board=expected.hex(),xtal_request_status=7,user_bitmap_unchanged=True))
(D/'board-startup-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),validation='original-instruction bounded block and subsequent complete request assertions',block_start='0x4C2B06',block_end_exclusive='0x4C2B18',default_table_address='0x77D8F8',default_table_sha256=hashlib.sha256(expected).hexdigest(),defaults=dict(hs_mode=0,hs_hz=0,ls_mode=0,ls_hz=32768,external_hz=12000000),comparisons=rows,limits=['Stops before HFRC/HFRC2 configuration calls; not complete platform initialization.','No claim that another caller never later changes board info.','No connected hardware or observed running-board configuration.']),indent=2)+'\n');print('PASS',len(rows),'original board startup assertions')
