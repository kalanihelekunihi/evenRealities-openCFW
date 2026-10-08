from pathlib import Path
import subprocess,json,struct,hashlib,itertools,argparse,shutil
N=Path(__file__).resolve().parent; R=next(p for p in N.parents if (p/'AGENTS.md').exists()); Q=N/'qemu-full';Q.mkdir(exist_ok=True);P=N.parent/'iar-format-parser'
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('/tmp/opencfw-iar-engine-qemu-full'));ap.add_argument('--source-dir',type=Path,default=N);ap.add_argument('--stack-word',type=lambda x:int(x,0),default=0x31313131);args=ap.parse_args();T=args.output;T.mkdir(parents=True,exist_ok=True);S=args.source_dir
blob=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'; official=hashlib.sha256(blob.read_bytes()).hexdigest();assert official=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
fixtures=[]
for name in ['verify_engine.py','verify_float_engine.py']:
 code=(N/name).read_text().split('fixtures=[]',1)[1].split('rows=[]',1)[0];env={'fixtures':[],'itertools':itertools,'struct':struct};exec(code,env);fixtures.extend(f for f in env['fixtures'] if f.get('handler',True))
# Controlled additional boundaries: explicit callbacks stop pathological widths.
for fmt in ['%2147483647d','%2147483648d','%2147483647.2147483647f','%.2147483647f','%.2147483648f','%*.*f']:
 for fail in [0,1,4,10]:fixtures.append(dict(format=fmt,words=[0x80000000,0x80000000,0,0x3ff00000] if fmt=='%*.*f' else [1,0x3ff00000],fail_at=fail))
for bits in [1,0x000fffffffffffff,0x0010000000000000,0x7fefffffffffffff,0x7ff0000000000001,0xfff0000000000001]:
 for fmt in ['%a','%.3e','%.6g','%020.3f']:
  for fpscr in [0,0x00400000,0x00800000,0x00c00000,0x01000000,0x02000000]:fixtures.append(dict(format=fmt,words=[bits&0xffffffff,bits>>32],fpscr=fpscr,fail_at=20))
for mode in [0,1,256,257]:
 for fmt in ['%La','%Lf','%Lg','%a:%n:%d']:
  fixtures.append(dict(format=fmt,words=[0,0x3ff80000,0x20005000,42],mode=mode))
for precision in [0x7fffffff,0x7ffffffe,0x80000000,0xffffffff,0,1,32,100]:
 for fmt in ['%.*f','%.*e','%.*g','%.*a']:
  for fail in [0,4,20]:fixtures.append(dict(format=fmt,words=[precision,0,0,0x3ff00000],fail_at=fail))
for fmt in ['%d:%s:%+020.3f:%n:%llX','%hhn:%c:%.3s:%hn:%g']:
 fixtures.append(dict(format=fmt,words=[42,0x20004000,0,0x3ff80000,0x20005000,0,0x89abcdef,0x12345678] if fmt.startswith('%d') else [0x20005000,65,0x20004000,0x20005004,0,0x3ff00000]))
# Word arrays are deduplicated, and pointer tokens are relocated only in the harness.
wordmap={};formmap={};rows=[]
for f in fixtures:
 words=tuple(x&0xffffffff for x in f['words']);wi=wordmap.setdefault(words,len(wordmap));fi=formmap.setdefault(f['format'],len(formmap));rows.append('{format%d,words%d,%du,%du,%d,%d,%d}'%(fi,wi,f.get('fpscr',0),f.get('mode',0),f.get('fail_at',-1),f.get('align',0),f.get('mask',0)))
