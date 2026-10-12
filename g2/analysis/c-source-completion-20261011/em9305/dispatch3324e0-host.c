#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t Q,I,O;static unsigned initial,prefix,allocfail,mutation,fail,allocs,sends,children,powers,counts,sizes;static uint32_t allocsize;
static void *opencfw_em9305_memset(void*d,uint32_t v,uint32_t n){return memset(d,v,n);}
static unsigned fresh(void){unsigned commands[]={initial,0x2036,0x203b,0x203a,0x2080,0xffff};return commands[mutation];}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t opcode){if(opcode!=initial)fail++;allocs++;allocsize=n;*(uint16_t*)Q=fresh();return allocfail?0:O;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=O-5)fail++;sends++;return 37;}
static unsigned byte(unsigned j){return *(uint8_t*)(I+j);}
static uint32_t le(unsigned j,unsigned n){uint32_t v=0;for(unsigned k=0;k<n;k++)v|=byte(j+k)<<(8*k);return v;}
extern uint32_t opencfw_em9305_dispatch_3328c8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_field_30cee0(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_extended_packet_30d678(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_packet_30d5ac(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_data_30d580(uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_response_30d854(uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_enable_rows_30b6cc(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_clear_30ca00(uint32_t);
extern uint32_t opencfw_em9305_command_clear_all_30b118(void);
extern uint32_t opencfw_em9305_command_intervals_30db34(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_periodic_data_30dac8(uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_periodic_enable_30daf8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_packet_power_30bd8c(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_packet_count_30c7b0(uintptr_t);
extern uint32_t opencfw_em9305_command_packet_size_30c768(uintptr_t);
/* Native3324e0..3327f4: complete packet/periodic command projection,
 * sparse scratch records, fresh response opcode and status paths. */
uint32_t opencfw_em9305_dispatch_3324e0(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_3328c8(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2035u>=12u&&command!=0x207fu)return 0u;
 uint8_t scratch[32] __attribute__((aligned(4)));uint32_t status=0u,id=255u,size=1u;
 switch(command){
 case 0x2035u:id=*(volatile uint8_t *)input;status=opencfw_em9305_command_field_30cee0(id,input+1u);break;
 case 0x2036u:case 0x207fu:{
  if(command==0x2036u)(void)opencfw_em9305_memset(scratch,0u,32u);
  id=*(volatile uint8_t *)input;
  uint32_t first=*(volatile uint8_t *)(input+1u)+((uint32_t)*(volatile uint8_t *)(input+2u)<<8);
  uint32_t lower=*(volatile uint8_t *)(input+3u)+((uint32_t)*(volatile uint8_t *)(input+4u)<<8)+((uint32_t)*(volatile uint8_t *)(input+5u)<<16);
  uint32_t upper=*(volatile uint8_t *)(input+6u)+((uint32_t)*(volatile uint8_t *)(input+7u)<<8)+((uint32_t)*(volatile uint8_t *)(input+8u)<<16);
  uint32_t a=*(volatile uint8_t *)(input+9u),b=*(volatile uint8_t *)(input+10u),c=*(volatile uint8_t *)(input+11u);
  uint32_t extra=command==0x207fu?9u:7u;uint8_t tail[9];for(uint32_t j=0u;j<extra;++j)tail[j]=*(volatile uint8_t *)(input+18u+j);
  *(uint16_t *)(void *)scratch=(uint16_t)first;*(uint32_t *)(void *)(scratch+4u)=lower;*(uint32_t *)(void *)(scratch+8u)=upper;
  scratch[12]=(uint8_t)a;scratch[13]=(uint8_t)b;scratch[14]=(uint8_t)c;*(uint32_t *)(void *)(scratch+16u)=(uint32_t)(input+12u);
  for(uint32_t j=0u;j<extra;++j)scratch[20u+j]=tail[j];
  if(command==0x207fu){status=opencfw_em9305_command_extended_packet_30d678(id,(uintptr_t)scratch);*(volatile uint8_t *)(input+27u)=(uint8_t)status;}
  else{status=opencfw_em9305_command_packet_30d5ac(id,(uintptr_t)scratch);*(volatile uint8_t *)(input+25u)=(uint8_t)status;}
  size=2u;break;}
 case 0x2037u:case 0x2038u:{uint32_t d=*(volatile uint8_t *)(input+3u),c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;
  status=command==0x2037u?opencfw_em9305_command_data_30d580(a,b,c,d,input+4u):opencfw_em9305_command_response_30d854(a,b,c,d,input+4u);break;}
 case 0x2039u:{uint32_t count=*(volatile uint8_t *)(input+1u),enable=*(volatile uint8_t *)input,n=count<2u?count:2u;uintptr_t cursor=input+2u;
  for(uint32_t j=0u;j<n;++j){uint32_t high=*(volatile uint8_t *)(cursor+2u),low=*(volatile uint8_t *)(cursor+1u),a=*(volatile uint8_t *)cursor,b=*(volatile uint8_t *)(cursor+3u);scratch[j*6u]=(uint8_t)a;scratch[j*6u+4u]=(uint8_t)b;*(uint16_t *)(void *)(scratch+j*6u+2u)=(uint16_t)(low+(high<<8));cursor+=4u;}
  (void)opencfw_em9305_command_enable_rows_30b6cc(enable,count,(uintptr_t)scratch);return 1u;}
 case 0x203au:size=3u;break;
 case 0x203bu:size=2u;break;
 case 0x203cu:status=opencfw_em9305_command_clear_30ca00(*(volatile uint8_t *)input);break;
 case 0x203du:status=opencfw_em9305_command_clear_all_30b118();break;
 case 0x203eu:{uint32_t a=*(volatile uint8_t *)(input+1u)+((uint32_t)*(volatile uint8_t *)(input+2u)<<8),b=*(volatile uint8_t *)(input+3u)+((uint32_t)*(volatile uint8_t *)(input+4u)<<8),c=*(volatile uint8_t *)(input+5u)+((uint32_t)*(volatile uint8_t *)(input+6u)<<8);id=*(volatile uint8_t *)input;*(uint16_t *)(void *)scratch=a;*(uint16_t *)(void *)(scratch+2u)=b;*(uint16_t *)(void *)(scratch+4u)=c;status=opencfw_em9305_command_intervals_30db34(id,(uintptr_t)scratch);break;}
 case 0x203fu:{uint32_t c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;status=opencfw_em9305_command_periodic_data_30dac8(a,b,c,input+3u);break;}
 case 0x2040u:{uint32_t b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;(void)opencfw_em9305_command_periodic_enable_30daf8(a,b);return 1u;}
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,*(volatile uint16_t *)request);if(response==0u)return 1u;
 command=*(volatile uint16_t *)request;
 if(command==0x2036u||command==0x207fu){(void)opencfw_em9305_command_packet_power_30bd8c(id,(uintptr_t)scratch);*(volatile uint8_t *)response=(uint8_t)status;*(volatile uint8_t *)(response+1u)=scratch[0];}
 else if(command==0x203bu){scratch[0]=1u;uint32_t result=opencfw_em9305_command_packet_count_30c7b0((uintptr_t)scratch);*(volatile uint8_t *)response=(uint8_t)result;*(volatile uint8_t *)(response+1u)=scratch[0];}
 else if(command==0x203au){*(uint16_t *)(void *)scratch=31u;uint32_t result=opencfw_em9305_command_packet_size_30c768((uintptr_t)scratch);*(volatile uint8_t *)response=(uint8_t)result;*(volatile uint8_t *)(response+1u)=scratch[0];*(volatile uint8_t *)(response+2u)=scratch[1];}
 else if(command-0x2035u<12u||command==0x2080u)*(volatile uint8_t *)response=(uint8_t)status;
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}

uint32_t opencfw_em9305_dispatch_3328c8(uintptr_t q,uintptr_t i){if(q!=Q||i!=I)fail++;return prefix;}
uint32_t opencfw_em9305_command_field_30cee0(uint32_t a,uintptr_t p){if(a!=byte(0)||p!=I+1)fail++;children++;return 0x1a6;}
static uint32_t packet(uint32_t id,uintptr_t s,unsigned extra,unsigned zero){
 if(id!=byte(0)||*(uint16_t*)s!=le(1,2)||*(uint32_t*)(s+4)!=le(3,3)||*(uint32_t*)(s+8)!=le(6,3)||*(uint8_t*)(s+12)!=byte(9)||*(uint8_t*)(s+13)!=byte(10)||*(uint8_t*)(s+14)!=byte(11)||*(uint32_t*)(s+16)!=(uint32_t)(I+12))fail++;
 for(unsigned j=0;j<extra;j++)if(*(uint8_t*)(s+20+j)!=byte(18+j))fail++;
 if(zero){unsigned z[]={2,3,15,27,28,29,30,31};for(unsigned j=0;j<8;j++)if(*(uint8_t*)(s+z[j]))fail++;}
 children++;return 0x1a6;
}
uint32_t opencfw_em9305_command_extended_packet_30d678(uint32_t id,uintptr_t s){return packet(id,s,9,0);}
uint32_t opencfw_em9305_command_packet_30d5ac(uint32_t id,uintptr_t s){return packet(id,s,7,1);}
static uint32_t data(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uintptr_t p){if(a!=byte(0)||b!=byte(1)||c!=byte(2)||d!=byte(3)||p!=I+4)fail++;children++;return 0x1a6;}
uint32_t opencfw_em9305_command_data_30d580(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uintptr_t p){return data(a,b,c,d,p);}
uint32_t opencfw_em9305_command_response_30d854(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uintptr_t p){return data(a,b,c,d,p);}
uint32_t opencfw_em9305_command_enable_rows_30b6cc(uint32_t a,uint32_t n,uintptr_t s){if(a!=byte(0)||n!=byte(1))fail++;for(unsigned j=0;j<n&&j<2;j++){if(*(uint8_t*)(s+j*6)!=byte(2+j*4)||*(uint16_t*)(s+j*6+2)!=le(3+j*4,2)||*(uint8_t*)(s+j*6+4)!=byte(5+j*4))fail++;}children++;return 0x1a6;}
uint32_t opencfw_em9305_command_clear_30ca00(uint32_t a){if(a!=byte(0))fail++;children++;return 0x1a6;}
uint32_t opencfw_em9305_command_clear_all_30b118(void){children++;return 0x1a6;}
uint32_t opencfw_em9305_command_intervals_30db34(uint32_t a,uintptr_t s){if(a!=byte(0))fail++;for(unsigned j=0;j<3;j++)if(*(uint16_t*)(s+j*2)!=le(1+j*2,2))fail++;children++;return 0x1a6;}
uint32_t opencfw_em9305_command_periodic_data_30dac8(uint32_t a,uint32_t b,uint32_t c,uintptr_t p){if(a!=byte(0)||b!=byte(1)||c!=byte(2)||p!=I+3)fail++;children++;return 0x1a6;}
uint32_t opencfw_em9305_command_periodic_enable_30daf8(uint32_t a,uint32_t b){if(a!=byte(0)||b!=byte(1))fail++;children++;return 0x1a6;}
uint32_t opencfw_em9305_command_packet_power_30bd8c(uint32_t id,uintptr_t s){unsigned want=initial==0x2035||initial==0x2036||initial==0x207f||initial==0x203e?byte(0):255;if(id!=want)fail++;*(uint8_t*)s=0x81;powers++;return 73;}
uint32_t opencfw_em9305_command_packet_count_30c7b0(uintptr_t s){if(*(uint8_t*)s!=1)fail++;*(uint8_t*)s=0x82;counts++;return 0x187;}
uint32_t opencfw_em9305_command_packet_size_30c768(uintptr_t s){if(*(uint16_t*)s!=31)fail++;*(uint16_t*)s=0x1234;sizes++;return 0x188;}
static void run(unsigned seed){
 *(uint16_t*)Q=initial;for(unsigned j=0;j<64;j++)*(uint8_t*)(I+j)=(uint8_t)(seed+11*j);memset((void*)O,0xa5,64);allocs=sends=children=powers=counts=sizes=allocsize=0;
 unsigned recognized=(initial>=0x2035&&initial<=0x2040)||initial==0x207f,respond=recognized&&initial!=0x2039&&initial!=0x2040;unsigned child=recognized&&initial!=0x203a&&initial!=0x203b;
 uint32_t got=opencfw_em9305_dispatch_3324e0(Q,I);uint8_t expected[64];memset(expected,0xa5,64);unsigned ep=0,ec=0,es=0;
 uint32_t status=child?0xa6:0;unsigned op=fresh();
 if(!prefix&&respond&&!allocfail){if(op==0x2036||op==0x207f){expected[0]=status;expected[1]=0x81;ep=1;}else if(op==0x203b){expected[0]=0x87;expected[1]=0x82;ec=1;}else if(op==0x203a){expected[0]=0x88;expected[1]=0x34;expected[2]=0x12;es=1;}else if((op>=0x2035&&op<=0x2040)||op==0x2080)expected[0]=status;}
 unsigned size=initial==0x203a?3:(initial==0x2036||initial==0x207f||initial==0x203b)?2:1;
 if(got!=(prefix||recognized)||allocs!=(!prefix&&respond)||sends!=(!prefix&&respond&&!allocfail)||children!=(!prefix&&child)||powers!=ep||counts!=ec||sizes!=es||memcmp(expected,(void*)O,64)||(!prefix&&respond&&allocsize!=size))fail++;
 if(!prefix&&initial==0x2036&&byte(25)!=0xa6)fail++;if(!prefix&&initial==0x207f&&byte(27)!=0xa6)fail++;
}
int main(void){if(mmap((void*)0x20000000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x20000000)return 2;Q=0x20000000;I=Q+64;O=Q+256;unsigned cases=0;
 for(initial=0;initial<65536;initial++)for(prefix=0;prefix<2;prefix++)for(allocfail=0;allocfail<2;allocfail++)for(mutation=0;mutation<6;mutation++){run(3);cases++;}
 prefix=allocfail=mutation=0;for(initial=0x2035;initial<=0x2040;initial++)for(unsigned seed=0;seed<256;seed++){run(seed);cases++;}initial=0x207f;for(unsigned seed=0;seed<256;seed++){run(seed);cases++;}
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
