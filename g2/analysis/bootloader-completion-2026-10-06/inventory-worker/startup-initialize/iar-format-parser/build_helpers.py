from pathlib import Path
import argparse,subprocess,json,hashlib
N=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
flags=['--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-O2','-ffreestanding','-fno-builtin']
for stem,ld,manifest in [('format_parser','module.ld','build-inputs.json'),('integer_cursor','integer_module.ld','integer-build-inputs.json'),('integer_render','render_module.ld','render-build-inputs.json')]:
 obj=a.output/(stem+'.o');elf=a.output/(stem+'.elf')
 subprocess.run(['clang',*flags,'-c',str(N/(stem+'.c')),'-o',str(obj)],check=True)
 subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(N/ld),str(obj),'-o',str(elf)],check=True)
 m=json.loads((N/manifest).read_text());assert hashlib.sha256(elf.read_bytes()).hexdigest()==m['elf_sha256'],stem
 print('PASS reproduced helper',stem,m['elf_sha256'])
