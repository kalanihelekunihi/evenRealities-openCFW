from pathlib import Path
import itertools,json,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
rows=[]
for family,ref,hs_hz in itertools.product(['hfrc2','syspll'],[0,1],[0,24000000]):
 u=machine();u.mem_write(0x20073324,b'\0'*56);u.mem_write(0x200001cc,struct.pack('<5I',0,hs_hz,0,32768,12000000));u.mem_write(0x20004537,b'\0');u.mem_write(0x20074f55,b'\0')
 if family=='hfrc2':entry=0x4c399e;cfg=struct.pack('<BBHII',ref,0,0,0x12345678,0);valid_address=0x20004537;freq=196608000
 else:entry=0x4c3b44;cfg=struct.pack('<6BHI',ref,0,0,4,2,1,48,0);valid_address=0x20074f55;freq=48000000
 u.mem_write(0x20006000,cfg);u.reg_write(UC_ARM_REG_R0,freq);u.reg_write(UC_ARM_REG_R1,0x20006000);u.emu_start(entry|1,0x2007f000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;status=u.reg_read(UC_ARM_REG_R0);valid=bytes(u.mem_read(valid_address,1)).hex();assert status==(7 if ref==0 and hs_hz==0 else 0);assert valid==('00' if status else '01')
 rows.append(dict(family=family,reference=ref,hs_hz=hs_hz,external_hz=12000000,status=status,valid=valid))
(D/'config-constraint-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),validation='original-only private configuration assertions, not native comparison',comparisons=rows,limits=['Explicit valid config with no active users; no full boot/caller or hardware reference proof.','Stock HS=0 prevents a freshly validated adjusted XTAL-reference config.','Tests that manually seed valid XTAL-reference config at HS=0 are constructed/inconsistent state, not established stock-startup reachability.']),indent=2)+'\n');print('PASS',len(rows),'original configuration guard assertions')
