import hashlib,json
from pathlib import Path
import unicorn as u
from unicorn.arm_const import *
out=Path(__file__).parent
root=Path('/Users/kalani/Repo/evenRealities-openCFW')
p=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(p).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=p[0x4807a0-0x437fe0:0x4807fc-0x437fe0]
assert hashlib.sha256(body[:80]).hexdigest()=='f95193c502160b469e1579e13223f1cdf488a2d8fab9ec07f686c9101fbed753'
rows=json.loads((out/'iteration-predictions.json').read_text())['rows'];results=[]
for r in rows:
 c=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);c.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for addr,size in [(0,4096),(0x480000,4096),(0x20000000,4096),(0x40021000,4096),(0xe000e000,4096)]:c.mem_map(addr,size)
 c.mem_write(0x4807a0,body);c.mem_write(0x40021000,(16 if r['hp'] else 0).to_bytes(4,'little'))
 c.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);c.mem_write(0xe000ed88,(0xf00000).to_bytes(4,'little'))
 c.reg_write(UC_ARM_REG_FPEXC,0x40000000);c.reg_write(UC_ARM_REG_FPSCR,0)
 assert c.reg_read(UC_ARM_REG_FPSCR)==0
 c.reg_write(UC_ARM_REG_SP,0x20000800);c.reg_write(UC_ARM_REG_LR,0x481);c.reg_write(UC_ARM_REG_R0,r['us'])
 trace=[];pc=0x4807a0;error=None
 try:
  for step in range(100):
   if pc in (0x40,0x480):break
   assert 0x4807a0<=pc<0x4807f0
   trace.append(hex(pc));c.emu_start(pc|1,0,count=1);pc=c.reg_read(UC_ARM_REG_PC)
  else:raise RuntimeError('instruction bound')
 except Exception as e:error=str(e)
 predicted=r['stock_pinned'];actual=c.reg_read(UC_ARM_REG_R0) if pc==0x40 else None
 results.append({'us':r['us'],'hp':r['hp'],'fpscr_initial':0,'fpscr_final':c.reg_read(UC_ARM_REG_FPSCR),'stop_pc':hex(pc),'loop_argument':actual,'predicted':predicted['loop_argument'],'pass':error is None and pc==(0x40 if predicted['calls_loop'] else 0x480) and actual==predicted['loop_argument'],'error':error,'trace':trace})
 if error:break
report={'engine':u.__version__,'cpu':'Cortex-M33 M-class, single-instruction stepping','stock_body_sha256':hashlib.sha256(body[:80]).hexdigest(),'synthetic_inputs':['stack','CPACR/FPEXC enabled','FPSCR reset state zero','performance register value'],'loop_executed':False,'results':results,'passed':sum(r['pass'] for r in results),'attempted':len(results),'total_planned':len(rows)}
with (out/'execution-receipt.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print({k:v for k,v in report.items() if k!='results'});print([r for r in results if not r['pass']])
