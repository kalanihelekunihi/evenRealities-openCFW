#!/usr/bin/env python3
"""Compare pinned Bosch validator with native and independent parameter limits."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-setup';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'bosch-setup-kernels.o';assert sha(obj)==b['units'][1]['object_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 digest=hashlib.sha256();counts={'0':0,'-8':0,'-15':0};sp=0x2003d000;regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 with tempfile.TemporaryDirectory(prefix='r1-bma-validator-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','r1_bma_validate_accel_parameters','-T',str(ld),'-e','r1_bma_validate_accel_parameters',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
  for odr,bw,perf in itertools.product(range(256),range(256),[0,1,2,255]):
   expected=-8 if perf not in [0,1] or bw>(2 if perf==1 else 7) or not 1<=odr<=12 else -15 if perf==0 and (odr>10 or bw>[7,7,7,7,6,5,4,3,2,1][odr-1]) else 0
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(sp-256,b'\x96'*256)
    for reg,v in zip(regs,[odr,bw,perf,0xabcdef01]):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms['r1_bma_validate_accel_parameters'] if side else 0x96820)|1,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==sp and [u.reg_read(x) for x in saved]==[0x12340000+i for i in range(8)]
    results.append(u.reg_read(UC_ARM_REG_R0))
   assert results[0]==results[1]==expected&0xffffffff,(odr,bw,perf,results,expected)
   counts[str(expected)]+=1;digest.update(bytes([odr,bw,perf])+results[0].to_bytes(4,'little'))
 receipt=dict(comparisons=sum(counts.values()),result_counts=counts,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),all_65536_odr_bandwidth_byte_pairs_at_perf_0_1_2_255=True,independent_limits_oracle=True,actual_pinned_validator_bodies_no_fixtures=True,raw_r0_callee_sp_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'validator-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
