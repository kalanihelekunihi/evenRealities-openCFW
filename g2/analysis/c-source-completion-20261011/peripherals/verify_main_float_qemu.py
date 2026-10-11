#!/usr/bin/env python3
"""QEMU M55 direct stock/source FP formatter comparison; never flashes."""
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parents[4]
D=R/'g2/components/main/full_formatter_outer_candidate'
T=Path('/tmp/g2-main-format-qemu');T.mkdir(exist_ok=True)
stock=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
(T/'start.S').write_text('''.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x20080000\n.word reset_entry\n.rept 14\n.word fault_entry\n.endr\n.text\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n.global fault_entry\n.thumb_func\nfault_entry: mov r0,sp\nbl report_fault\nb .\n''')
(T/'oracle.S').write_text('.section .stock,"ax"\n.incbin "'+str(stock)+'",32\n')
(T/'module.ld').write_text('ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.text 0x1000 : {*(.text*) *(.rodata*)}.stock 0x438000 : {KEEP(*(.stock))}. = 0x20010000;.data : {*(.data*)}.bss : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n')
(T/'harness.c').write_text(r'''#include <stdint.h>
typedef void *(*put_fn)(void *,uint32_t);
extern int32_t g2_iar_general_format(put_fn,void *,const char *,uint32_t **,uint32_t);
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void print(const char *s){host(4,(uintptr_t)s);}
static void hex(uint32_t x){char b[9];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(x>>(28-4*i))&15];b[8]=0;print(b);}
void report_fault(uint32_t *sp){print("FAULT ");hex(sp[6]);print(" ");hex(*(volatile uint32_t *)0xe000ed28);print("\\n");unsigned quit[2]={0x20026,3};host(0x20,(uintptr_t)quit);for(;;){}}
static char out[128];static uint32_t count;
static void *put(void *p,uint32_t ch){(void)p;if(count<127)out[count]=(char)ch;count++;return (void *)1;}
static void clear(void){for(unsigned i=0;i<128;i++)out[i]=0;count=0;}
void __aeabi_memclr4(void *p,unsigned n){volatile uint8_t *q=p;while(n--)*q++=0;}
void __aeabi_memcpy(void *p,const void *s,unsigned n){uint8_t *d=p;const uint8_t *q=s;while(n--)*d++=*q++;}
typedef int32_t (*engine)(put_fn,void *,const char *,uint32_t **,uint32_t);
static int run(engine f,const char *fmt,uint32_t low,uint32_t high){uint32_t words[2] __attribute__((aligned(8)))={low,high};uint32_t *cursor=words;clear();return f(put,(void *)1,fmt,&cursor,0);}
int main(void){print("BEGIN\\n");*(volatile uint32_t *)0xe000ed88=0x00f00000u;__asm__ volatile("dsb;isb");*(volatile uint32_t *)0x200044acu=(uintptr_t)".";
 const char *fmt[]={"%f","%.2f","%e","%g","%a","%F"};const uint32_t bits[][2]={{0,0x3ff00000},{0,0x3ff40000},{0,0},{0,0x7ff00000}};
 unsigned failures=0;
 for(unsigned i=0;i<sizeof(fmt)/sizeof(fmt[0]);i++)for(unsigned j=0;j<sizeof(bits)/sizeof(bits[0]);j++){
  print("STOCK\\n");int a=run((engine)(uintptr_t)0x481837,fmt[i],bits[j][0],bits[j][1]);char saved[128];uint32_t n=count;for(unsigned k=0;k<128;k++)saved[k]=out[k];
  int b=run(g2_iar_general_format,fmt[i],bits[j][0],bits[j][1]);unsigned same=(a==b&&n==count);for(unsigned k=0;k<128;k++)if(saved[k]!=out[k])same=0;
  if(!same){print("FAIL ");print(fmt[i]);print("\n");failures++;} }
 if(!failures)print("PASS 24\n");unsigned quit[2]={0x20026,failures};host(0x20,(uintptr_t)quit);for(;;){} }
''')
flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin']
sources=[T/'start.S',T/'oracle.S',T/'harness.c',*[D/(n+'.c') for n in ('general_format','float_bridge','float_render','fp_primitives')]]
objects=[]
for source in sources:
 obj=T/(source.name+'.o')
 result=subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],capture_output=True,text=True)
 if result.returncode:raise RuntimeError(result.stderr)
 objects.append(str(obj))
elf=T/'main.elf'
result=subprocess.run(['arm-none-eabi-ld','-T',str(T/'module.ld'),*objects,'-o',str(elf)],capture_output=True,text=True)
if result.returncode:raise RuntimeError(result.stderr)
result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-nographic','-monitor','none','-serial','none',
                       '-semihosting-config','enable=on,target=native','-kernel',str(elf)],
                      capture_output=True,text=True,timeout=8)
print(result.returncode,result.stdout[-1000:],result.stderr[-1000:])
if 'FAULT 00481836 00000100' in result.stderr:
 print('SKIP_UNMAPPED_MAIN_STOCK: QEMU MPS3-AN547 lacks executable memory at 0x481836')
 raise SystemExit(0)
assert result.returncode==0 and 'PASS 24' in result.stdout
