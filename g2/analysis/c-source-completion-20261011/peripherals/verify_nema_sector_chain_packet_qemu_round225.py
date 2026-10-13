from pathlib import Path
import tempfile,subprocess,json,hashlib,sys,re
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-sector-chain-packet-round225';S=D/'candidate.c';STOCK=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=STOCK.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native523ce0');z=selected.find('\n#include',a);S=t/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native523ce0')[0]+selected[a:z if z>=0 else len(selected)])
 base=0x28100000;delta=base-0x523ce0;cuts=[(0x5140ea,'flush'),(0x514046,'write')]
 asm='.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n.section .stock,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x523ce0-0x438000)+','+str(0x523e92-0x523ce0)+'\n.section .literal,"a"\n .word 0x20073db0\n.word 0xff0000f0\n.word 0xff0000f4\n.word 0x000200f4\n'
 for a,n in cuts:asm+=' .section .cut_'+n+',"ax"\n.thumb_func\n b.w cut_'+n+'\n'
 (t/'start.S').write_text(asm);ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {KEEP(*(.reset))}.text 0x28000000 : {*(.text*) *(.rodata*)}.stock '+hex(base)+' : {KEEP(*(.stock))}.literal '+hex(0x52404c+delta)+' : {KEEP(*(.literal))}'
 for a,n in cuts:ld+=' .cut_'+n+' '+hex(a+delta)+' : {KEEP(*(.cut_'+n+'))}'
 ld+=' .data 0x20001000 : {*(.data*)}.bss 0x20001000 : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n';(t/'module.ld').write_text(ld)
 harness=r'''
#include <stdint.h>
extern uint32_t audio_uart_nema_sector_finalize_523ce0(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_chain_finalize_523dba(void *,uint32_t);
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
static uint32_t ring[8],other[8],commands[64],node[4],events[16],saved[101],count;
static volatile uint32_t current[9];
static void log(uint32_t t,uint32_t a,uint32_t b){events[count++]=t;events[count++]=a;events[count++]=b;}
void cut_flush(void *p){log(1,(uintptr_t)p,0);if(current[6]==1){audio_uart_nema_ring_descriptor[0]=(uintptr_t)other;audio_uart_nema_ring_descriptor[2]=0x20009000;other[4]=3;}}
void cut_write(uint32_t r,uint32_t v){log(2,r,v);if(current[6]==2){audio_uart_nema_ring_descriptor[0]=(uintptr_t)other;other[5]=current[4]^0x01000000u;}}
void audio_uart_nema_buffer_flush_5140ea(void *p){cut_flush(p);}
void audio_uart_nema_reg_write_514046(uint32_t r,uint32_t v){cut_write(r,v);}
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void hx(uint32_t v){char b[10];for(unsigned i=0;i<8;i++)b[i]="0123456789abcdef"[(v>>((7-i)*4))&15];b[8]=32;b[9]=0;host(4,(uintptr_t)b);}
void fault_handler(void){for(unsigned i=0;i<9;i++)hx(current[i]);host(4,(uintptr_t)"FAULT_PACKET\n");unsigned x[2]={0x20026,12};host(0x20,(uintptr_t)x);for(;;){}}
static void init(void){count=0;for(unsigned i=0;i<8;i++)ring[i]=other[i]=0;for(unsigned i=0;i<16;i++)events[i]=0;for(unsigned i=0;i<64;i++)commands[i]=current[7]?0xa5a5a5a5:0;ring[0]=256;ring[2]=(uintptr_t)commands;ring[3]=0x20008000;ring[4]=current[3];ring[5]=other[5]=current[4];node[3]=current[5];audio_uart_nema_ring_descriptor[0]=(uintptr_t)ring;audio_uart_nema_ring_descriptor[1]=(uintptr_t)commands;audio_uart_nema_ring_descriptor[2]=0x20008000;audio_uart_nema_ring_descriptor[3]=current[2];audio_uart_nema_ring_descriptor[4]=0;}
static unsigned snap(unsigned save){unsigned k=0,bad=0;uint32_t *r[]={ring,other,commands,events,(uint32_t*)audio_uart_nema_ring_descriptor};unsigned sizes[]={8,8,64,16,5};for(unsigned j=0;j<5;j++)for(unsigned i=0;i<sizes[j];i++){uint32_t v=r[j][i];if(save)saved[k]=v;else if(saved[k]!=v){if(!bad){hx(k);hx(saved[k]);hx(v);}bad++;}k++;}return bad;}
int main(void){unsigned n=0;uint32_t ws[]={0,1,0xffffffff},cs[]={0,1,2,4,8,16,32,0x80000000,0xffffffff},is[]={0,1,3,7,15},qs[]={0,0xfffffe,0xffffff,0x7fffffff,0x80000000,0xffffffff},ps[]={0,0x20008000,0xffffffff};
for(unsigned mode=0;mode<2;mode++)for(unsigned w=0;w<3;w++)for(unsigned c=0;c<9;c++)for(unsigned i=0;i<5;i++)for(unsigned q=0;q<6;q++)for(unsigned p=0;p<3;p++)for(unsigned m=0;m<3;m++)for(unsigned seed=0;seed<2;seed++){
current[0]=mode;current[1]=ws[w];current[2]=cs[c];current[3]=is[i];current[4]=qs[q];current[5]=ps[p];current[6]=m;current[7]=seed;current[8]=0;init();uint32_t a=mode?((uint32_t(*)(void*,uint32_t))(uintptr_t)0x281000db)(node,current[1]):((uint32_t(*)(uint32_t,uint32_t))(uintptr_t)0x28100001)(current[5],current[1]);snap(1);current[8]=1;init();uint32_t b=mode?audio_uart_nema_chain_finalize_523dba(node,current[1]):audio_uart_nema_sector_finalize_523ce0(current[5],current[1]);if(snap(0)||a!=b){hx(a);hx(b);for(unsigned j=0;j<9;j++)hx(current[j]);host(4,(uintptr_t)"FAIL_PACKET\n");unsigned x[2]={0x20026,1};host(0x20,(uintptr_t)x);for(;;){}}n++;}
host(4,(uintptr_t)"PASS_PACKET\n");hx(n);unsigned x[2]={0x20026,0};host(0x20,(uintptr_t)x);for(;;){}}
''';(t/'harness.c').write_text(harness)
 flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding','-fno-builtin','-fno-vectorize','-fno-slp-vectorize'];objs=[]
 for p in [t/'start.S',t/'harness.c',S]:
  o=t/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
 e=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),'--defsym=audio_uart_nema_ring_descriptor=0x20073db0',*objs,'-o',str(e)],check=True)
 result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(e)],capture_output=True,text=True,timeout=45);output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);(D/'last-qemu-observation.json').write_text(json.dumps({'returncode':result.returncode,'output':output},indent=2)+'\n');assert result.returncode==0 and 'PASS_PACKET' in output
 receipt={'status':'PASS_M55_QEMU_NEMA_SECTOR_CHAIN_PACKET','cases':int(re.search(r'PASS_PACKET\n([0-9a-f]{8})',output).group(1),16),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'native_body_sha256':hashlib.sha256(blob[0x523ce0-0x438000:0x523e92-0x438000]).hexdigest(),'child_cuts':2,'limits':['Unchanged434byte native sector+chain bodies relocated/mod4 with descriptor and packet literal words preserved and child veneers. Full ring/alternate ring/command buffer/descriptor/ordered child events/results compared.','Ordered bus trace/NULL chain pointer faults/actual cache-register/ownership/hardware remain open.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
