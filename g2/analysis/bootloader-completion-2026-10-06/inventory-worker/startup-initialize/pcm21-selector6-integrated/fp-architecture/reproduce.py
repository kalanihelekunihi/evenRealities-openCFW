from pathlib import Path
import subprocess,hashlib,json
here=Path(__file__).resolve().parent;t=Path('/tmp/opencfw-fp-reproduce');t.mkdir(exist_ok=True);rows=[]
flags=['--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=softfp','-ffreestanding','-fno-builtin','-O1']
subprocess.run(['clang',*flags,'-c',str(here/'start.S'),'-o',str(t/'start.o')],check=True)
for name in ['probe','probe-zero']:
 subprocess.run(['clang',*flags,'-c',str(here/(name+'.c')),'-o',str(t/(name+'.o'))],check=True)
 elf=t/(name+'.elf');subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(here/'module.ld'),'-o',str(elf),str(t/'start.o'),str(t/(name+'.o'))],check=True)
 run=subprocess.run(['/opt/homebrew/bin/qemu-system-arm','-M','mps3-an547','-nographic','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(elf)],capture_output=True,text=True,timeout=20);assert run.returncode==0
 lines=(run.stdout+run.stderr).splitlines();assert len(lines)==48
 for line in lines:
  mode,bits,before,after=[int(x,16) for x in line.split()];assert before==mode;assert after&0x3000000==mode&0x3000000
  flags_added=(1 if bits in [0x7f800001,0xff800001] else 0)|(0x80 if mode&(1<<24) and bits in [1,0x80000001] else 0)
  assert after&0x9f==(mode&0x9f)|flags_added
 rows.append(dict(name=name,cases=48,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),output=lines))
(t/'comparison.json').write_text(json.dumps(dict(status='PASS_BOUNDED_MICROPROBE',results=rows),indent=2));print('PASS 96 scalar FP microprobes')
