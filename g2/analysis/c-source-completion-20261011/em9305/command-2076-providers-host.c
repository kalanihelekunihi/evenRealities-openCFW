#define _GNU_SOURCE
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
/* Authenticated command2076 providers and native kind/query helpers.
 * Signed query byte uses MPYUW; invalid kind must not read feature RAM. */
extern uint32_t opencfw_em9305_command_apply_32754c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_apply_327630(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_apply_327694(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_command_kind_valid_31b768(uint32_t kind)
{
 if(kind-3u<2u)return (*(volatile uint8_t *)(uintptr_t)0x805a95u>>3u)&1u;
 if(kind==1u)return 1u;
 if(kind==2u)return *(volatile uint8_t *)(uintptr_t)0x805a95u&1u;
 return 0u;
}
uint32_t opencfw_em9305_command_signed_query_306fa8(uint32_t id,uint32_t kind)
{
 uint32_t original_not_four=kind!=4u,offset;
 offset=host_mpy(id);
 if(kind==4u)kind=3u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t subtract=(kind!=3u)|original_not_four;
 uintptr_t address=base+offset+(uint32_t)(kind-subtract)+332u;
 uint32_t result=*(volatile uint8_t *)address;
 if(result==0x7eu)result=0u;
 return (uint32_t)(int32_t)(int8_t)result;
}
uint32_t opencfw_em9305_command_30c65c(uint32_t id,uint32_t value,uint32_t kind)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u))return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u)return 2u;
 if(opencfw_em9305_command_kind_valid_31b768(kind)==0u)return 17u;
 uint64_t words=opencfw_em9305_ll_connection_query_words_307044(id);
 if(((uint32_t)(words>>32u)&2u)==0u)return 17u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
 if(message==0u)return 7u;
 *(volatile uint16_t *)(message+2u)=0x2801u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+5u)=(uint8_t)kind;
 *(volatile uint8_t *)(message+4u)=(uint8_t)value;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
uint32_t opencfw_em9305_command_30da2c(uint32_t id,uint32_t value)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u))return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u)return 2u;
 return opencfw_em9305_command_apply_32754c(id,value);
}
uint32_t opencfw_em9305_command_30da5c(uint32_t id,uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t last)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u))return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u)return 2u;
 if(first==255u)second=0u;
 if(first+second>255u||third>first)return 18u;
 if(third<fourth)return 18u;
 if((int32_t)(first-second)<(int32_t)(third+fourth))return 18u;
 return opencfw_em9305_command_apply_327630(id,first,second,third,fourth,last);
}
uint32_t opencfw_em9305_command_30e000(uint32_t id,uint32_t first,uint32_t second)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u))return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u)return 2u;
 return opencfw_em9305_command_apply_327694(id,first,second);
}
uint32_t opencfw_em9305_command_query_30bd34(uint32_t id,uint32_t kind,uintptr_t first,uintptr_t second)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t status=2u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id<*(volatile uint8_t *)(config+34u)&&opencfw_em9305_ll_slot_active_30731c(id)!=0u){
  status=17u;
  if(opencfw_em9305_command_kind_valid_31b768(kind)!=0u){
   uint8_t lower;
   (void)opencfw_em9305_ll_signed_bounds_31026c((uintptr_t)&lower,second);
   uint32_t query=opencfw_em9305_command_signed_query_306fa8(id,kind);
   uint32_t clamped=opencfw_em9305_ll_signed_clamp_310230(query);
   status=0u;
   *(volatile uint8_t *)first=(uint8_t)clamped;
  }
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}

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
