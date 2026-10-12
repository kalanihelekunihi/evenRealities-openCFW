#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t input[64],packet[32];static unsigned active,enters,exits,wakes,allocfail,allocs,sends,statuscalls,sstatus;static uint16_t request;static uint32_t allocated_len,allocated_op;
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t b){return (uint16_t)a*(uint16_t)b;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){enters++;return 1;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 0x12345678;}
static uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){if(id>7)abort();return active;}
static void *opencfw_em9305_memcpy(void*a,const void*b,uint32_t n){if(*(uint8_t*)0x805b80!=1)abort();return memcpy(a,b,n);}
static uintptr_t opencfw_em9305_wsf_wake_cell_313fc0(uintptr_t p){if(p!=0x805258||*(uint8_t*)p!=3)abort();wakes++;return 0x80606d;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t s){if(p!=(uintptr_t)&request)abort();statuscalls++;sstatus=s;return 77;}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t op){allocs++;allocated_len=n;allocated_op=op;return allocfail?0:(uintptr_t)(packet+8);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=(uintptr_t)(packet+3))abort();sends++;return 88;}
/* Native304838/304850/304880/304898: each provider reloads the table after
 * authentic MPYUW index*912; exact halfword field and native word return. */
static uint32_t opencfw_em9305_private_counter_field(uint32_t index,uint32_t field)
{
 uint32_t offset=opencfw_em9305_config_limit_mpyuw(index,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return *(volatile uint16_t *)(base+offset+field);
}
uint32_t opencfw_em9305_private_counter_304838(uint32_t index){return opencfw_em9305_private_counter_field(index,908u);}
uint32_t opencfw_em9305_private_counter_304850(uint32_t index){return opencfw_em9305_private_counter_field(index,906u);}
uint32_t opencfw_em9305_private_counter_304880(uint32_t index){return opencfw_em9305_private_counter_field(index,910u);}
uint32_t opencfw_em9305_private_counter_304898(uint32_t index){return opencfw_em9305_private_counter_field(index,904u);}
/* Native304994..3049a8: ST.AS227/226 are words at908/904, in that order. */
uint32_t opencfw_em9305_private_counter_reset_304994(uint32_t index)
{
 uint32_t offset=opencfw_em9305_config_limit_mpyuw(index,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=base+offset;
 *(volatile uint32_t *)(record+908u)=0u;
 *(volatile uint32_t *)(record+904u)=0u;
 return (uint32_t)record;
}
/* Native3049ac..3049c8: fullword count<=7, publish enable then count. */
uint32_t opencfw_em9305_private_mode_3049ac(uint32_t count,uint32_t enable)
{
 if(count>7u)return 18u;
 *(volatile uint8_t *)(uintptr_t)0x805f00u=(uint8_t)enable;
 *(volatile uint8_t *)(uintptr_t)0x8012fcu=(uint8_t)count;
 return 0u;
}
/* Native3049cc..3049fc: mark busy before64-byte copy; store operation3
 * before the existing wake provider, then return zero. */
uint32_t opencfw_em9305_private_data_3049cc(uintptr_t input)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805b80u!=0u)return 12u;
 *(volatile uint8_t *)(uintptr_t)0x805b80u=1u;
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x80527cu,(const void *)input,64u);
 *(volatile uint8_t *)(uintptr_t)0x805258u=3u;
 (void)opencfw_em9305_wsf_wake_cell_313fc0(0x805258u);
 return 0u;
}
/* Native304a00..304a60: critical capture and fourth output before exit.
 * Invalid slots zero all four halfwords; fourth store occurs before exit. */
