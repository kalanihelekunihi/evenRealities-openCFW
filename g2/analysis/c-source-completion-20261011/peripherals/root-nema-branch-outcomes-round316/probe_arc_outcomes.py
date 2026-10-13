from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
R=Path('/Users/kalani/Repo/evenRealities-openCFW/g2');D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-full-postprocessor-draft-round306';T=D/'probe';T.mkdir(exist_ok=True);stock=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=stock.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';base=0x28100000;delta=base-0x438000
import struct
oracle=bytearray(blob);binding_offset=0x577c38-0x438000;assert struct.unpack_from('<I',oracle,binding_offset)[0]==0x439ca5;struct.pack_into('<I',oracle,binding_offset,0x439ca5+delta);native_file=T/'native-oracle-bound.bin';native_file.write_bytes(oracle)
asm='.section .note.GNU-stack,"",%progbits\n.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: ldr r0,=0xe000ed88\nldr r1,[r0]\norr r1,r1,#0xf00000\nstr r1,[r0]\ndsb\nisb\nbl main\nb .\n.section .native_main,"ax"\n.incbin "'+str(native_file)+'",0,'+str(len(blob))+'\n';asm+='.section .text.abi_probe,"ax"\n.global abi_probe\n.thumb_func\nabi_probe:\n push {r4-r11,lr}\n vpush {d8-d15}\n sub sp,sp,#4\n mov r12,r0\n mov r0,r1\n ldr r2,=0x20016000\n str sp,[r2,#100]\n ldr r2,=abi_fp_seeds\n vldmia r2,{d8-d15}\n movw r4,#0x4444\n movw r5,#0x5555\n movw r6,#0x6666\n movw r7,#0x7777\n movw r8,#0x8888\n movw r9,#0x9999\n movw r10,#0xaaaa\n movw r11,#0xbbbb\n blx r12\n ldr r0,=0x20016000\n stmia r0!,{r4-r11}\n mov r1,sp\n str r1,[r0],#4\n vstmia r0,{d8-d15}\n add sp,sp,#4\n vpop {d8-d15}\n pop {r4-r11,pc}\n.section .rodata.abi_seeds,"a"\n.align 2\nabi_fp_seeds:\n.word 0x3f800001,0xbf800002,0x00000001,0x80000002\n.word 0x7fc12345,0x7f812345,0x7f800000,0xff800000\n.word 0x3e800003,0xbe800004,0x00000000,0x80000000\n.word 0x00800000,0x007fffff,0x7f7fffff,0xff7fffff\n';(T/'start.S').write_text(asm)
ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {*(.reset)}.text 0x28000000 : {*(.text*) *(.rodata*)}.native_main 0x28100000 : {KEEP(*(.native_main))}.bss 0x20001000 (NOLOAD) : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.comment*)}}';(T/'module.ld').write_text(ld)
h=r'''#include <stdint.h>
extern void audio_uart_nema_vg_path_process_561c68(void *);
extern void abi_probe(void(*)(void*),void*);
static volatile uint32_t *const abi=(void*)0x20016000;
static const uint32_t fp_seeds[]={0x3f800001,0xbf800002,1,0x80000002,0x7fc12345,0x7f812345,0x7f800000,0xff800000,0x3e800003,0xbe800004,0,0x80000000,0x00800000,0x007fffff,0x7f7fffff,0xff7fffff};
static volatile uint32_t phase;static uint32_t fp_control,guard_seed,arc_flags,relative_flag,mutation,slot;
static const uint32_t patterns[]={0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0xffc54321};
static volatile uint32_t *const path=(void*)0x20010000;
static void host(uint32_t op,uintptr_t p){register uint32_t r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=p;__asm__ volatile("bkpt 0xab":"+r"(r0),"+r"(r1)::"memory");}
static void hex(uint32_t v){char s[10];for(int i=0;i<8;i++)s[i]="0123456789abcdef"[(v>>(28-i*4))&15];s[8]='\n';s[9]=0;host(4,(uintptr_t)s);}
__attribute__((naked)) void fault_handler(void){__asm__ volatile("mov r0,sp\n\tmov r1,lr\n\tb fault_report");}
void fault_report(uint32_t *frame,uint32_t lr){host(4,(uintptr_t)"FAULT\n");hex(phase);hex(*(volatile uint32_t*)0xe000ed28);hex(*(volatile uint32_t*)0xe000ed2c);hex(lr);for(uint32_t i=0;i<28;i++)hex(frame[i]);if(!(lr&16u))frame+=18;hex(frame[6]);hex(frame[5]);hex(frame[7]);uint32_t a[2]={0x20026,1};host(0x20,(uintptr_t)a);for(;;){}}
static uint32_t fb(float f){union{float f;uint32_t b;}v={.f=f};return v.b;}
static void setup(uint32_t k){for(uint32_t i=0;i<64;i++)path[i]=guard_seed;volatile uint8_t *s=(void*)0x20011000;volatile uint32_t *d=(void*)0x20012000;for(uint32_t i=0;i<32;i++){s[i]=0;d[i]=fb((float)((int32_t)i-5));}uint32_t n=0,m=0;
#define SEG(v) s[n++]=((v)==0?0:((v)|relative_flag))
#define VAL(v) d[m++]=fb(v)
if(k && k!=14 && k!=27 && k!=37){SEG(1);VAL(1.25f);VAL(2.5f);}
switch(k){case 0:break;case 1:SEG(2);VAL(4.75f);VAL(-3.25f);break;case 2:SEG(3);VAL(5.0f);SEG(4);VAL(-2.0f);break;case 3:SEG(5);VAL(4.0f);VAL(9.0f);VAL(8.0f);VAL(-2.0f);break;case 4:SEG(6);VAL(9.0f);VAL(-5.0f);VAL(-3.0f);VAL(8.0f);VAL(5.0f);VAL(1.0f);break;case 5:SEG(5);VAL(4.0f);VAL(9.0f);VAL(8.0f);VAL(-2.0f);SEG(7);VAL(2.0f);VAL(6.0f);break;case 6:SEG(6);VAL(9.0f);VAL(-5.0f);VAL(-3.0f);VAL(8.0f);VAL(5.0f);VAL(1.0f);SEG(8);VAL(7.0f);VAL(9.0f);VAL(2.0f);VAL(3.0f);break;case 7:SEG(9|arc_flags);VAL(4.0f);VAL(3.0f);VAL(0.0f);VAL(5.0f);VAL(6.0f);break;case 8:SEG(9|arc_flags);VAL(4.0f);VAL(3.0f);VAL(30.0f);VAL(5.0f);VAL(6.0f);break;case 9:SEG(10);VAL(4.0f);VAL(4.0f);VAL(3.0f);VAL(8.0f);VAL(5.0f);break;case 10:SEG(11);VAL(4.0f);VAL(4.0f);VAL(3.0f);VAL(8.0f);VAL(5.0f);break;case 11:SEG(0x12);VAL(2.0f);VAL(-3.0f);break;case 12:SEG(2);VAL(4);VAL(5);SEG(1);VAL(-3);VAL(2);SEG(2);VAL(7);VAL(9);break;
case 13:SEG(0);SEG(1);VAL(3);VAL(4);SEG(2);VAL(-2);VAL(-3);break;
case 14:SEG(2);VAL(3);VAL(4);break;
case 15:SEG(10);VAL(6);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);break;
case 16:SEG(11);VAL(6);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);break;
case 17:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(0);VAL(0);VAL(1);VAL(1);VAL(3);VAL(3);break;
case 18:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(1);VAL(-1);VAL(3);VAL(-3);VAL(6);VAL(-6);break;
case 19:SEG(6);VAL(2);VAL(3);VAL(3);VAL(4);VAL(8);VAL(9);break;
case 20:SEG(9|arc_flags);VAL(4);VAL(3);VAL(-30);VAL(5);VAL(6);break;
case 21:SEG(9|arc_flags);VAL(0);VAL(3);VAL(30);VAL(5);VAL(6);break;
case 22:SEG(9|arc_flags);VAL(4);VAL(3);VAL(30);VAL(1.25f);VAL(2.5f);break;
case 23:SEG(7);VAL(5);VAL(6);break;
case 24:SEG(8);VAL(3);VAL(5);VAL(6);VAL(8);break;
case 25:SEG(0);SEG(0);SEG(2);VAL(5);VAL(6);break;
case 26:SEG(1);VAL(3);VAL(4);SEG(2);VAL(5);VAL(6);break;
case 27:SEG(12);break;
case 28:SEG(10);VAL(2);VAL(4);VAL(3);break;
case 29:SEG(11);VAL(2);VAL(4);VAL(3);break;
case 30:SEG(10);VAL(0);break;
case 31:SEG(11);VAL(-2);break;case 32:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(1);VAL(1);VAL(1);VAL(1);VAL(0);VAL(0);break;case 33:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(2);VAL(1);VAL(3);VAL(1);VAL(3);VAL(0);break;case 34:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(1);VAL(1);VAL(3);VAL(1);VAL(6);VAL(0);break;case 35:SEG(10);VAL(10);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);VAL(1);VAL(2);VAL(6);VAL(-3);break;
case 36:SEG(11);VAL(10);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);VAL(1);VAL(2);VAL(6);VAL(-3);break;
case 37:SEG(2);VAL(3);VAL(4);SEG(1);VAL(5);VAL(6);SEG(2);VAL(7);VAL(8);break;
case 38:SEG(6);VAL(9);VAL(-5);VAL(-3);VAL(8);VAL(5);VAL(1);SEG(7);VAL(2);VAL(6);break;
case 39:SEG(5);VAL(4);VAL(9);VAL(8);VAL(-2);SEG(8);VAL(3);VAL(5);VAL(6);VAL(8);break;case 40:SEG(9|arc_flags);VAL(4);VAL(3);VAL(90);VAL(5);VAL(6);break;case 41:SEG(9|arc_flags);VAL(4);VAL(3);VAL(270);VAL(5);VAL(6);break;case 42:SEG(9|arc_flags);VAL(4);VAL(3);VAL(180);VAL(5);VAL(6);break;case 43:SEG(9|arc_flags);d[m++]=0x7fc12345;VAL(3);VAL(45);VAL(5);VAL(6);break;}
if(k)SEG(0);if(0)d[slot]=patterns[mutation];path[0]=n;path[1]=m;path[2]=0x20011000;path[3]=0x20012000;*(volatile uint32_t*)0x20074f14=0xa5a5a5a5;uint32_t f=0x40000u|fp_control;__asm__ volatile("vmsr fpscr,%0"::"r"(f));}
static void fail_comparison(void){uint32_t a[2]={0x20026,1};host(0x20,(uintptr_t)a);for(;;){}}
int main(void){uint32_t result[64],abi_native[25],fpscr,error_native;for(uint32_t relative=0;relative<2;relative++)for(uint32_t arc=0;arc<4;arc++)for(uint32_t guard=0;guard<3;guard++)for(uint32_t round=0;round<4;round++)for(uint32_t extra=0;extra<2;extra++)for(uint32_t k=0;k<44;k++){arc_flags=arc<<5;relative_flag=relative?16:0;guard_seed=guard==0?0:(guard==1?0x5a5a5a5a:0xffffffff);fp_control=(round<<22)|(extra?0x0300009f:0);setup(k);phase=10+k;abi_probe((void(*)(void*))NATIVE_ENTRY,(void*)path);for(uint32_t i=0;i<25;i++)abi_native[i]=abi[i];for(uint32_t i=0;i<8;i++)if(abi[i]!=(i+4)*0x1111u){host(4,(uintptr_t)"FAIL_NATIVE_CORE_SEED\n");fail_comparison();}for(uint32_t i=0;i<16;i++)if(abi[9+i]!=fp_seeds[i]){host(4,(uintptr_t)"FAIL_NATIVE_FP_SEED\n");fail_comparison();}if(abi[8]!=abi[25]){host(4,(uintptr_t)"FAIL_NATIVE_SP\n");fail_comparison();}for(uint32_t i=0;i<64;i++)result[i]=path[i];__asm__ volatile("vmrs %0,fpscr":"=r"(fpscr));error_native=*(volatile uint32_t*)0x20074f14;setup(k);phase=20+k;abi_probe(audio_uart_nema_vg_path_process_561c68,(void*)path);for(uint32_t i=0;i<25;i++)if(abi_native[i]!=abi[i]){host(4,(uintptr_t)"FAIL_ABI\n");hex(i);hex(abi_native[i]);hex(abi[i]);fail_comparison();}if(abi[8]!=abi[25]){host(4,(uintptr_t)"FAIL_C_SP\n");fail_comparison();}uint32_t c;__asm__ volatile("vmrs %0,fpscr":"=r"(c));for(uint32_t i=0;i<64;i++)if(result[i]!=path[i]){host(4,(uintptr_t)"FAIL_PATH\n");hex(mutation);hex(slot);hex(relative);hex(arc);hex(guard);hex(round);hex(extra);hex(k);hex(i);hex(result[i]);hex(path[i]);fail_comparison();}if(error_native!=*(volatile uint32_t*)0x20074f14){host(4,(uintptr_t)"FAIL_ERROR_CELL\n");hex(mutation);hex(slot);hex(relative);hex(arc);hex(guard);hex(round);hex(extra);hex(k);hex(error_native);hex(*(volatile uint32_t*)0x20074f14);fail_comparison();}if(c!=fpscr){host(4,(uintptr_t)"FAIL_FPSCR\n");hex(mutation);hex(slot);hex(relative);hex(arc);hex(guard);hex(round);hex(extra);hex(k);hex(fpscr);hex(c);fail_comparison();}}
host(4,(uintptr_t)"PASS_TARGETED_BRANCH_FIXTURES_ABI_MATRIX\n");uint32_t a[2]={0x20026,0};host(0x20,(uintptr_t)a);for(;;){}}
'''.replace('NATIVE_ENTRY',hex((0x561c68+delta)|1));(T/'harness.c').write_text(h)
flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-ffp-contract=off','-ffunction-sections','-fdata-sections','-fno-vectorize','-fno-slp-vectorize','-mllvm','-disable-arm-loloops'];objs=[]
for p in [T/'start.S',T/'harness.c',D/'candidate-unadmitted.c',R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c']:
 o=T/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
archive=R/'build/c-firmware/20261012/peripherals-root-native-tangent-round304/apollo_main/audio/libaudio-source-candidates.a';elf=T/'test.elf';subprocess.run(['arm-none-eabi-ld','--gc-sections','-T',str(T/'module.ld'),'--defsym=audio_uart_float_math_error_cell_20074f14=0x20074f14',*objs,'-o',str(elf)],check=True)
with elf.open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.native_main');assert s['sh_addr']==base and s.data()==oracle
(D/'probe-native-map.json').write_text(json.dumps({'native_vma':hex(base),'native_sha256':hashlib.sha256(blob).hexdigest(),'selected_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((D/'candidate-unadmitted.c').read_bytes()).hexdigest(),'full_native_instruction_bytes_verified':True,'literal_bindings':[{'native_address':'577c38','original_pointer':'439ca5','oracle_pointer':hex(0x439ca5+delta),'scope':'Onlyauthenticatedfunction-pointerdata rebound; officialblobunchanged'}]},indent=2)+'\n')
r=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(elf)],capture_output=True,text=True,timeout=55);out=r.stdout+r.stderr;(R/'analysis/c-source-completion-20261011/peripherals/root-nema-branch-outcomes-round316/arc-observation.json').write_text(json.dumps({'returncode':r.returncode,'output':out,'scope':'Nonfinite mutation matrix; NOT admission/fullbody qualification'},indent=2)+'\n');print(out[-1500:]);print({'returncode':r.returncode})
