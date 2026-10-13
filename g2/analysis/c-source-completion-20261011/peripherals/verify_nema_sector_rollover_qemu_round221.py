from pathlib import Path
import tempfile,subprocess,json,hashlib,sys,re
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-sector-rollover-round221';S=D/'candidate.c';STOCK=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=STOCK.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native5147b0');z=selected.find('\n#include',a);S=t/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native5147b0')[0]+selected[a:z if z>=0 else len(selected)])
 base=0x28100000;delta=base-0x5147b0;cuts=[(0x4b127c,'error'),(0x514b7c,'finalize'),(0x523f10,'submit'),(0x514026,'poll')]
 asm='.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n.section .stock,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x5147b0-0x438000)+','+str(0x514846-0x5147b0)+'\n.section .literal,"a"\n.word 0x20074efc\n'
 for a,n in cuts:asm+=' .section .cut_'+n+',"ax"\n.thumb_func\n b.w cut_'+n+'\n'
 (t/'start.S').write_text(asm);ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {KEEP(*(.reset))}.text 0x28000000 : {*(.text*) *(.rodata*)}.stock '+hex(base)+' : {KEEP(*(.stock))}.literal '+hex(0x514b78+delta)+' : {KEEP(*(.literal))}'
 for a,n in cuts:ld+=' .cut_'+n+' '+hex(a+delta)+' : {KEEP(*(.cut_'+n+'))}'
 ld+=' .data 0x20001000 : {*(.data*)}.bss 0x20001000 : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n';(t/'module.ld').write_text(ld)
 harness=r'''
#include <stdint.h>
extern void audio_uart_nema_sector_rollover_5147b0(void *);
static uint32_t context[64],list[16],events[32],saved[112],count,flags,mut,pollret;
static volatile uint32_t current[10];
static void log(uint32_t tag,uint32_t arg){events[count++]=tag;events[count++]=arg;}
void cut_error(uint32_t x){log(0,x);}
void cut_finalize(void *x){log(1,(uintptr_t)x);if(mut==1){list[6]=flags^32;list[13]=0xffffff;((uint8_t*)context)[249]=1;}}
void cut_submit(uint32_t x){log(2,x);if(mut==2)list[13]=0x12345678;}
int32_t cut_poll(uint32_t x){log(3,x);return pollret;}
void audio_uart_nema_error_set_4b127c(uint32_t x){cut_error(x);}
void audio_uart_nema_list_finalize_514b7c(void *x){cut_finalize(x);}
void audio_uart_nema_submit_523f10(uint32_t x){cut_submit(x);}
int32_t audio_uart_nema_poll_514026(uint32_t x){return cut_poll(x);}
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void hx(uint32_t v){char b[10];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(v>>((7-i)*4))&15];b[8]=32;b[9]=0;host(4,(uintptr_t)b);}
void fault_handler(void){for(unsigned i=0;i<10;i++)hx(current[i]);host(4,(uintptr_t)"FAULT_ROLLOVER\n");unsigned x[2]={0x20026,12};host(0x20,(uintptr_t)x);for(;;){}}
static void init(void){count=0;flags=current[0];mut=current[7];pollret=current[6];for(unsigned i=0;i<64;i++)context[i]=0;for(unsigned i=0;i<16;i++)list[i]=0;for(unsigned i=0;i<32;i++)events[i]=0;*(volatile uint32_t*)0x20074efc=(uintptr_t)context;list[5]=current[1];list[6]=flags;list[7]=list[13]=current[5];list[10]=current[8];list[11]=current[2];list[12]=current[3];((uint8_t*)context)[249]=current[4];}
static unsigned snap(unsigned save){unsigned k=0,bad=0;uint32_t *r[]={context,list,events};unsigned sizes[]={64,16,32};for(unsigned j=0;j<3;j++)for(unsigned i=0;i<sizes[j];i++){uint32_t v=r[j][i];if(save)saved[k]=v;else if(saved[k]!=v){if(!bad){hx(k);hx(saved[k]);hx(v);}bad++;}k++;}return bad;}
int main(void){unsigned n=0;uint32_t fs[]={0,32,255},us[]={0,1,16,0x80000000},ss[]={0,8,0xffffffff},ps[]={0,16,32,48,7},cs[]={0,64,0x80000000,0xffffffff};
for(unsigned f=0;f<3;f++)for(unsigned u=0;u<4;u++)for(unsigned s=0;s<3;s++)for(unsigned p=0;p<5;p++)for(unsigned r=0;r<2;r++)for(unsigned q=0;q<2;q++)for(unsigned e=0;e<2;e++)for(unsigned m=0;m<3;m++)for(unsigned c=0;c<4;c++){
current[0]=fs[f];current[1]=us[u];current[2]=ss[s];current[3]=ps[p];current[4]=r;current[5]=q?7:0xffffff;current[6]=e?0xffffffff:0;current[7]=m==0?0xffffffff:m;current[8]=cs[c];current[9]=0;init();((void(*)(void*))(uintptr_t)0x28100001)(list);snap(1);current[9]=1;init();audio_uart_nema_sector_rollover_5147b0(list);if(snap(0)){for(unsigned i=0;i<10;i++)hx(current[i]);host(4,(uintptr_t)"FAIL_ROLLOVER\n");unsigned x[2]={0x20026,1};host(0x20,(uintptr_t)x);for(;;){}}n++;}
current[9]=0;init();((void(*)(void*))(uintptr_t)0x28100001)(0);snap(1);current[9]=1;init();audio_uart_nema_sector_rollover_5147b0(0);if(snap(0)){unsigned x[2]={0x20026,2};host(0x20,(uintptr_t)x);for(;;){}}n++;host(4,(uintptr_t)"PASS_ROLLOVER\n");hx(n);unsigned x[2]={0x20026,0};host(0x20,(uintptr_t)x);for(;;){}}
''';(t/'harness.c').write_text(harness)
 flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding','-fno-builtin','-fno-vectorize','-fno-slp-vectorize'];objs=[]
 for p in [t/'start.S',t/'harness.c',S]:
  o=t/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
 e=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),'--defsym=audio_uart_nema_context_cell=0x20074efc',*objs,'-o',str(e)],check=True)
 result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(e)],capture_output=True,text=True,timeout=45);output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);(D/'last-qemu-observation.json').write_text(json.dumps({'returncode':result.returncode,'output':output},indent=2)+'\n');assert result.returncode==0 and 'PASS_ROLLOVER' in output
 receipt={'status':'PASS_M55_QEMU_NEMA_SECTOR_ROLLOVER','cases':int(re.search(r'PASS_ROLLOVER\n([0-9a-f]{8})',output).group(1),16),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'native_body_sha256':hashlib.sha256(blob[0x5147b0-0x438000:0x514846-0x438000]).hexdigest(),'child_cuts':4,'limits':['Unchanged150byte native body relocated with mod4 alignment, relative veneers/context literal preserved. Full list/context/ordered child events compared including capacity bounds and mutations.','Ordered bus trace/real finalize-submit-poll/error/ownership/pointerfaults/hardware remain open.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
