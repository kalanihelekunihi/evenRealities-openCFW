#!/usr/bin/env python3
"""Observe native compressed input consumption at its authenticated return path."""
import hashlib,json
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-scatter-data';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,b'\x96'*0x40000);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
 for reg,value in [(UC_ARM_REG_R0,0xc4610),(UC_ARM_REG_R1,0x200064a8),(UC_ARM_REG_R2,0x195c)]:u.reg_write(reg,value)
 cursors=[]
 def observe(u,address,size,_):
  if address==0x28746:cursors.append(u.reg_read(UC_ARM_REG_R0))
 u.hook_add(UC_HOOK_CODE,observe);u.emu_start(0x286f5,0x20000100,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and len(cursors)==1 and 0xc4610<=cursors[0]<=0xc4d08
 output=bytes(u.mem_read(0x200064a8,6492));assert hashlib.sha256(output).hexdigest()==sha(OUT/'observed-initialized-data.bin');end=cursors[0]
 receipt=dict(application_sha256=sha(app),driver_sha256=sha(Path(__file__)),native_return_observation_pc='0x28746',input_start='0xc4610',input_cursor_before_zero_return=hex(end),consumed_bytes=end-0xc4610,available_fixture_bytes=1784,trailing_bytes=app.read_bytes()[end-0x27000:0xc4d08-0x27000].hex(),initialized_bytes=6492,initialized_sha256=hashlib.sha256(output).hexdigest(),source_ownership=False,limitations=['Observed cursor covers this locked input and native return path only; no source startup or whole-image completion is inferred.'])
 (OUT/'input-consumption.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
