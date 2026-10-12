from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command2076 providers'):s.index('/* Authenticated command apply327630/327694')]
b=b.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=host_mpy(id);')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned active,allocation,lookups,sends,enters,exits,apply_calls;
static uint64_t words;static uint32_t args[6],clamp_input;
static uint32_t host_mpy(uint32_t id){assert(id<8);return id*912;}
static uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id<8);lookups++;return active;}
static uint64_t opencfw_em9305_ll_connection_query_words_307044(uint32_t id){assert(id==1);return words;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);*(uint8_t *)0x805b18=77;return allocation?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t msg){assert(handler==77&&msg==0x840000);sends++;return 999;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){enters++;return 15;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 16;}
static uint32_t opencfw_em9305_ll_signed_bounds_31026c(uintptr_t first,uintptr_t second){*(uint8_t *)first=0xfe;*(uint8_t *)second=0x33;return 0;}
static uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t value){clamp_input=value;return value;}
'''+b+r'''
uint32_t opencfw_em9305_command_apply_32754c(uint32_t id,uint32_t value){args[0]=id;args[1]=value;apply_calls++;return 71;}
uint32_t opencfw_em9305_command_apply_327630(uint32_t a,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){uint32_t v[]={a,c,d,e,f,g};memcpy(args,v,sizeof(v));apply_calls++;return 72;}
uint32_t opencfw_em9305_command_apply_327694(uint32_t id,uint32_t first,uint32_t second){args[0]=id;args[1]=first;args[2]=second;apply_calls++;return 73;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810022=5;*(uint32_t *)0x805c70=0x820000;active=1;unsigned cases=0;
for(unsigned flags=0;flags<256;flags++)for(unsigned kind=0;kind<256;kind++){*(uint8_t *)0x805a95=flags;unsigned expected=kind==1?1:kind==2?flags&1:kind==3||kind==4?(flags>>3)&1:0;assert(opencfw_em9305_command_kind_valid_31b768(kind)==expected);cases++;}
for(unsigned id=0;id<8;id++)for(unsigned kind=1;kind<=4;kind++)for(unsigned value=0;value<256;value++){unsigned index=kind==1?0:kind==2?1:kind==3?2:3;*(uint8_t *)(uintptr_t)(0x820000+id*912+332+index)=value;assert(opencfw_em9305_command_signed_query_306fa8(id,kind)==(uint32_t)(int32_t)(int8_t)(value==126?0:value));cases++;}
for(unsigned flags=0;flags<16;flags++)for(unsigned kind=0;kind<6;kind++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned alloc=0;alloc<2;alloc++){*(uint8_t *)0x805a95=flags;words=(uint64_t)(enabled?2:0)<<32;allocation=alloc;sends=0;unsigned valid=opencfw_em9305_command_kind_valid_31b768(kind);unsigned expected=!valid||!enabled?17:!alloc?7:0;assert(opencfw_em9305_command_30c65c(1,0x1234,kind)==expected);assert(sends==(expected==0));if(sends){assert(*(uint16_t *)0x840000==1&&*(uint16_t *)0x840002==0x2801&&*(uint8_t *)0x840004==0x34&&*(uint8_t *)0x840005==kind);}cases++;}
for(unsigned first=0;first<260;first++)for(unsigned second=0;second<260;second++)for(unsigned third=0;third<8;third++)for(unsigned fourth=0;fourth<8;fourth++){unsigned adjusted=first==255?0:second;unsigned invalid=first+adjusted>255||third>first||third<fourth||(int32_t)(first-adjusted)<(int32_t)(third+fourth);apply_calls=0;assert(opencfw_em9305_command_30da5c(1,first,second,third,fourth,0xdeadbeef)==(invalid?18:72));assert(apply_calls==!invalid);if(!invalid)assert(args[0]==1&&args[1]==first&&args[2]==adjusted&&args[3]==third&&args[4]==fourth&&args[5]==0xdeadbeef);cases++;}
for(unsigned enabled=0;enabled<2;enabled++)for(unsigned id=0;id<8;id++){active=enabled;apply_calls=lookups=0;unsigned ok=id<5&&enabled;assert(opencfw_em9305_command_30da2c(id,0xabcdef)==(ok?71:2));assert(lookups==(id<5)&&apply_calls==ok);apply_calls=lookups=0;assert(opencfw_em9305_command_30e000(id,0x123,0x456)==(ok?73:2));assert(lookups==(id<5)&&apply_calls==ok);cases+=2;}
active=1;for(unsigned kind=0;kind<6;kind++){*(uint8_t *)0x805a95=9;uint8_t first=0xaa,second=0xbb;enters=exits=0;unsigned valid=opencfw_em9305_command_kind_valid_31b768(kind);unsigned index=kind==1?0:kind==2?1:kind==3?2:3;*(uint8_t *)(uintptr_t)(0x820000+912+332+index)=0xf0;assert(opencfw_em9305_command_query_30bd34(1,kind,(uintptr_t)&first,(uintptr_t)&second)==(valid?0:17));assert(enters==1&&exits==1);if(valid)assert(first==0xf0&&second==0x33&&clamp_input==0xfffffff0);else assert(first==0xaa&&second==0xbb);cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-2076-providers-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('command-2076-providers-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Seven selected bodies; MPYUW normalized for ids0..7, genuine lower contracts controlled. Feature bytes, signed query sentinels, policy/guard/allocation and forwarding. No target DSP/runtime/hardware proof.'},indent=2)+'\n')
