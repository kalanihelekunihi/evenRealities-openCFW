#!/usr/bin/env python3
"""Execute original sample correction; gate/finite fixture evidence, no C equivalence claim."""
import importlib.util,json,hashlib,struct,itertools
from pathlib import Path
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('control',ROOT/'g2/components/bootloader/initializer_callbacks/verify_adc_control.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
rows=[];trace={}
for valid,enable,word in itertools.product((0,1,255),(0,1,256,257),(0,0x0000003f,0x000fffff,0xa5ffffff)):
 m=v.Machine(False,(),{},dict(values=[0]*5,rom_status=0));m.cpu.mem_write(0x20027199,bytes([valid]));m.w(0x20026fe0,0);m.w(0x20026fe4,0);m.cpu.reg_write(a.UC_ARM_REG_R0,word);m.cpu.reg_write(a.UC_ARM_REG_R1,enable);m.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);m.cpu.reg_write(a.UC_ARM_REG_SP,v.v.v.SP);m.cpu.reg_write(a.UC_ARM_REG_LR,v.v.v.STOP|1);m.cpu.emu_start(0x42ee01,v.v.v.STOP+2,count=1000);assert m.done;actual=m.cpu.reg_read(a.UC_ARM_REG_R0)
 if not valid or not(enable&255):expected=word
 else:
  raw=(word>>6)&0x3fff;intermediate=(raw*1190)>>12;corrected=int(f32(f32(f32(float(intermediate))*4096.0)/1190.0));expected=(word&0xfff00000)|((corrected<<6)&0x3ffff)
 assert actual==expected,(valid,enable,hex(word),hex(actual),hex(expected));rows.append(dict(valid=valid,enable=enable,input=hex(word),output=hex(actual)));trace.update({hex(pc):raw for pc,raw in m.trace.items()})
b=v.v.v.BLOB.read_bytes()
for pc,raw in trace.items():p=int(pc,16);assert b[p-v.v.v.BASE:p-v.v.v.BASE+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
r=dict(status='PASS',cases=len(rows),original_sha256=hashlib.sha256(b).hexdigest(),scope='Original instructions only, no reconstructed-source or shared-image equivalence claim.',original_trace=trace,comparisons=rows,limits=['FP32/FPSCR default and zero gain/offset fixture only; arbitrary calibration, nonfinite values and saturation remain untested.','Mapped RAM/MMIO and direct invocation; no actual FIFO, analog or application delivery proof.']);(Path(__file__).parent/'adc-sample-gate-original.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='PASS',cases=len(rows))))