uint32_t opencfw_em9305_private_stats_304a00(uint32_t index,uintptr_t first,uintptr_t second,uintptr_t third,uintptr_t fourth)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u),status=2u,value=0u;
 if(index<count&&opencfw_em9305_ll_slot_active_30731c(index)!=0u){
  *(volatile uint16_t *)first=(uint16_t)opencfw_em9305_private_counter_304898(index);
  *(volatile uint16_t *)second=(uint16_t)opencfw_em9305_private_counter_304850(index);
  *(volatile uint16_t *)third=(uint16_t)opencfw_em9305_private_counter_304838(index);
  value=opencfw_em9305_private_counter_304880(index);
  status=0u;
 }else{
  *(volatile uint16_t *)first=0u;
  *(volatile uint16_t *)second=0u;
  *(volatile uint16_t *)third=0u;
 }
 *(volatile uint16_t *)fourth=(uint16_t)value;
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
/* Native304a64..304a94: validated counter reset inside critical region. */
uint32_t opencfw_em9305_private_reset_304a64(uint32_t index)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u;
 if(index<*(volatile uint8_t *)(config+34u)&&opencfw_em9305_ll_slot_active_30731c(index)!=0u){
  (void)opencfw_em9305_private_counter_reset_304994(index);status=0u;
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
/* Native304afc..304bb0: all four vendor-private opcodes; allocation uses
 * command captured at native points, subsequent query tests fresh request. */
uint32_t opencfw_em9305_primary_private_304afc(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0xfe84u){
  uint32_t status=opencfw_em9305_private_reset_304a64(*(volatile uint8_t *)input);
  (void)opencfw_em9305_ll_status_event_331bf8(request,(uint8_t)status);return 1u;
 }
 if(command==0xfe82u){
  uint32_t status=opencfw_em9305_private_data_3049cc(input);
  (void)opencfw_em9305_ll_status_event_331bf8(request,(uint8_t)status);return 1u;
 }
 uint32_t id=0u,length=1u;
 if(command==0xfe81u){
  uint32_t count=*(volatile uint8_t *)input,enabled=*(volatile uint8_t *)(input+1u);
  (void)opencfw_em9305_private_mode_3049ac(count,enabled!=0u);
  command=*(volatile uint16_t *)request;
 }else if(command==0xfe83u){id=*(volatile uint8_t *)input;length=9u;}
 else return 0u;
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,command);
 if(packet==0u)return 1u;
 _Alignas(4) uint8_t scratch[8];
 if(*(volatile uint16_t *)request==0xfe83u){
  uint32_t result=opencfw_em9305_private_stats_304a00(id,(uintptr_t)scratch,(uintptr_t)(scratch+6u),(uintptr_t)(scratch+4u),(uintptr_t)(scratch+2u));
  *(volatile uint8_t *)packet=(uint8_t)result;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)scratch;
  uint32_t first=*(volatile uint16_t *)(scratch+6u),second=*(volatile uint16_t *)(scratch+4u),third=*(volatile uint16_t *)(scratch+2u),high=*(volatile uint8_t *)(scratch+1u);
  *(volatile uint8_t *)(packet+3u)=(uint8_t)first;
  *(volatile uint8_t *)(packet+5u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+7u)=(uint8_t)third;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)high;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(first>>8u);
  *(volatile uint8_t *)(packet+6u)=(uint8_t)(second>>8u);
  *(volatile uint8_t *)(packet+8u)=(uint8_t)(third>>8u);
 }
 (void)opencfw_em9305_ll_event_send(packet-5u);
 return 1u;
}
int main(void){if(mmap((void*)0x800000,0x30000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x80f000;*(uint32_t*)0x805c70=0x810000;unsigned n=0;for(unsigned i=0;i<64;i++)input[i]=i+11;for(unsigned count=0;count<256;count++)for(unsigned enable=0;enable<3;enable++){*(uint8_t*)0x805f00=91;*(uint8_t*)0x8012fc=92;unsigned r=opencfw_em9305_private_mode_3049ac(count,enable);if(r!=(count>7?18:0)||*(uint8_t*)0x805f00!=(count>7?91:enable)||*(uint8_t*)0x8012fc!=(count>7?92:count))abort();n++;}
for(unsigned busy=0;busy<256;busy++){*(uint8_t*)0x805b80=busy;memset((void*)0x80527c,0xa5,64);*(uint8_t*)0x805258=99;wakes=0;unsigned r=opencfw_em9305_private_data_3049cc((uintptr_t)input);if(r!=(busy?12:0)||wakes!=!busy||*(uint8_t*)0x805258!=(busy?99:3)||*(uint8_t*)0x805b80!=(busy?busy:1))abort();if(!busy&&memcmp((void*)0x80527c,input,64))abort();if(busy)for(unsigned i=0;i<64;i++)if(((uint8_t*)0x80527c)[i]!=0xa5)abort();n++;}
for(unsigned index=0;index<8;index++)for(unsigned count=0;count<8;count++)for(active=0;active<2;active++){*(uint8_t*)0x80f022=count;uintptr_t rec=0x810000+index*912;for(unsigned i=0;i<4;i++)*(uint16_t*)(rec+904+i*2)=0x1234+i;uint16_t out[4]={0xa5,0xa5,0xa5,0xa5};enters=exits=0;unsigned valid=index<count&&active;unsigned r=opencfw_em9305_private_stats_304a00(index,(uintptr_t)&out[0],(uintptr_t)&out[1],(uintptr_t)&out[2],(uintptr_t)&out[3]);if(r!=(valid?0:2)||enters!=1||exits!=1)abort();for(unsigned i=0;i<4;i++)if(out[i]!=(valid?0x1234+i:0))abort();n++;enters=exits=0;r=opencfw_em9305_private_reset_304a64(index);if(r!=(valid?0:2)||enters!=1||exits!=1)abort();for(unsigned i=0;i<4;i++)if(*(uint16_t*)(rec+904+i*2)!=(valid?0:0x1234+i))abort();n++;}
active=1;*(uint8_t*)0x80f022=4;input[0]=1;input[1]=2;for(unsigned op=0;op<65536;op++)for(allocfail=0;allocfail<2;allocfail++){request=op;memset(packet,0xa5,32);allocs=sends=statuscalls=wakes=enters=exits=0;*(uint8_t*)0x805b80=0;uintptr_t rec=0x810000+912;for(unsigned i=0;i<4;i++)*(uint16_t*)(rec+904+i*2)=0x1234+i;unsigned got=opencfw_em9305_primary_private_304afc((uintptr_t)&request,(uintptr_t)input);unsigned recognized=op>=0xfe81&&op<=0xfe84;if(got!=recognized)abort();if(op==0xfe81||op==0xfe83){if(allocs!=1||allocated_op!=op||allocated_len!=(op==0xfe81?1:9)||sends!=!allocfail||statuscalls)abort();uint8_t expected[32];memset(expected,0xa5,32);if(op==0xfe83&&!allocfail){uint8_t e[]={0,0x34,0x12,0x35,0x12,0x36,0x12,0x37,0x12};memcpy(expected+8,e,9);}if(memcmp(packet,expected,32))abort();}else if(op==0xfe82||op==0xfe84){if(allocs||sends||statuscalls!=1||sstatus)abort();}else if(allocs||sends||statuscalls||enters||wakes)abort();n++;}printf("PASS %u private fixtures\n",n);}