shutil.copy2(N/'qemu/start.S',Q/'start.S')
(Q/'oracle.S').write_text('.section .stock,"ax"\n.incbin "'+str(blob)+'"\n')
(Q/'module.ld').write_text('ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.text 0x1000 : {*(.text*) *(.rodata*)}.stock 0x40000 : {KEEP(*(.stock))}. = 0x20010000;.data : {*(.data*)}.bss : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n')
(Q/'call.S').write_text(r""".syntax unified
.thumb
.text
.global call_engine
.thumb_func
call_engine:
 push.w {r4-r11,lr}
 sub sp,#12
 mov r12,r0
 ldr r0,[r12,#20]
 str r0,[sp]
 sub.w r0,sp,#232
 sub.w r1,sp,#40
 movw r2,#0x3131
 movt r2,#0x3131
1: str r2,[r0],#4
 cmp r0,r1
 blo 1b
 movw r4,#0x0004
 movt r4,#0xaac0
 adds r5,r4,#1
 adds r6,r4,#2
 adds r7,r4,#3
 adds r8,r4,#4
 adds r9,r4,#5
 adds r10,r4,#6
 adds r11,r4,#7
 ldr r0,[r12,#4]
 ldr r1,[r12,#8]
 ldr r2,[r12,#12]
 ldr r3,[r12,#16]
 ldr r12,[r12]
 blx r12
 ldr r12,=abi_result
 str r0,[r12],#4
 stmia.w r12!,{r4-r11}
 mov r1,sp
 str r1,[r12],#4
 mrs r1,primask
 str r1,[r12],#4
 vmrs r1,fpscr
 str r1,[r12]
 add sp,#12
 pop.w {r4-r11,pc}
""")
call=(Q/'call.S').read_text().replace('movw r2,#0x3131','movw r2,#'+str(args.stack_word&65535)).replace('movt r2,#0x3131','movt r2,#'+str(args.stack_word>>16));(Q/'call.S').write_text(call)
code=r"""#include <stdint.h>
#include "../engine.h"
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void text(const char*s){host(4,(uintptr_t)s);}static void hex(uint32_t x){char b[9];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(x>>(28-i*4))&15];b[8]=0;text(b);}
uint32_t abi_result[12];extern void call_engine(void*);
struct fixture{const char *format;const uint32_t *words;uint32_t fpscr,mode;int32_t fail;uint8_t align,mask;};
struct result{uint32_t abi[12],attempts,cursor,target[4],arguments[8],message[64],constraint_args[3];uint32_t bytes[2048],contexts[2048];};
static struct result current,saved;static uint32_t states[2048],outtarget[4],arguments[16] __attribute__((aligned(8)));static char format[256];static const char sample[]="hello-boundary";static int fail_at;static uint32_t failures;
static void *put(void *ctx,uint32_t byte){unsigned n=current.attempts++;if(n>=2048)return 0;current.bytes[n]=byte;current.contexts[n]=(uint32_t)((uintptr_t)ctx-(uintptr_t)states);return n==(unsigned)fail_at?0:states+n+1;}
static void constraint(const char *s,void *ctx,unsigned code){for(unsigned i=0;i<64;i++){current.message[i]=(uint8_t)s[i];if(!s[i])break;}current.constraint_args[0]++;current.constraint_args[1]=(uintptr_t)ctx;current.constraint_args[2]=code;}
static void reset(const struct fixture*f){for(unsigned i=0;i<sizeof(current)/4;i++)((uint32_t*)&current)[i]=0;for(unsigned i=0;i<4;i++)outtarget[i]=0xa5a5a5a5;for(unsigned i=0;i<16;i++)arguments[i]=0;unsigned start=f->align/4;for(unsigned i=0;i<8;i++){uint32_t x=f->words[i];if(x==0x20004000)x=(uintptr_t)sample;if(x>=0x20005000&&x<0x20005010)x=(uintptr_t)outtarget+x-0x20005000;arguments[start+i]=x;}for(unsigned i=0;i<256;i++)format[i]=0;for(unsigned i=0;f->format[i];i++)format[i]=f->format[i];fail_at=f->fail;}
static void run(const struct fixture*f,uint32_t function){reset(f);uint32_t *cursor=arguments+f->align/4;uint32_t call[6]={function,(uintptr_t)put,(uintptr_t)states,(uintptr_t)format,(uintptr_t)&cursor,f->mode};__asm__ volatile("msr primask,%0;vmsr fpscr,%1"::"r"((unsigned)f->mask),"r"(f->fpscr):"memory");call_engine(call);__asm__ volatile("cpsie i":::"memory");for(unsigned i=0;i<12;i++)current.abi[i]=abi_result[i];current.cursor=(uintptr_t)cursor-(uintptr_t)(arguments+f->align/4);for(unsigned i=0;i<4;i++)current.target[i]=outtarget[i];for(unsigned i=0;i<8;i++)current.arguments[i]=arguments[f->align/4+i];}
"""
for fmt,i in formmap.items():code+='static const char format%d[]=%s;\n'%(i,json.dumps(fmt))
for words,i in wordmap.items():code+='static const uint32_t words%d[8]={%s};\n'%(i,','.join(str(x)+'u' for x in words))
code+='static const struct fixture fixtures[]={'+','.join(rows)+'};\n'
code+=r"""int main(void){W(0xe000ed88)=0xf00000;__asm__ volatile("dsb;isb");W(0x2000053c)=(uintptr_t)".";W(0x20027190)=(uintptr_t)constraint;
for(unsigned i=0;i<sizeof(fixtures)/sizeof(fixtures[0]);i++){run(fixtures+i,0x4e47b);for(unsigned j=0;j<sizeof(current)/4;j++)((uint32_t*)&saved)[j]=((uint32_t*)&current)[j];run(fixtures+i,(uintptr_t)opencfw_iar_format_engine);unsigned equal=1,field=0;for(unsigned j=0;j<sizeof(current)/4;j++)if(((uint32_t*)&saved)[j]!=((uint32_t*)&current)[j]){equal=0;field=j;break;}for(unsigned j=0;j<8;j++)if(current.abi[j+1]!=0xaac00004+j)equal=0;
hex(i);text(" ");hex(equal);text(" ");hex(field);text(" ");hex(saved.abi[0]);text(" ");hex(current.abi[0]);text(" ");hex(saved.abi[11]);text(" ");hex(current.abi[11]);text("\n");if(!equal){hex(((uint32_t*)&saved)[field]);text(" ");hex(((uint32_t*)&current)[field]);text("\n");failures++;if(failures>=10)break;}}
unsigned quit[2]={0x20026,failures};host(0x20,(uintptr_t)quit);for(;;){} }
"""
(Q/'harness.c').write_text(code);(Q/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
flags=['--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=softfp','-mfpu=fpv5-d16','-O2','-ffreestanding','-fno-builtin'];objects=[];sources=[Q/'harness.c',Q/'start.S',Q/'call.S',Q/'oracle.S',*[S/p for p in ['engine.c','entry.c','termination.c','fp_primitives.c','float_render.c']],*[(S/p if (S/p).exists() else P/p) for p in ['format_parser.c','integer_cursor.c','integer_render.c']]]
for src in sources:
 obj=T/(src.name+'.o');r=subprocess.run(['clang',*flags,'-I',str(N),'-c',str(src),'-o',str(obj)],capture_output=True,text=True);assert r.returncode==0,r.stderr;objects.append(str(obj))
elf=T/'candidate.elf';r=subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(Q/'module.ld'),*objects,'-o',str(elf)],capture_output=True,text=True);assert r.returncode==0,r.stderr
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-objcopy','--dump-section','.stock='+str(T/'oracle.bin'),str(elf)],check=True)
assert hashlib.sha256((T/'oracle.bin').read_bytes()).hexdigest()==official
assert int(subprocess.run(['/opt/homebrew/bin/arm-none-eabi-size',str(elf)],capture_output=True,text=True).stdout.splitlines()[1].split()[0])<0x80000
r=subprocess.run(['/opt/homebrew/bin/qemu-system-arm','-M','mps3-an547','-nographic','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(elf)],capture_output=True,text=True,timeout=60);(T/'comparison.log').write_text(r.stdout+r.stderr)
lines=[x.split() for x in (r.stdout+r.stderr).splitlines() if len(x.split())==7];assert r.returncode!=0 or (len(lines)==len(fixtures) and all(x[1]=='00000001' for x in lines))
receipt={'status':'PASS' if r.returncode==0 else 'FAIL','cases':len(fixtures),'exit_code':r.returncode,'stack_word':args.stack_word,'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'original_sha256':official,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'flags':flags,'log_sha256':hashlib.sha256((T/'comparison.log').read_bytes()).hexdigest(),'limits':['QEMU11 M55; unchanged oracle relocated 0x410000 to0x40000. Native controlled output/constraint callbacks and decimal locale. No hardware/scheduler proof.','Exact return, callback32-bit argument/context sequence, va cursor, n-write targets, caller words, R4-R11, SP, PRIMASK and full FPSCR comparison. Stock-size callee scratch painted identically to31.','Default-handler semihost termination excluded here; prior revision Unicorn boundary receipts preserved.']};(T/'comparison.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],receipt['cases'],receipt['elf_sha256']);print((r.stdout+r.stderr)[-600:]);assert r.returncode==0
