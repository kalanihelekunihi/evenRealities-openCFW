#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,busy,hvalid,cvalid,abusy,fail,calls;
static uintptr_t H,P,C,I;static uint32_t ident,num;
static uint32_t opencfw_em9305_ll_stream_gate_30e510(void){calls|=1;return gate;}
static uint32_t opencfw_em9305_ll_stream_control_decode_332a78(uintptr_t o,uintptr_t i){for(unsigned j=0;j<12;j+=2){uint32_t hi=*(uint8_t*)(i+j+1),lo=*(uint8_t*)(i+j);*(uint16_t*)(o+j)=(hi<<8)+lo;}return 12;}
static uint32_t opencfw_em9305_ll_stream_command_30b7ec(uintptr_t h,uintptr_t p,uintptr_t c){if(h!=H||p!=P||c!=C)fail++;calls|=2;return 177;}
static uint32_t opencfw_em9305_ll_stream_header_valid_332f04(uintptr_t h){if(h!=H)fail++;calls|=4;return hvalid;}
static uint32_t opencfw_em9305_ll_stream_control_valid_332f00(uintptr_t c){if(c!=C)fail++;calls|=8;return cvalid;}
static uint64_t opencfw_em9305_controller_pack_address(uintptr_t a){calls|=16;uint64_t x=0;for(unsigned j=0;j<6;j++)x|=(uint64_t)*(uint8_t*)(a+j)<<(8*j);return x;}
static uint32_t opencfw_em9305_ll_stream_address_busy_318200(uint32_t k,uint32_t lo,uint32_t hi){uint64_t x=0;for(unsigned j=0;j<6;j++)x|=(uint64_t)*(uint8_t*)(I+5+j)<<(8*j);if(k!=*(uint8_t*)(H+2)||lo!=(uint32_t)x||hi!=(uint32_t)(x>>32))fail++;calls|=32;return abusy;}
extern uint32_t opencfw_em9305_command_records_commit_3096a8(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_struct_commit_306cec(uintptr_t,uintptr_t);
/* Native30dc48..30dc6e: gate precedes ID validity; preserve captured arguments. */
uint32_t opencfw_em9305_command_records_apply_30dc48(uint32_t id,uint32_t count,uintptr_t records)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(id>239u)return 18u;
 return opencfw_em9305_command_records_commit_3096a8(id,count,records);
}
/* Native332abc..332b60: header projection and either one or packed controls. */
uint32_t opencfw_em9305_command_struct_decode_332abc(uintptr_t header,uintptr_t pairs,uintptr_t controls,uintptr_t input)
{
 uint32_t first=*(volatile uint8_t *)input;
 *(volatile uint8_t *)(header+9u)=(uint8_t)first;
 uint32_t second=*(volatile uint8_t *)(input+1u);
 *(volatile uint8_t *)(header+10u)=(uint8_t)second;
 *(volatile uint8_t *)header=*(volatile uint8_t *)(input+2u);
 *(volatile uint8_t *)(header+1u)=*(volatile uint8_t *)(input+3u);
 uint32_t kind=*(volatile uint8_t *)(input+4u);
 *(volatile uint32_t *)(header+4u)=(uint32_t)(input+5u);
 *(volatile uint8_t *)(header+2u)=(uint8_t)kind;
 *(volatile uint8_t *)(header+8u)=*(volatile uint8_t *)(input+11u);
 uintptr_t cursor=input+12u;
 if(first!=255u&&second!=255u){
  uint32_t high=*(volatile uint8_t *)(input+13u),low=*(volatile uint8_t *)(input+12u);
  *(volatile uint16_t *)pairs=(uint16_t)((high<<8)+low);
  high=*(volatile uint8_t *)(input+15u);low=*(volatile uint8_t *)(input+14u);
  *(volatile uint16_t *)(pairs+2u)=(uint16_t)((high<<8)+low);
  cursor=input+16u+opencfw_em9305_ll_stream_control_decode_332a78(controls,input+16u);
 }else{
  uint32_t packed=0u;
  for(uint32_t bit=0u;bit<8u&&packed<3u;++bit){
   uint32_t mask=*(volatile uint8_t *)(header+8u);
   if((mask&(1u<<bit))==0u)continue;
   uintptr_t pair=pairs+packed*4u;
   uint32_t high=*(volatile uint8_t *)(cursor+1u),low=*(volatile uint8_t *)cursor;
   *(volatile uint16_t *)pair=(uint16_t)((high<<8)+low);
   high=*(volatile uint8_t *)(cursor+3u);low=*(volatile uint8_t *)(cursor+2u);
   *(volatile uint16_t *)(pair+2u)=(uint16_t)((high<<8)+low);
   uint32_t size=opencfw_em9305_ll_stream_control_decode_332a78(controls+packed*12u,cursor+4u);
   cursor+=size+4u;++packed;
  }
 }
 return (uint8_t)(cursor-input);
}
/* Native30b974..30b9ee: guarded single command or existing packed stream path. */
uint32_t opencfw_em9305_command_struct_apply_30b974(uintptr_t header,uintptr_t pairs,uintptr_t controls)
{
 uint32_t id=*(volatile uint8_t *)(header+9u);
 if(id==255u)return opencfw_em9305_ll_stream_command_30b7ec(header,pairs,controls);
 uint32_t stream=*(volatile uint8_t *)(header+10u);
 if(stream==255u)return opencfw_em9305_ll_stream_command_30b7ec(header,pairs,controls);
 if(id>239u)return 66u;
 if(stream>=16u)return 18u;
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a74u;
 if(busy!=0u||gate==0u)return 12u;
 if(opencfw_em9305_ll_stream_header_valid_332f04(header)==0u)return 18u;
 if(opencfw_em9305_ll_stream_control_valid_332f00(controls)!=0u)return 18u;
 uint64_t address=opencfw_em9305_controller_pack_address(*(volatile uint32_t *)(header+4u));
 if(opencfw_em9305_ll_stream_address_busy_318200(*(volatile uint8_t *)(header+2u),(uint32_t)address,(uint32_t)(address>>32u))!=0u)return 11u;
 return opencfw_em9305_command_struct_commit_306cec(header,controls);
}

