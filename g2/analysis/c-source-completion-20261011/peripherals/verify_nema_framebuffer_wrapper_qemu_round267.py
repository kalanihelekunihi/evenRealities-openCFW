from pathlib import Path
import tempfile,subprocess,json,hashlib,re,sys
from elftools.elf.elffile import ELFFile
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-framebuffer-wrapper-round267';S=D/'candidate.c';STOCK=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=STOCK.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
base=0x28100002;delta=base-0x5223a2;cuts=[(0x5155dc,'destroy'),(0x5155e4,'store'),(0x51565c,'error')]
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);(t/'candidate.c').write_text('#include <stdint.h>\ntypedef struct {uint32_t words[4];} audio_uart_vg_framebuffer_264;\n'+S.read_text())
 asm='.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n.section .native_wrapper,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x5223a2-0x438000)+','+str(0x5223fa-0x5223a2)+'\n.section .wrapper_literal,"a"\n.word 0x20074f08\n'
 for a,n in cuts:asm+=' .section .cut_'+n+',"ax"\n.thumb_func\nb.w cut_'+n+'\n'
 (t/'start.S').write_text(asm);ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {*(.reset)}.text 0x28000000 : {*(.text*) *(.rodata*)}.native_wrapper '+hex(base)+' : {*(.native_wrapper)}.wrapper_literal '+hex(0x522568+delta)+' : {*(.wrapper_literal)}'
 for a,n in cuts:ld+='.cut_'+n+' '+hex(a+delta)+' : {*(.cut_'+n+')}'
 ld+='.bss 0x20001000 (NOLOAD) : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.comment*)}}';(t/'module.ld').write_text(ld)
 harness=r'''
#include <stdint.h>
typedef struct{uint32_t words[4];} F;
extern void audio_uart_nema_vg_set_framebuffer_5223a2(uint32_t,uint32_t,F);
#define CELL (*(volatile uint32_t*)0x20074f08)
static volatile uint32_t *const a=(void*)0x20010000,*const b=(void*)0x20011000;
static uint32_t events[32],ne,mut;
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab" : "+r"(r0),"+r"(r1)::"memory");}
static void hex(uint32_t x){char s[10];for(unsigned i=0;i<8;i++)s[i]="0123456789abcdef"[(x>>(28-i*4))&15];s[8]='\n';s[9]=0;host(4,(uintptr_t)s);}
void fault_handler(void){host(4,(uintptr_t)"FAULT\n");unsigned out[2]={0x20026,1};host(0x20,(uintptr_t)out);for(;;){}}
void cut_destroy(void){events[ne++]=1;if(mut)CELL=(uint32_t)(uintptr_t)b;}
void cut_store(uint32_t w,uint32_t h,F f){events[ne++]=2;events[ne++]=w;events[ne++]=h;for(unsigned i=0;i<4;i++)events[ne++]=f.words[i];if(mut)CELL=(uint32_t)(uintptr_t)b;}
void cut_error(uint32_t x){events[ne++]=3;events[ne++]=x;}
void audio_uart_nema_vg_framebuffer_destroy_5155dc(void){cut_destroy();}
void audio_uart_nema_vg_framebuffer_store_5155e4(uint32_t w,uint32_t h,F f){cut_store(w,h,f);}
void audio_uart_nema_vg_set_error_51565c(uint32_t x){cut_error(x);}
static void init(unsigned flag,unsigned x,unsigned y,unsigned m,unsigned seed){ne=0;mut=m;CELL=(uint32_t)(uintptr_t)a;for(unsigned i=0;i<32;i++){a[i]=seed*0x01010101u;b[i]=(seed^255)*0x01010101u;}a[6]=flag;a[4]=x;a[5]=y;b[4]=y;b[5]=x;}
void main(void){uint32_t values[]={0,1,2,3,0x80000000,0xffffffff};unsigned count=0;for(unsigned f=0;f<4;f++)for(unsigned x=0;x<6;x++)for(unsigned y=0;y<6;y++)for(unsigned m=0;m<2;m++)for(unsigned seed=0;seed<2;seed++){
F p={{0x12345678,0x89abcdef,0x76543210,0xfedcba98}};uint32_t saved[32],n;init(f,values[x],values[y],m,seed?165:0);((void(*)(uint32_t,uint32_t,F))(uintptr_t)0x28100003)(values[x],values[y],p);n=ne;for(unsigned i=0;i<n;i++)saved[i]=events[i];uint32_t cell=CELL;
init(f,values[x],values[y],m,seed?165:0);audio_uart_nema_vg_set_framebuffer_5223a2(values[x],values[y],p);if(n!=ne||cell!=CELL){host(4,(uintptr_t)"FAIL_COUNT\n");fault_handler();}for(unsigned i=0;i<n;i++)if(saved[i]!=events[i]){hex(f);hex(x);hex(y);hex(m);hex(i);hex(saved[i]);hex(events[i]);host(4,(uintptr_t)"FAIL_EVENT\n");fault_handler();}count++;}
host(4,(uintptr_t)"PASS_FRAMEBUFFER_WRAPPER\n");hex(count);unsigned out[2]={0x20026,0};host(0x20,(uintptr_t)out);for(;;){}}
''';(t/'harness.c').write_text(harness);flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding','-fno-builtin','-fno-vectorize','-fno-slp-vectorize'];objs=[]
 for p in [t/'start.S',t/'harness.c',t/'candidate.c']:
  o=t/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
 e=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),'--defsym=audio_uart_nema_vg_framebuffer_context_cell_20074f08=0x20074f08',*objs,'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);sec=elf.get_section_by_name('.native_wrapper');assert sec['sh_addr']==base and sec.data()==blob[0x5223a2-0x438000:0x5223fa-0x438000]
 result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(e)],capture_output=True,text=True,timeout=45);output=result.stdout+result.stderr;(D/'last-qemu-observation.json').write_text(json.dumps({'returncode':result.returncode,'output':output},indent=2)+'\n');print(output[-1500:]);assert result.returncode==0 and 'PASS_FRAMEBUFFER_WRAPPER' in output
 receipt={'status':'PASS_M55_QEMU_FRAMEBUFFER_WRAPPER','cases':int(re.search(r'PASS_FRAMEBUFFER_WRAPPER\n([0-9a-f]{8})',output).group(1),16),'selected':'--selected' in sys.argv,'native_section_vma_and_bytes_verified':True,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':3,'limits':['Unchanged native IT conditional calls execute on M55; child events/AAPCS descriptor/fresh context cell matched with controlled child mutations. Real children,memory trace/guards,SP/callee-saved,FPU lifecycle/layout/hardware remain.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
