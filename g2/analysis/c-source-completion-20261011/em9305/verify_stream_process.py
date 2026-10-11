from pathlib import Path
import subprocess,tempfile,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native317680..3177e8'):s.index('/* Native331100..33118c')];b=b.replace('*(volatile uint32_t *)(stream+4u)','parent_pointer')
for addr,name in [('805b38','exhaust_callback'),('8051e0','timing_callback'),('805adc','g_counter')]:
 for typ in ['uint32_t','uint8_t']:b=b.replace(f'*(volatile {typ} *)(uintptr_t)0x{addr}u',name)
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,13".*?;', 'offset=current*13u;', b)
# First native multiply uses the low byte of index, not fresh current.
b=b.replace('uint32_t offset;\n   offset=current*13u;', 'uint32_t offset;\n   offset=(uint8_t)index*13u;')
b=b.replace('*(volatile uint32_t *)(stream+228u)=(uint32_t)(uintptr_t)timing;', '*(volatile uint32_t *)(stream+228u)=(uint32_t)(uintptr_t)timing;published=(uintptr_t)timing;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t stream[256],parent[512],packet[4096],decoded[24],message[512];static uintptr_t parent_pointer,exhaust_callback,timing_callback;static uint8_t g_counter;static unsigned fail,released,queued,headers,callback_calls,exhaust_calls;static uintptr_t published;
struct opencfw_em9305_native_product_pair {uint32_t low,high;};
struct opencfw_em9305_native_product_pair opencfw_em9305_native_mpydu_329154(uint32_t a,uint32_t b){uint64_t p=(uint64_t)a*b;struct opencfw_em9305_native_product_pair r={(uint32_t)p,(uint32_t)(p>>32)};return r;}
uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return a*b;}
uintptr_t opencfw_em9305_ll_stream_packet_take_316e5c(void){return fail?0:(uintptr_t)packet;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==(uintptr_t)message);released++;return 0;}
uint32_t opencfw_em9305_wsf_critical_enter(void){return 0;}uint32_t opencfw_em9305_wsf_critical_exit(void){return 0;}
uint32_t opencfw_em9305_ll_segment_error_32322c(uint32_t e){assert(e==7);return 71;}
uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t p,uint32_t h,uintptr_t m){assert(p==(uintptr_t)(stream+8)&&h==9&&m==(uintptr_t)packet);queued++;return 91;}
uint32_t opencfw_em9305_ll_stream_segment_header_316f50(uintptr_t p,uint32_t n,uint32_t kind){assert(p==(uintptr_t)(packet+22+13*headers));unsigned total=*(uint16_t *)(decoded+14);unsigned unit=parent[4];unsigned consumed=headers*unit;unsigned remaining=total-consumed;assert(n==(remaining<unit?remaining:unit));assert(kind==(total?parent[30]?2:consumed+n!=total:0));((uint8_t *)p)[0]=kind;((uint8_t *)p)[1]=n;headers++;return 2;}
static uint32_t timing_cb(uintptr_t ctx,uintptr_t head,uintptr_t payload,uintptr_t trailer){assert(ctx==(uintptr_t)(stream+196)&&head==(uintptr_t)(packet+22+13*callback_calls)&&trailer==head+7&&payload==(uintptr_t)(message+16+4*callback_calls));uint64_t expected=3ull*((2ull<<32)|0xfffffffe)+callback_calls;assert(((uint32_t *)published)[0]==(uint32_t)expected&&((uint32_t *)published)[1]==expected>>32);callback_calls++;return callback_calls&1;}
static uint32_t exhaust_cb(uint32_t code,uintptr_t id,uintptr_t count){assert(code==1&&*(uint16_t *)id==9&&*(uint16_t *)count==1);exhaust_calls++;return 0;}

'''+b+r'''
int main(void){parent_pointer=(uintptr_t)parent;unsigned cases=0;for(unsigned len=0;len<65;len++)for(unsigned unit=1;unit<17;unit++)for(unsigned mode=0;mode<2;mode++){memset(packet,0xa5,sizeof packet);memset(stream,0,256);memset(parent,0,512);memset(decoded,0,24);parent[4]=unit;parent[28]=255;parent[30]=mode;parent[24]=3;*(uint32_t *)(parent+32)=0xfffffffe;*(uint32_t *)(parent+36)=2;decoded[0]=9;decoded[3]=2;*(uint16_t *)(decoded+14)=len;*(uint32_t *)(decoded+8)=1234;fail=released=queued=headers=0;assert(opencfw_em9305_ll_stream_process_317680((uintptr_t)stream,(uintptr_t)decoded,(uintptr_t)message)==91);unsigned count=len?(len+unit-1)/unit:1;assert(headers==count&&packet[11]==count&&queued==1&&!released&&packet[12]==255&&packet[10]==unit&&*(uint32_t *)(packet+16)==1234);assert(*(uint32_t *)packet==(uint32_t)(uintptr_t)message&&*(uint32_t *)(packet+4)==(uint32_t)(uintptr_t)(message+16));for(unsigned i=0;i<count;i++)assert(packet[20+13*i]==2&&packet[21+13*i]==0);if(len)assert(*(uint32_t *)(stream+228)==0);cases++;}for(unsigned len=1;len<65;len++){*(uint16_t *)(decoded+14)=len;parent[4]=4;parent[30]=0;timing_callback=(uintptr_t)timing_cb;headers=queued=callback_calls=0;fail=0;assert(opencfw_em9305_ll_stream_process_317680((uintptr_t)stream,(uintptr_t)decoded,(uintptr_t)message)==91);assert(callback_calls==(len+3)/4);for(unsigned i=0;i<callback_calls;i++)assert(packet[21+13*i]==(i%2==0?4:0));}timing_callback=0;fail=1;released=queued=0;g_counter=255;assert(opencfw_em9305_ll_stream_process_317680((uintptr_t)stream,(uintptr_t)decoded,(uintptr_t)message)==71&&released==1&&queued==0&&g_counter==0);exhaust_callback=(uintptr_t)exhaust_cb;for(unsigned blocked=0;blocked<2;blocked++){stream[108]=blocked;exhaust_calls=0;assert(opencfw_em9305_ll_stream_process_317680((uintptr_t)stream,(uintptr_t)decoded,(uintptr_t)message)==71&&exhaust_calls==!blocked);}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('stream-process-receipt.json').write_text(json.dumps({'cases_passed':n,'exhaustion_case_passed':1,'timing_callback_cases_passed':64,'exhaustion_callback_cases_passed':2,'scope':'Actual C zero/nonzero lengths0..64 units1..16 parentmode0/1, segmentation/ownership and exhaustion counter wrap. 64 callback-present cases verify timing carry, payload offsets and alternating status flags; two exhaustion callback enabled/blocked cases. ISA arithmetic/parent pointers/children normalized; no native ISA/layout/hardware proof.'},indent=2)+'\n');print('PASS',n,'EXHAUST',1)
