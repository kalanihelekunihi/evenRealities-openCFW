from pathlib import Path
import tempfile,subprocess,json,hashlib,sys,re
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-list-finalize-round222';S=D/'candidate.c';STOCK=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=STOCK.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native514b7c');z=selected.find('\n#include',a);S=t/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native514b7c')[0]+selected[a:z if z>=0 else len(selected)])
 base=0x28100000;delta=base-0x514b7c;cuts=[(0x4b127c,'error'),(0x5140ea,'flush'),(0x51403c,'read'),(0x514026,'poll'),(0x523ce0,'sector'),(0x523dba,'chain')]
 asm='.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n.section .stock,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x514b7c-0x438000)+','+str(0x514cf2-0x514b7c)+'\n.section .literal,"a"\n.word 0x20074efc\n'
 for a,n in cuts:asm+=' .section .cut_'+n+',"ax"\n.thumb_func\n b.w cut_'+n+'\n'
 (t/'start.S').write_text(asm);ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {KEEP(*(.reset))}.text 0x28000000 : {*(.text*) *(.rodata*)}.stock '+hex(base)+' : {KEEP(*(.stock))}.literal '+hex(0x514b78+delta)+' : {KEEP(*(.literal))}'
 for a,n in cuts:ld+=' .cut_'+n+' '+hex(a+delta)+' : {KEEP(*(.cut_'+n+'))}'
 ld+=' .data 0x20001000 : {*(.data*)}.bss 0x20001000 : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n';(t/'module.ld').write_text(ld)
 harness=r'''
#include <stdint.h>
extern void audio_uart_nema_list_finalize_514b7c(void *);
static uint32_t list[16],next[16],tail[16],buffers[3][64],events[128],saved[368],eventcount,mode;
static volatile uint32_t current[10];
static void log(uint32_t tag,uint32_t a,uint32_t b){events[eventcount++]=tag;events[eventcount++]=a;events[eventcount++]=b;}
void cut_error(uint32_t x){log(0,x,0);}
void cut_flush(const uint32_t *p){log(1,p[0],p[1]);log(11,p[2],p[3]);if(mode==1){list[6]^=8;list[13]=0xabcdef;list[12]=2;}}
uint32_t cut_read(uint32_t x){log(2,x,0);if(mode==2){list[10]=1;list[13]=0x12345678;}return current[6];}
int32_t cut_poll(uint32_t x){log(3,x,0);if(mode==3){list[12]=0xffffffff;list[10]=4;}return 0;}
uint32_t cut_sector(uint32_t p,uint32_t n){log(4,p,n);if(mode==4){list[12]=0xffffffff;list[11]=7;list[10]=3;}return 0x13579bdf;}
uint32_t cut_chain(void *p,uint32_t n){log(5,(uintptr_t)p,n);if(mode==5)list[5]=0x87654321;return 0x2468ace0;}
void audio_uart_nema_error_set_4b127c(uint32_t x){cut_error(x);}
void audio_uart_nema_buffer_flush_5140ea(const uint32_t*p){cut_flush(p);}
uint32_t audio_uart_nema_reg_read_51403c(uint32_t x){return cut_read(x);}
int32_t audio_uart_nema_poll_514026(uint32_t x){return cut_poll(x);}
uint32_t audio_uart_nema_sector_finalize_523ce0(uint32_t p,uint32_t n){return cut_sector(p,n);}
uint32_t audio_uart_nema_chain_finalize_523dba(void *p,uint32_t n){return cut_chain(p,n);}
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void hx(uint32_t v){char b[10];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(v>>((7-i)*4))&15];b[8]=32;b[9]=0;host(4,(uintptr_t)b);}
void fault_handler(void){for(unsigned i=0;i<10;i++)hx(current[i]);host(4,(uintptr_t)"FAULT_FINALIZE\n");unsigned x[2]={0x20026,12};host(0x20,(uintptr_t)x);for(;;){}}
static void init(void){eventcount=0;mode=current[7];for(unsigned i=0;i<128;i++)events[i]=0;for(unsigned i=0;i<16;i++)list[i]=next[i]=tail[i]=0;for(unsigned i=0;i<3;i++)for(unsigned j=0;j<64;j++)buffers[i][j]=0xa5a5a5a5;uint32_t *nodes[]={list,next,tail};for(unsigned i=0;i<3;i++){uint32_t *p=nodes[i];p[0]=256;p[1]=i;p[2]=(uintptr_t)buffers[i];p[3]=0x20008000+i*4096;p[4]=16;p[5]=current[1];p[6]=i?(i==1?4u:0u):current[0];p[7]=7;p[8]=current[8]>i?(uintptr_t)nodes[i+1]:0;p[10]=current[4];p[11]=current[2];p[12]=current[3];p[13]=current[5];}if(current[8]==2)next[6]=36;}
static unsigned snap(unsigned save){unsigned k=0,bad=0;uint32_t *r[]={list,next,tail,buffers[0],buffers[1],buffers[2],events};unsigned sizes[]={16,16,16,64,64,64,128};for(unsigned j=0;j<7;j++)for(unsigned i=0;i<sizes[j];i++){uint32_t v=r[j][i];if(save)saved[k]=v;else if(saved[k]!=v){if(!bad){hx(k);hx(saved[k]);hx(v);}bad++;}k++;}return bad;}
int main(void){unsigned n=0;uint32_t fs[]={0,4,8,12,32,36,40,44},us[]={0,1,8,0x80000000},ss[]={0,8,0xffffffff},ps[]={0,1,3},cs[]={0,4,0x80000000},qs[]={0,4,0xffffff};
for(unsigned f=0;f<8;f++)for(unsigned u=0;u<4;u++)for(unsigned s=0;s<3;s++)for(unsigned p=0;p<3;p++)for(unsigned c=0;c<3;c++)for(unsigned q=0;q<3;q++)for(unsigned e=0;e<2;e++)for(unsigned m=0;m<6;m++)for(unsigned chain=0;chain<3;chain++){
current[0]=fs[f];current[1]=us[u];current[2]=ss[s];current[3]=ps[p];current[4]=cs[c];current[5]=qs[q];current[6]=e?0xffffffff:0;current[7]=m;current[8]=chain;current[9]=0;init();((void(*)(void*))(uintptr_t)0x28100001)(list);snap(1);current[9]=1;init();audio_uart_nema_list_finalize_514b7c(list);if(snap(0)){for(unsigned i=0;i<10;i++)hx(current[i]);host(4,(uintptr_t)"FAIL_FINALIZE\n");unsigned x[2]={0x20026,1};host(0x20,(uintptr_t)x);for(;;){}}n++;}
current[9]=0;init();((void(*)(void*))(uintptr_t)0x28100001)(0);snap(1);current[9]=1;init();audio_uart_nema_list_finalize_514b7c(0);if(snap(0)){unsigned x[2]={0x20026,2};host(0x20,(uintptr_t)x);for(;;){}}n++;host(4,(uintptr_t)"PASS_FINALIZE\n");hx(n);unsigned x[2]={0x20026,0};host(0x20,(uintptr_t)x);for(;;){}}
''';(t/'harness.c').write_text(harness)
 flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding','-fno-builtin','-fno-vectorize','-fno-slp-vectorize'];objs=[]
 for p in [t/'start.S',t/'harness.c',S]:
  o=t/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
 e=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),'--defsym=audio_uart_nema_context_cell=0x20074efc',*objs,'-o',str(e)],check=True)
 result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(e)],capture_output=True,text=True,timeout=45);output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);(D/'last-qemu-observation.json').write_text(json.dumps({'returncode':result.returncode,'output':output},indent=2)+'\n');assert result.returncode==0 and 'PASS_FINALIZE' in output
 receipt={'status':'PASS_M55_QEMU_NEMA_LIST_FINALIZE','cases':int(re.search(r'PASS_FINALIZE\n([0-9a-f]{8})',output).group(1),16),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'native_body_sha256':hashlib.sha256(blob[0x514b7c-0x438000:0x514cf2-0x438000]).hexdigest(),'child_cuts':6,'limits':['Unchanged374byte native body relocated/mod4; relative child veneers. Full three lists/three command buffers/ordered child arguments and flush descriptors compared.','Ordered bus trace/real cache-register-sector-chain-poll/error/ownership/pointerfaults/hardware remain open.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
