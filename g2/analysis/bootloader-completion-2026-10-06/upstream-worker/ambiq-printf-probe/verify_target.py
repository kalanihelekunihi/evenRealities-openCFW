import argparse,hashlib,importlib.util,json,struct,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);old=v.Uc
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-plain-printf.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('target-comparison.json'));args=ap.parse_args();_,segs,syms=v.elf.elf_info(args.elf)
def oracle(arch,mode):
 u=old(arch,mode & ~v.UC_MODE_MCLASS);u.ctl_set_cpu_model(v.a.UC_CPU_ARM_CORTEX_A9);u.reg_write(v.a.UC_ARM_REG_C1_C0_2,0xf<<20);u.reg_write(v.a.UC_ARM_REG_FPEXC,0x40000000);u.reg_write(v.a.UC_ARM_REG_FPSCR,0);return u
v.Uc=oracle
strings=[('%'+w+prec+'s',[('s',text)]) for w in ['', '0','1','3','8','-1','-3','-8','08'] for prec in ['', '.0','.1','.2','.8','.-1'] for text in ['', 'a','abc','abcdef','a\nb','abcdefghi']]
values=[0.,-0.,1.25,-1.25,1.36399,1.363994,1.363995,1.996,-1.996,0.1,-0.1,1.5,9.999,99.999,0.00000001,1e-7,1e-6,1e7,2147483520.,2147483648.,math.inf,-math.inf,math.nan]
floats=[('%'+width+prec+'f',[('f',val)]) for width in ['', '12','012'] for prec in ['', '.0','.1','.2','.3','.6','.9','.20'] for val in values]
integers=[('%lld',[('q',-9223372036854775808)]),('%llu',[('q',18446744073709551615)]),('%016llx',[('q',0x123456789abcdef)]),('%d:%llu',[('i',7),('q',0x123456789abcdef)]),('%05d',[('i',-42)]),('%u',[('i',0xffffffff)]),('%x',[('i',0xabcdef)]),('%X',[('i',0xabcdef)]),('%c',[('i',65)]),('%*d',[('i',5),('i',7)]),('a\nb',[]),('%%',[]),('%q',[('i',7)])]
rows=[];trace={}
for translation in [False,True]:
 for fmt,vals in strings+floats+integers:
  obs=[]
  for source in [False,True]:
   m=v.Machine(source,segs,syms);u=m.cpu;u.mem_write(0x200271c4,bytes([translation]));u.mem_write(0x20001000,fmt.encode()+b'\0');words=bytearray();si=0
   for kind,val in vals:
    if kind in ['q','f']:
     while len(words)%8:words+=bytes(4)
     words+=struct.pack('<Q',val&0xffffffffffffffff) if kind=='q' else struct.pack('<d',val)
    elif kind=='s':
     ptr=0x20004000+si*512;si+=1;u.mem_write(ptr,val.encode()+b'\0');words+=struct.pack('<I',ptr)
    else:words+=struct.pack('<I',val&0xffffffff)
   u.mem_write(0x20003000,bytes(words)+bytes(32));u.reg_write(v.a.UC_ARM_REG_SP,v.SP);u.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
   for r,val in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2],[0x20002000,0x20001000,0x20003000]):u.reg_write(r,val)
   try:u.emu_start((syms['opencfw_boot_plain_vsprintf']&~1 if source else 0x415bf6)|1,v.STOP+2,count=500000)
   except Exception as e:raise RuntimeError((source,fmt,vals,hex(u.reg_read(v.a.UC_ARM_REG_PC)),bytes(u.mem_read(u.reg_read(v.a.UC_ARM_REG_PC),4)).hex())) from e
   assert m.done;obs.append({'count':u.reg_read(v.a.UC_ARM_REG_R0),'bytes':bytes(u.mem_read(0x20002000,256)).hex()});trace.update(m.trace)
  assert obs[0]==obs[1],(fmt,vals,obs);rows.append({'format':fmt,'arguments':repr(vals),'translation':translation,'count':obs[0]['count'],'bytes':bytes.fromhex(obs[0]['bytes']).split(b'\0')[0].hex()})
r={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/plain_printf.c').read_bytes()).hexdigest(),'original_sha256':hashlib.sha256(v.BLOB.read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in trace.items()},'limits':['Both actual Thumb stock and compiled ARM C execute on A9 FP64 instruction oracle, not M-profile/hardware proof. No external helper or FP expected-output stubs.','Synthetic scalar argument memory; default FPSCR round-nearest. Original stock wrapper ABI checked separately.','256 destination bytes compare; oversized output, null strings, overlap and concurrent reentrant sinks not certified.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows))
