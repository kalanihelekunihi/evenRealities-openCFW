#!/usr/bin/env python3
"""Bounded original/source 0x415fae formatter entry and R1 contract."""
import hashlib, importlib.util, json, struct, subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
BODY_SHA='4dd35a80dd88663be85e71c3b7e3bf5409c1e4e2150ec3fd1d66133b6d2ad0ea'
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py');er=importlib.util.module_from_spec(spec);spec.loader.exec_module(er)
ELF=HERE/'formatter_415fae_trial.elf';STOP=0x08000000;CALLBACK=0x08002000
FMT=0x20022000;BUF=0x20024cd0;CB=0x200270cc;SP=0x2003f000

def run(stock,image,segments,symbols,fmt,reg_words,callback):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
 for lo,sz in ((0x10000,0x20000),(0x410000,0x25000),(0x20000000,0x40000),(0x08000000,0x3000),(0xe000e000,0x2000)):u.mem_map(lo,sz)
 if stock:u.mem_write(0x410000,image)
 else:
  for s in segments:u.mem_write(s['address'],s['data'])
 u.mem_write(FMT,fmt+b'\0');u.mem_write(BUF,b'\xa5'*160)
 u.mem_write(CB,struct.pack('<I',CALLBACK|1 if callback else 0))
 u.mem_write(0x200271c4,b'\0')
 u.reg_write(a.UC_ARM_REG_SP,SP);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
 for i,val in enumerate([FMT,*reg_words]):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),val)
 u.mem_write(SP,struct.pack('<IIII',0x11223344,0x55667788,0x99aabbcc,0xddeeff00))
 state={'done':False,'calls':[],'trace':set()}
 def hook(cpu,pc,size,_):
  if pc==STOP:state['done']=True;cpu.emu_stop();return
  if pc==CALLBACK:
   arg=cpu.reg_read(a.UC_ARM_REG_R0);raw=bytes(cpu.mem_read(arg,160));state['calls'].append([arg,raw.split(b'\0',1)[0].hex()]);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if pc in (0x08001000,0x08001010):raise AssertionError('unsupported float helper reached')
  if stock and 0x415fae<=pc<0x415fda:state['trace'].update(range(pc,pc+size))
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(f'source entered locked code {pc:#x}')
 u.hook_add(UC_HOOK_CODE,hook)
 entry=0x415fae if stock else symbols['opencfw_provider_415fae']&~1
 try:u.emu_start(entry|1,0,count=1000000)
 except Exception as e:raise RuntimeError(f'{stock=} {fmt=} PC={u.reg_read(a.UC_ARM_REG_PC):#x}') from e
 assert state['done']
 return {'r0':u.reg_read(a.UC_ARM_REG_R0),'r1':u.reg_read(a.UC_ARM_REG_R1),'calls':state['calls'],'buffer':bytes(u.mem_read(BUF,160)).hex(),'sp':u.reg_read(a.UC_ARM_REG_SP),'r4_r11':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)]},state['trace']

def main():
 image=IMAGE.read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 body=image[0x415fae-0x410000:0x415fda-0x410000];assert len(body)==44 and hashlib.sha256(body).hexdigest()==BODY_SHA
 entry_src=ROOT/'g2/components/bootloader/source_candidate_20261010/formatter_415fae_entry.c'
 parser_src=ROOT/'g2/components/bootloader/initializer_callbacks/plain_printf.c'
 for src,obj in ((entry_src,HERE/'formatter_415fae_entry_m4_trial.o'),(parser_src,HERE/'plain_printf_m4_trial.o')):
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-ffreestanding','-fno-builtin','-std=c11','-O2','-fwrapv','-c',str(src),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-T',str(HERE/'formatter_415fae_trial.ld'),str(HERE/'formatter_415fae_entry_m4_trial.o'),str(HERE/'plain_printf_m4_trial.o'),'-o',str(ELF)],check=True,capture_output=True)
 _,segments,symbols=er.elf_info(ELF)
 rows=[];vis=set();formats=[b'hello',b'value=%d',b'hex=%x',b'Error switching to high performance mode. error num = %d\r\n',b'MSPI read xfer failed: instr=0x%02X, addr=0x%08X, len=%u, hal_st=%d\n']
 for callback in (False,True):
  for fmt in formats:
   for regs in ((0,0,0),(0x12345678,0x20022100,0xa5a55a5a)):
    outputs=[]
    for stock in (True,False):
     out,trace=run(stock,image,segments,symbols,fmt,regs,callback);outputs.append(out)
     if stock:vis|=trace
    assert outputs[0]==outputs[1],(callback,fmt,regs,outputs)
    rows.append({'callback':callback,'format':fmt.decode(),'register_args':regs,'result':outputs[0]})
 report={'status':'PASS','cases':len(rows),'image_sha256':SHA,'original_body_sha256':BODY_SHA,'source_entry_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/source_candidate_20261010/formatter_415fae_entry.c').read_bytes()).hexdigest(),'visited_original_bytes':len(vis),'unvisited_original_addresses':[hex(x) for x in range(0x415fae,0x415fda) if x not in vis],'comparisons':rows,'limits':['Callback body is a controlled observer; parser executes stock or selected source.','The format matrix is bounded; floats and full varargs grammar are not covered.','M4-compatible ELF comparison; current M55 archive compilation/linking checked separately.']}
 (HERE/'formatter-415fae-round80-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS',len(rows),'cases',len(vis),'/44 original bytes')
if __name__=='__main__':main()
