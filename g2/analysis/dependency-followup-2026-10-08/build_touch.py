"""Compile only pinned public SCB source and prove six fixed original extents."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--with-i2c',action='store_true');p.add_argument('--with-irq',action='store_true');p.add_argument('--with-real-irq',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
base=D/'touch-source';pdl=base/'mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc';core=base/'core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561'
flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections']
includes=[base,base/'cmsis',pdl/'drivers/include',pdl/'devices/include',core/'include'];obj=a.output/'scb.o';elf=a.output/'scb.elf'
subprocess.run([str(a.gcc),*flags,*['-I'+str(i) for i in includes],'-c',str(pdl/'drivers/source/cy_scb_common.c'),'-o',str(obj)],check=True)
ld=a.gcc.with_name('arm-none-eabi-ld');subprocess.run([str(ld),'-T',str(D/'touch-scb.ld'),str(obj),'-o',str(elf)],check=True)
b=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
with elf.open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.text');assert s['sh_addr']==0x9218;raw=s.data();assert len(raw)==254 and raw==b[32+0x5f18:32+0x6016]
r=dict(status='PASS_EXACT254',compiler=subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0],compiler_executable_sha256=hashlib.sha256(a.gcc.read_bytes()).hexdigest(),flags=flags,source_files={str(x.relative_to(D)):hashlib.sha256(x.read_bytes()).hexdigest() for x in base.rglob('*') if x.is_file()},object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),linked_text_sha256=hashlib.sha256(raw).hexdigest(),exact_bytes=254,new_compiled_match_bytes=198)
(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS pinned public source matches254 original bytes (198 new attribution)')

if a.with_i2c or a.with_irq or a.with_real_irq:
 iobj=a.output/'i2c-short.o';ielf=a.output/'i2c-init-short.elf'
 subprocess.run([str(a.gcc),*flags,'-fshort-enums',*['-I'+str(i) for i in includes],'-c',str(pdl/'drivers/source/cy_scb_i2c.c'),'-o',str(iobj)],check=True)
 subprocess.run([str(ld),'-T',str(D/'touch-i2c-init.ld'),str(iobj),'-o',str(ielf)],check=True)
 r['i2c_object_sha256']=hashlib.sha256(iobj.read_bytes()).hexdigest();r['i2c_elf_sha256']=hashlib.sha256(ielf.read_bytes()).hexdigest();r['i2c_extra_flags']=['-fshort-enums']
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Built bounded I2C init comparator; run verify_touch_i2c_init.py on i2c-init-short.elf')

if a.with_irq:
 irq=a.output/'i2c-irq.elf'
 subprocess.run([str(ld),'--gc-sections','-Ttext=0x100000','-e','Cy_SCB_I2C_SlaveInterrupt',str(iobj),str(obj),'--defsym=Cy_SysLib_DelayUs=0x110001','--defsym=__aeabi_uidiv=0x110005','--defsym=__aeabi_uidivmod=0x110009','--defsym=Cy_SysLib_EnterCriticalSection=0x11000d','--defsym=Cy_SysLib_ExitCriticalSection=0x110011','-o',str(irq)],check=True)
 r['i2c_irq_elf_sha256']=hashlib.sha256(irq.read_bytes()).hexdigest();r['i2c_irq_limits']='Five helper entry cuts; unreachable external aliases are guarded in verifier, not implementations.'
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Built IRQ dispatch comparator with explicit child cuts; not a full driver execution')

if a.with_real_irq:
 asm=a.output/'syslib-asm.o';real=a.output/'i2c-irq-real.elf'
 subprocess.run([str(a.gcc),'-mcpu=cortex-m0plus','-mthumb','-c',str(pdl/'drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S'),'-o',str(asm)],check=True)
 subprocess.run([str(ld),'--gc-sections','-Ttext=0x100000','-e','Cy_SCB_I2C_SlaveInterrupt',str(iobj),str(obj),str(asm),'-o',str(real)],check=True)
 r['i2c_real_irq_elf_sha256']=hashlib.sha256(real.read_bytes()).hexdigest();r['i2c_real_irq_limits']='Actual source helpers/critical assembly, synthetic FIFO/MMIO and null callbacks only.'
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Built real helper comparator; no numeric executable aliases or stock code')
