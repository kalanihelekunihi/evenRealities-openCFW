from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];rows=[]
for value,clock_mode in itertools.product([1,2,5,100],[0,2]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x40021000,0x1000);u.mem_map(0xe000e000,0x2000);u.mem_write(0x40021000,struct.pack('<I',clock_mode<<3));u.mem_write(0xe000ed88,struct.pack('<I',0xf00000));boundary=[]
 def fetch(u,access,a,size,v,d):boundary.append(dict(address=hex(a),rom_argument=u.reg_read(UC_ARM_REG_R0),lr=hex(u.reg_read(UC_ARM_REG_LR))));return False
 u.hook_add(UC_HOOK_MEM_FETCH_UNMAPPED,fetch);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 try:u.emu_start(0x4807a1,0x2007f000,count=10000)
 except UcError as e:assert e.errno==UC_ERR_FETCH_UNMAPPED;error=str(e)
 else:raise AssertionError('Expected absent ROM entry')
 assert len(boundary)==1 and boundary[0]['address']=='0x40' and boundary[0]['lr']=='0x4807ef'
 rows.append(dict(input=value,clock_mode=clock_mode,boundary=boundary,error=error))
(D/'delay-boundary-results.json').write_text(json.dumps(dict(status='EXPECTED_EXTERNAL_BOUNDARY',original_only_cases=len(rows),comparisons=rows,image_sha256=hashlib.sha256(blob).hexdigest(),cpu_profile='Cortex-M33 selected ARMv8-M/FPU instructions compatible with Apollo M55 path',limits=['Original delay body executes to genuine absent resident ROM fetch0x40; no mapped trampoline, trap, copied opcodes or fake delay return.','This is boundary verification, not independent full delay reconstruction or timing/physical power proof.','Current OTA raw image maps0x438000..0x794324 and does not provide ROM0x40. Need authenticated resident-ROM code or an external hardware/ROM behavior contract to continue that provider.']),indent=2)+'\n');print('Confirmed',len(rows),'original-only ROM0x40 boundaries')