uint32_t opencfw_em9305_command_records_commit_3096a8(uint32_t i,uint32_t n,uintptr_t r){if(i!=ident||n!=num||r!=C)fail++;calls|=64;return 219;}
uint32_t opencfw_em9305_command_struct_commit_306cec(uintptr_t h,uintptr_t c){if(h!=H||c!=C)fail++;calls|=128;return 237;}
int main(void){
 if(mmap((void*)0x800000,131072,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;
 H=0x810000;P=H+64;C=H+128;I=H+256;unsigned cases=0;
 for(unsigned mask=0;mask<256;mask++)for(unsigned choice=0;choice<3;choice++)for(unsigned seed=0;seed<32;seed++){
  for(unsigned j=0;j<128;j++)*(uint8_t*)(I+j)=(uint8_t)(j*37+seed);
  *(uint8_t*)I=choice==1?255:seed;*(uint8_t*)(I+1)=choice==2?255:seed+1;*(uint8_t*)(I+11)=mask;
  memset((void*)H,0xa5,12);memset((void*)P,0xa5,12);memset((void*)C,0xa5,36);
  unsigned n=1;if(choice){n=0;for(unsigned bit=0;bit<8&&n<3;bit++)if(mask&(1<<bit))n++;}
  uint32_t result=opencfw_em9305_command_struct_decode_332abc(H,P,C,I);
  if(result!=12+16*n||*(uint8_t*)(H+9)!=*(uint8_t*)I||*(uint8_t*)(H+10)!=*(uint8_t*)(I+1)||*(uint32_t*)(H+4)!=(uint32_t)(I+5)||*(uint8_t*)(H+8)!=mask||*(uint8_t*)(H+3)!=0xa5||*(uint8_t*)(H+11)!=0xa5)fail++;
  for(unsigned j=0;j<3;j++)if(*(uint8_t*)(H+j)!=*(uint8_t*)(I+j+2))fail++;
  for(unsigned j=0;j<n;j++){if(memcmp((void*)(P+j*4),(void*)(I+12+j*16),4)||memcmp((void*)(C+j*12),(void*)(I+16+j*16),12))fail++;}
  for(unsigned j=n*4;j<12;j++)if(*(uint8_t*)(P+j)!=0xa5)fail++;
  for(unsigned j=n*12;j<36;j++)if(*(uint8_t*)(C+j)!=0xa5)fail++;
  cases++;
 }
 for(ident=0;ident<256;ident++)for(num=0;num<256;num++)for(gate=0;gate<2;gate++){
  calls=0;uint32_t want=!gate?12:ident>239?18:219;unsigned wc=1|(gate&&ident<=239?64:0);
  if(opencfw_em9305_command_records_apply_30dc48(ident,num,C)!=want||calls!=wc)fail++;cases++;
 }
 *(uint32_t*)(H+4)=I+5;*(uint8_t*)(H+2)=3;
 for(unsigned id=0;id<256;id++)for(unsigned st=0;st<256;st++)for(unsigned v=0;v<8;v++){
  *(uint8_t*)(H+9)=id;*(uint8_t*)(H+10)=st;gate=v!=0;busy=v==1;hvalid=v!=2;cvalid=v==3;abusy=v==4;*(uint8_t*)0x805a74=busy;calls=0;
  uint32_t want;unsigned wc;
  if(id==255||st==255){want=177;wc=2;}else if(id>239){want=66;wc=0;}else if(st>=16){want=18;wc=0;}else if(!gate||busy){want=12;wc=1;}else if(!hvalid){want=18;wc=5;}else if(cvalid){want=18;wc=13;}else if(abusy){want=11;wc=61;}else {want=237;wc=189;}
  if(opencfw_em9305_command_struct_apply_30b974(H,P,C)!=want||calls!=wc)fail++;cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
