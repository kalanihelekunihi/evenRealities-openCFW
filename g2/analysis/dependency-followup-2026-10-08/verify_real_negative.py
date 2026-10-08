from pathlib import Path
import subprocess,tempfile,json,argparse
D=Path(__file__).resolve().parent;base=D/'touch-source';pdl=base/'mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc';core=base/'core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561';p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);a=p.parse_args();results=[]
text=(pdl/'drivers/source/cy_scb_i2c.c').read_text()
for name,modified in [('wrong-RX-progress',text.replace('context->slaveRxBufferIdx  += numToCopy;','context->slaveRxBufferIdx  += numToCopy + 1;')),('missing-TX-pointer-advance',text.replace('&context->slaveTxBuffer[numToCopy]','&context->slaveTxBuffer[0]'))]:
 assert modified!=text
 with tempfile.TemporaryDirectory(prefix='opencfw-i2c-real-negative-') as work:
  w=Path(work);src=w/'mutant.c';src.write_text(modified)
  flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-fshort-enums','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections'];inc=['-I'+str(i) for i in [base,base/'cmsis',pdl/'drivers/include',pdl/'devices/include',core/'include']]
  for source,target in [(src,'i2c.o'),(pdl/'drivers/source/cy_scb_common.c','scb.o')]:subprocess.run([str(a.gcc),*flags,*inc,'-c',str(source),'-o',str(w/target)],check=True)
  subprocess.run([str(a.gcc),'-mcpu=cortex-m0plus','-mthumb','-c',str(pdl/'drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S'),'-o',str(w/'asm.o')],check=True)
  subprocess.run([str(a.gcc.with_name('arm-none-eabi-ld')),'--gc-sections','-Ttext=0x100000','-e','Cy_SCB_I2C_SlaveInterrupt',str(w/'i2c.o'),str(w/'scb.o'),str(w/'asm.o'),'-o',str(w/'test.elf')],check=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify_touch_i2c_real.py'),str(w/'test.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr
  results.append(dict(control=name,rejected=True,diagnostic_tail=r.stderr[-800:]))
(D/'touch-i2c-real-negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS',len(results),'actual-helper progress mutants rejected')
