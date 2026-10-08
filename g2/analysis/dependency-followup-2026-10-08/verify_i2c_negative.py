from pathlib import Path
import subprocess,json,tempfile
D=Path(__file__).resolve().parent;base=D/'touch-source';pdl=base/'mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc';core=base/'core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561';gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');source=pdl/'drivers/source/cy_scb_i2c.c';results=[]
for name,short,mutate in [('wrong-enum-ABI',False,False),('swap-RX-config-for-TX',True,True)]:
 with tempfile.TemporaryDirectory(prefix='opencfw-i2c-negative-') as work:
  w=Path(work);src=source
  if mutate:
   src=w/'mutant.c';src.write_text(source.read_text().replace('config->useRxFifo','config->useTxFifo'))
  flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections']
  flags += ['-fshort-enums' if short else '-fno-short-enums']
  subprocess.run([str(gcc),*flags,*['-I'+str(i) for i in [base,base/'cmsis',pdl/'drivers/include',pdl/'devices/include',core/'include']],'-c',str(src),'-o',str(w/'object.o')],check=True)
  subprocess.run([str(gcc.with_name('arm-none-eabi-ld')),'-T',str(D/'touch-i2c-init.ld'),str(w/'object.o'),'-o',str(w/'test.elf')],check=True)
  p=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify_touch_i2c_init.py'),str(w/'test.elf')],capture_output=True,text=True)
  assert p.returncode!=0 and ('AssertionError' in p.stderr or 'UC_ERR_EXCEPTION' in p.stderr)
  results.append(dict(control=name,rejected=True,reason='assertion trap under wrong enum layout' if not short else 'guarded state/MMIO mismatch',diagnostic_tail=p.stderr[-400:]))
(D/'touch-i2c-negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS',len(results),'I2C negative controls rejected')
