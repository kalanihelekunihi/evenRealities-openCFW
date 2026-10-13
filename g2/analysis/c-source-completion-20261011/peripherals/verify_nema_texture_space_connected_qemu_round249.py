from pathlib import Path
import tempfile,subprocess,json,hashlib,sys,re
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-texture-space-connected-round249';S=B/'root-nema-list-extension-round247/candidate.c';STOCK=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=STOCK.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('static int32_t ext247_div');z=selected.find('\n#include',a);S=t/'selected.c';S.write_text((B/'root-nema-list-extension-round247/candidate.c').read_text().split('static int32_t ext247_div')[0]+selected[a:z if z>=0 else len(selected)])
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('static int32_t space246_div');z=selected.find('\n#include',a);space=t/'space.c';space.write_text((B/'root-nema-command-space-round246/candidate.c').read_text().split('static int32_t space246_div')[0]+selected[a:z if z>=0 else len(selected)])
 a=selected.index('static uint32_t bind243_align4');z=selected.find('\n#include',a);texture=t/'texture.c';texture.write_text((B/'root-nema-texture-bind-round243/candidate.c').read_text().split('static uint32_t bind243_align4')[0]+selected[a:z])
 a=selected.index('/* Native52262e');z=selected.find('\n#include',a);h=selected[a:z];a=selected.index('/* Native52264e');z=selected.find('\n#include',a);h+=selected[a:z];tiling=t/'tiling.c';tiling.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_context_cell[];\n'+h)
 base=0x28100000;delta=base-0x4b1298;cuts=[(0x4b127c,'error'),(0x51416c,'alloc'),(0x514070,'buffer'),(0x514178,'release'),(0x5147b0,'sector')]
 asm='.syntax unified\n.thumb\n.section .vectors,"a"\n.word 0x2007ff00\n.word reset_entry\n.rept 14\n.word fault_handler\n.endr\n.section .reset,"ax"\n.global reset_entry\n.thumb_func\nreset_entry: bl main\nb .\n.section .stock,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x514504-0x438000)+','+str(0x5147b0-0x514504)+'\n.section .literal,"a"\n.word 0x20074efc\n'
 asm+=' .section .space,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x514aec-0x438000)+','+str(0x514b76-0x514aec)+'\n.section .literal2,"a"\n.word 0x20074efc\n'
 asm+=' .section .native_tex,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x4b1298-0x438000)+','+str(0x4b146c-0x4b1298)+'\n.section .tiling,"ax"\n.incbin "'+str(STOCK)+'",'+str(32+0x52262e-0x438000)+','+str(0x52266e-0x52262e)+'\n.section .tex_lit,"a"\n.word 0x20074efc\n.section .tilingliteral,"a"\n.word 0x20074efc\n'
 for a,n in cuts:asm+=' .section .cut_'+n+',"ax"\n.thumb_func\n b.w cut_'+n+'\n'
 (t/'start.S').write_text(asm);ld='ENTRY(reset_entry)\nSECTIONS{.vectors 0 : {KEEP(*(.vectors))}.reset 0x1000 : {KEEP(*(.reset))}.text 0x28000000 : {*(.text*) *(.rodata*)}.stock '+hex(0x514504+delta)+' : {KEEP(*(.stock))}.literal '+hex(0x514b78+delta)+' : {KEEP(*(.literal))}'
 ld+=' .space '+hex(0x514aec+delta)+' : {KEEP(*(.space))}.literal2 '+hex(0x514d94+delta)+' : {KEEP(*(.literal2))}'
 ld+=' .native_tex '+hex(base)+' : {KEEP(*(.native_tex))}.tiling '+hex(0x52262e+delta)+' : {KEEP(*(.tiling))}.tex_lit '+hex(0x4b178c+delta)+' : {KEEP(*(.tex_lit))}.tilingliteral '+hex(0x522f18+delta)+' : {KEEP(*(.tilingliteral))}'
 for a,n in cuts:ld+=' .cut_'+n+' '+hex(a+delta)+' : {KEEP(*(.cut_'+n+'))}'
 ld+=' .data 0x20001000 : {*(.data*)}.bss 0x20001000 : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}\n';(t/'module.ld').write_text(ld)
 harness=r'''
#include <stdint.h>
extern void audio_uart_nema_bind_tex_4b1298(uint32_t,uint32_t,uint32_t,uint32_t,int32_t,uint32_t,uint32_t);
volatile uint32_t *const cell=(void *)0x20074efc;
static uint32_t context[64],cl[15],next[15],tail[15],commands[128],nextcmd[128],tailcmd[128];
static volatile uint32_t current_case[9];
static uint32_t saved[64+15*3+128*3+64],events[64],eventcount,mode;
static void log(uint32_t a,uint32_t b,uint32_t c){events[eventcount++]=a;events[eventcount++]=b;events[eventcount++]=c;}
void cut_raw(uint32_t a,uint32_t b){log(1,a,b);}
void cut_sector(void *p){log(2,(uintptr_t)p,0);((uint32_t*)p)[5]=0;}
void cut_error(uint32_t e){log(3,e,0);((uint32_t*)*cell)[8]|=e;}
void *cut_alloc(uint32_t n){log(4,n,0);return mode==0?0:next;}
void cut_buffer(uint32_t *out,uint32_t pool,uint32_t size){log(5,pool,size);out[0]=size;out[1]=pool;out[2]=mode==1?0:(uintptr_t)nextcmd;out[3]=0x20008000+(mode==3);}
void cut_release(void *p){log(6,(uintptr_t)p,0);}
void cut_unbind(void){log(7,0,0);context[1]=0;}
void audio_uart_nema_register_emit_523e92(uint32_t a,uint32_t b){cut_raw(a,b);}
void audio_uart_nema_sector_rollover_5147b0(void*p){cut_sector(p);}
void audio_uart_nema_error_set_4b127c(uint32_t e){cut_error(e);}
void *audio_uart_nema_node_allocate_51416c(uint32_t n){return cut_alloc(n);}
void audio_uart_nema_buffer_create_514070(uint32_t *o,uint32_t p,uint32_t n){cut_buffer(o,p,n);}
void audio_uart_nema_cl_node_release_514178(void*p){cut_release(p);}
void audio_uart_nema_cl_unbind_5144ba(void){cut_unbind();}
static void host(unsigned op,uintptr_t x){register unsigned r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=x;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void hx(uint32_t v){char b[10];for(unsigned i=0;i<8;i++){unsigned n=(v>>((7-i)*4))&15;b[i]="0123456789abcdef"[n];}b[8]=32;b[9]=0;host(4,(uintptr_t)b);}
void fault_handler(void){for(unsigned i=0;i<9;i++)hx(current_case[i]);hx(*(volatile uint32_t*)0xe000ed28);hx(*(volatile uint32_t*)0xe000ed2c);hx(*(volatile uint32_t*)0xe000ed14);host(4,(uintptr_t)"FAULT_TEXTURE_GRAPH\n");unsigned out[2]={0x20026,12};host(0x20,(uintptr_t)out);for(;;){}}
static void init(unsigned flags,unsigned cap,unsigned used,unsigned sect,unsigned m,unsigned chain,unsigned seed,unsigned bound){
mode=m;eventcount=0;for(unsigned i=0;i<64;i++){context[i]=seed*0x01010101u;events[i]=0;}for(unsigned i=0;i<15;i++)cl[i]=next[i]=tail[i]=seed*0x01010101u;for(unsigned i=0;i<128;i++)commands[i]=nextcmd[i]=tailcmd[i]=seed*0x01010101u;
*cell=(uintptr_t)context;context[1]=bound?(uintptr_t)cl:0;cl[2]=(uintptr_t)commands;cl[4]=cap;cl[5]=used;cl[6]=flags;cl[8]=m==4?(uintptr_t)next:0;cl[9]=0;cl[11]=sect;
next[2]=(uintptr_t)nextcmd;next[3]=0x20008000;next[4]=128;next[5]=0;next[6]=chain?4:2;next[8]=chain?(uintptr_t)tail:0;next[9]=(uintptr_t)cl;
tail[2]=(uintptr_t)tailcmd;tail[3]=0x20009000;tail[4]=128;tail[5]=0;tail[6]=2;tail[8]=0;}
static unsigned snapshot(unsigned save){unsigned k=0,bad=0;uint32_t *regions[]={context,cl,next,tail,commands,nextcmd,tailcmd,events};unsigned sizes[]={64,15,15,15,128,128,128,64};for(unsigned r=0;r<8;r++)for(unsigned i=0;i<sizes[r];i++){uint32_t v=regions[r][i];if(save)saved[k]=v;else if(saved[k]!=v){if(!bad){hx(k);hx(saved[k]);hx(v);}bad++;}k++;}return bad;}
int main(void){unsigned count=0,failures=0;unsigned flags[]={0,2,32,34,8,10,40,42,0xffffffff},caps[]={0,4,16,32},useds[]={0,3,7},sectors[]={0,8,0xffffffff};
for(unsigned f=0;f<9;f++)for(unsigned c=0;c<4;c++)for(unsigned u=0;u<3;u++)for(unsigned s=0;s<3;s++)for(unsigned m=0;m<5;m++)for(unsigned chain=0;chain<2;chain++)for(unsigned seed=0;seed<2;seed++)for(unsigned bound=0;bound<2;bound++)for(unsigned fmt=0;fmt<10;fmt++){
uint32_t delta;if(flags[f]&32u){uint32_t sec=sectors[s];int32_t q=sec?((int32_t)useds[u]==(int32_t)0x80000000&&sec==0xffffffff?(int32_t)0x80000000:(int32_t)useds[u]/(int32_t)sec):0;delta=sec-useds[u]+sec*(uint32_t)q;}else delta=caps[c]-useds[u];if((flags[f]&2u)&&((int32_t)delta/2)-2>32)continue;
unsigned formats[]={0,11,18,22,41,57,76,77,78,127};unsigned requested=seed?0x80000000u:7u;current_case[0]=flags[f];current_case[1]=caps[c];current_case[2]=useds[u];current_case[3]=sectors[s];current_case[4]=m;current_case[5]=chain;current_case[6]=seed;current_case[7]=bound;current_case[8]=0;
init(flags[f],caps[c],useds[u],sectors[s],m,chain,seed?165:0,bound);((void(*)(uint32_t,uint32_t,uint32_t,uint32_t,int32_t,uint32_t,uint32_t))(uintptr_t)0x28100001)(0,0x20009003,requested,31,formats[fmt],0xffffffffu,chain?16u:0u);snapshot(1);
current_case[8]=1;init(flags[f],caps[c],useds[u],sectors[s],m,chain,seed?165:0,bound);audio_uart_nema_bind_tex_4b1298(0,0x20009003,requested,31,formats[fmt],0xffffffffu,chain?16u:0u);if(snapshot(0)){hx(formats[fmt]);hx(eventcount);for(unsigned q=0;q<12;q++){hx(saved[64+15*3+128*3+q]);hx(events[q]);}hx(flags[f]);hx(caps[c]);hx(useds[u]);hx(s);hx(m);hx(chain);hx(seed);hx(bound);host(4,(uintptr_t)"FAIL_TEXTURE_GRAPH\n");unsigned out[2]={0x20026,1};host(0x20,(uintptr_t)out);for(;;){} }count++;
}
host(4,(uintptr_t)(failures?"FAIL_TEXTURE_GRAPH\n":"PASS_TEXTURE_GRAPH\n"));hx(count);unsigned out[2]={0x20026,failures};host(0x20,(uintptr_t)out);for(;;){} }
''';(t/'harness.c').write_text(harness)
 flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding','-fno-builtin','-fno-vectorize','-fno-slp-vectorize'];objs=[]
 for p in [t/'start.S',t/'harness.c',S,space,texture,tiling]:
  o=t/(p.name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);objs.append(str(o))
 e=t/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(t/'module.ld'),'--defsym=audio_uart_nema_context_cell=0x20074efc',*objs,'-o',str(e)],check=True)
 from elftools.elf.elffile import ELFFile
 native_map=[]
 with e.open('rb') as f:
  elf=ELFFile(f)
  for section,a,z in [('.stock',0x514504,0x5147b0),('.space',0x514aec,0x514b76),('.native_tex',0x4b1298,0x4b146c),('.tiling',0x52262e,0x52266e)]:
   sec=elf.get_section_by_name(section);assert sec is not None,section;assert sec['sh_addr']==a+delta;assert sec.data()==blob[a-0x438000:z-0x438000],section;native_map.append({'section':section,'native_start':hex(a),'vma':hex(sec['sh_addr']),'sha256':hashlib.sha256(sec.data()).hexdigest()})
 (D/'native-map.json').write_text(json.dumps(native_map,indent=2)+'\n')
 import shutil;shutil.copyfile(e,D/'oracle-debug.elf')
 result=subprocess.run(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(e)],capture_output=True,text=True,timeout=45);output=result.stdout+result.stderr;print(result.returncode,output[-2500:]);(D/'last-qemu-observation.json').write_text(json.dumps({'returncode':result.returncode,'output':output},indent=2)+'\n');assert result.returncode==0 and 'PASS_TEXTURE_GRAPH' in output
 receipt={'status':'PASS_M55_QEMU_CONNECTED_TEXTURE_TILING_SPACE_EXTENSION','cases':int(re.search(r'PASS_TEXTURE_GRAPH\n([0-9a-f]{8})',output).group(1),16),'matrix_cases':129600,'selected_extension':'--selected' in sys.argv,'selected_space':True,'space_sha256':hashlib.sha256(space.read_bytes()).hexdigest(),'texture_sha256':hashlib.sha256(texture.read_bytes()).hexdigest(),'tiling_sha256':hashlib.sha256(tiling.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'native_body_sha256':hashlib.sha256(blob[0x514504-0x438000:0x5147b0-0x438000]).hexdigest(),'child_cuts':5,'limits':['Native texture,tiling,space,extension unchanged at common delta; actual inter-body calls preserved; allocation/rollover/error/release cuts and four context literals. Cortex-M55 supports native low-overhead padding loops. Full context/list/threecommand buffers/ordered child events compared; ten format branches and widths7/80000000,flags0/16,actual pair count3,allocation failures/reuse/chain traversal exercised.','Bus access trace, unbounded wrapped-capacity padding beyond recorded matrix; no extension fault proof claimed, invalid pointers, child mutation and real allocation/driver/hardware/layout remain open.']};(D/'qemu-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
