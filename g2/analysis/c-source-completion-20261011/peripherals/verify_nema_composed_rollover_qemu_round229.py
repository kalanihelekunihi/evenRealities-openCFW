from pathlib import Path
import tempfile,subprocess,json,hashlib,sys,re
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-composed-rollover-qemu-round229';S=D/'candidate.c';STOCK=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=STOCK.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();sources=[]
 for folder,start in [('root-nema-sector-rollover-round221','static int32_t rollover_divide'),('root-nema-list-finalize-round222','static int32_t finalize_divide'),('root-nema-ring-submit-round224','static void submit_store'),('root-nema-sector-chain-packet-round225','static void packet_store')]:
  a=selected.index(start);z=selected.find('\n#include',a);p=t/(folder+'.c');p.write_text((B/folder/'candidate.c').read_text().split(start)[0]+selected[a:z if z>=0 else len(selected)]);sources.append(p)
 base=0x28100000;delta=base-0x5147b0;cuts=[(0x4b127c,'error'),(0x5140ea,'flush'),(0x51403c,'read'),(0x514046,'write'),(0x514026,'poll')];ranges=[('rollover',0x5147b0,0x514846),('finalize',0x514b7c,0x514cf2),('packets',0x523ce0,0x52404a)]
 asm='.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n'
 for name,a,z in ranges:asm+='.section .stock_'+name+',"ax"\n.incbin "'+str(STOCK)+'",'+str(32+a-0x438000)+','+str(z-a)+'\n'
 asm+='.section .contextliteral,"a"\n.word 0x20074efc\n.section .ringliteral,"a"\n.word 0x20073db0\n.word 0xff0000f0\n.word 0xff0000f4\n.word 0x000200f4\n'
 for a,n in cuts:asm+=' .section .cut_'+n+',"ax"\n.thumb_func\n b.w cut_'+n+'\n'
 (t/'start.S').write_text(asm);ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {KEEP(*(.reset))}.text 0x28000000 : {*(.text*) *(.rodata*)}'
 for name,a,z in ranges:ld+=' .stock_'+name+' '+hex(a+delta)+' : {KEEP(*(.stock_'+name+'))}'
 ld+=' .contextliteral '+hex(0x514b78+delta)+' : {KEEP(*(.contextliteral))} .ringliteral '+hex(0x52404c+delta)+' : {KEEP(*(.ringliteral))}'
 for a,n in cuts:ld+=' .cut_'+n+' '+hex(a+delta)+' : {KEEP(*(.cut_'+n+'))}'
 ld+=' .data 0x20001000 : {*(.data*)}.bss 0x20001000 : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n';(t/'module.ld').write_text(ld)
 harness=r'''
#include <stdint.h>
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
static uint32_t list[16],next[16],tail[16],buffers[3][64],events[128],saved[517],eventcount,mode;
static uint32_t ring[8],alternate[8],commands[64],context[64];
static volatile uint32_t current[10];
static void log(uint32_t tag,uint32_t a,uint32_t b){events[eventcount++]=tag;events[eventcount++]=a;events[eventcount++]=b;}
void cut_error(uint32_t x){log(0,x,0);}
void cut_flush(const uint32_t *p){log(1,p[0],p[1]);log(11,p[2],p[3]);if(mode==1){list[6]^=8;list[13]=0xabcdef;list[12]=2;}}
uint32_t cut_read(uint32_t x){log(2,x,0);if(mode==2){list[10]=1;list[13]=0x12345678;}return 0;}
int32_t cut_poll(uint32_t x){log(3,x,0);if(mode==3){list[12]=0xffffffff;list[10]=4;}return 0;}
void cut_write(uint32_t a,uint32_t b){log(4,a,b);if(mode==4){audio_uart_nema_ring_descriptor[0]=(uintptr_t)alternate;alternate[5]=0xffffff;}}
void audio_uart_nema_error_set_4b127c(uint32_t x){cut_error(x);}
void audio_uart_nema_buffer_flush_5140ea(const uint32_t*p){cut_flush(p);}
uint32_t audio_uart_nema_reg_read_51403c(uint32_t x){return cut_read(x);}
int32_t audio_uart_nema_poll_514026(uint32_t x){return cut_poll(x);}
void audio_uart_nema_reg_write_514046(uint32_t a,uint32_t b){cut_write(a,b);}
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void hx(uint32_t v){char b[10];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(v>>((7-i)*4))&15];b[8]=32;b[9]=0;host(4,(uintptr_t)b);}
void fault_handler(void){for(unsigned i=0;i<10;i++)hx(current[i]);host(4,(uintptr_t)"FAULT_FINALIZE\n");unsigned x[2]={0x20026,12};host(0x20,(uintptr_t)x);for(;;){}}
static void init(void){eventcount=0;mode=current[7];for(unsigned i=0;i<8;i++)ring[i]=alternate[i]=0;for(unsigned i=0;i<64;i++){commands[i]=0xa5a5a5a5;context[i]=0;}ring[0]=256;ring[1]=3;ring[2]=(uintptr_t)commands;ring[3]=0x2000b000;ring[4]=current[8];audio_uart_nema_ring_descriptor[0]=(uintptr_t)ring;audio_uart_nema_ring_descriptor[1]=(uintptr_t)commands;audio_uart_nema_ring_descriptor[2]=0x2000b000;audio_uart_nema_ring_descriptor[3]=current[4];audio_uart_nema_ring_descriptor[4]=0;*(volatile uint32_t*)0x20074efc=(uintptr_t)context;((uint8_t*)context)[249]=current[6];for(unsigned i=0;i<128;i++)events[i]=0;for(unsigned i=0;i<16;i++)list[i]=next[i]=tail[i]=0;for(unsigned i=0;i<3;i++)for(unsigned j=0;j<64;j++)buffers[i][j]=0xa5a5a5a5;uint32_t *nodes[]={list,next,tail};for(unsigned i=0;i<3;i++){uint32_t *p=nodes[i];p[0]=256;p[1]=i;p[2]=(uintptr_t)buffers[i];p[3]=0x20008000+i*4096;p[4]=16;p[5]=current[1];p[6]=i?(i==1?4u:0u):current[0];p[7]=7;p[8]=current[8]>i?(uintptr_t)nodes[i+1]:0;p[10]=current[4];p[11]=current[2];p[12]=current[3];p[13]=current[5];}if(current[8]==2)next[6]=36;}
static unsigned snap(unsigned save){unsigned k=0,bad=0;uint32_t *r[]={list,next,tail,buffers[0],buffers[1],buffers[2],events,ring,alternate,commands,(uint32_t*)audio_uart_nema_ring_descriptor,context};unsigned sizes[]={16,16,16,64,64,64,128,8,8,64,5,64};for(unsigned j=0;j<12;j++)for(unsigned i=0;i<sizes[j];i++){uint32_t v=r[j][i];if(save)saved[k]=v;else if(saved[k]!=v){if(!bad){hx(k);hx(saved[k]);hx(v);}bad++;}k++;}return bad;}
int main(void){unsigned n=0;uint32_t fs[]={0,4,8,12,32,36,40,44},us[]={0,1,8,0x80000000},ss[]={0,8,0xffffffff},ps[]={0,1,3},cs[]={0,4,0x80000000},qs[]={0,4,0xffffff};
for(unsigned f=0;f<8;f++)for(unsigned u=0;u<4;u++)for(unsigned s=0;s<3;s++)for(unsigned p=0;p<3;p++)for(unsigned c=0;c<3;c++)for(unsigned q=0;q<3;q++)for(unsigned e=0;e<2;e++)for(unsigned m=0;m<6;m++)for(unsigned chain=0;chain<3;chain++){
current[0]=fs[f];current[1]=us[u];current[2]=ss[s];current[3]=ps[p];current[4]=cs[c];current[5]=qs[q];current[6]=e;current[7]=m;current[8]=chain;current[9]=0;init();((void(*)(void*))(uintptr_t)0x28100001)(list);snap(1);current[9]=1;init();audio_uart_nema_sector_rollover_5147b0(list);if(snap(0)){for(unsigned i=0;i<10;i++)hx(current[i]);host(4,(uintptr_t)"FAIL_FINALIZE\n");unsigned x[2]={0x20026,1};host(0x20,(uintptr_t)x);for(;;){}}n++;}
current[9]=0;init();((void(*)(void*))(uintptr_t)0x28100001)(0);snap(1);current[9]=1;init();audio_uart_nema_sector_rollover_5147b0(0);if(snap(0)){unsigned x[2]={0x20026,2};host(0x20,(uintptr_t)x);for(;;){}}n++;host(4,(uintptr_t)"PASS_COMPOSED\n");hx(n);unsigned x[2]={0x20026,0};host(0x20,(uintptr_t)x);for(;;){}}
''';(t/'harness.c').write_text(harness)
 flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding','-fno-builtin','-fno-vectorize','-fno-slp-vectorize'];objs=[]
 for p in [t/'start.S',t/'harness.c',*sources]:
  o=t/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
 e=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),'--defsym=audio_uart_nema_ring_descriptor=0x20073db0',*objs,'-o',str(e)],check=True)
 result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(e)],capture_output=True,text=True,timeout=45);output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);(D/'last-qemu-observation.json').write_text(json.dumps({'returncode':result.returncode,'output':output},indent=2)+'\n');assert result.returncode==0 and 'PASS_COMPOSED' in output
 receipt={'status':'PASS_M55_QEMU_COMPOSED_NEMA_ROLLOVER_FINALIZE_SUBMIT_PACKETS','cases':int(re.search(r'PASS_COMPOSED\n([0-9a-f]{8})',output).group(1),16),'selected_source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'native_range_sha256':{name:hashlib.sha256(blob[a-0x438000:z-0x438000]).hexdigest() for name,a,z in ranges},'child_cuts':5,'limits':['Unchanged native rollover/finalizer/sector-chain/submit body composition with preserved relative calls and literals; full lists/three buffers/ring/alternate/commands/descriptor/context/ordered low-driver events compared.','Flush/read/write/poll/error lower drivers controlled; ordered bus trace/physical effects/ownership/faults/IRQ/scheduler/hardware remain open.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
