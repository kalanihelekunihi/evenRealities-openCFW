#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned duplicate,fail,allocs,sends;
static uintptr_t input=0x810000,address=0x810020;
static _Alignas(4) uint8_t message[24];
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==24);allocs++;return fail?0:(uintptr_t)message;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==9&&p==(uintptr_t)message);sends++;return 77;}
uint32_t opencfw_em9305_ll_stream_gate_30e510(void)
{
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a9eu;
 if(busy==0u) *(volatile uint8_t *)(uintptr_t)0x805a9fu=1u;
 return busy==0u;
}
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
 volatile uint8_t *bytes=(volatile uint8_t *)address;
 uint32_t second=bytes[1],third=bytes[2],first=bytes[0];
 uint32_t sixth=bytes[5],fourth=bytes[3],fifth=bytes[4];
 uint32_t low=first|(second<<8)|(third<<16)|(fourth<<24);
 uint32_t high=fifth|(sixth<<8);
 return ((uint64_t)high<<32)|low;
}
uint32_t opencfw_em9305_command_duplicate_307c5c(uint32_t role,uint32_t kind,uint32_t low,uint32_t high){assert(role==*(uint8_t *)(input+1)&&kind==*(uint8_t *)(input+2));uint64_t packed=opencfw_em9305_controller_pack_address(address);assert(low==(uint32_t)packed&&high==packed>>32);return duplicate;}
/* Native307ca8..307cb8: product state equals0. */
uint32_t opencfw_em9305_command_idle_307ca8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==0u;}
/* Native3213b0..3213d0: six byte rows summed, low8 return. */
uint32_t opencfw_em9305_command_count_3213b0(void)
{
 uint32_t sum=0u;
 for(uint32_t i=0u;i<6u;++i)sum+=*(volatile uint8_t *)(uintptr_t)(0x803d78u+i*784u);
 return sum&255u;
}
extern uint32_t opencfw_em9305_command_duplicate_307c5c(uint32_t,uint32_t,uint32_t,uint32_t);
/* Native30c488..30c54c: full create guards and24-byte command projection. */
uint32_t opencfw_em9305_command_create_30c488(uintptr_t input)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(*(volatile uint8_t *)(input+2u)>=2u)return 18u;
 if(*(volatile uint8_t *)(input+1u)>=16u)return 18u;
 if(*(volatile uint16_t *)(input+8u)>499u)return 18u;
 if(*(volatile uint8_t *)input>=8u)return 18u;
 uint32_t timing=*(volatile uint16_t *)(input+10u);
 if((uint16_t)(timing-16385u)<49161u)return 18u;
 if(*(volatile uint8_t *)(input+12u)==31u)return 12u;
 if(opencfw_em9305_command_idle_307ca8()==0u)return 12u;
 uintptr_t address=*(volatile uint32_t *)(input+4u);
 uint32_t kind=*(volatile uint8_t *)(input+2u),role=*(volatile uint8_t *)(input+1u);
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 if(opencfw_em9305_command_duplicate_307c5c(role,kind,(uint32_t)packed,(uint32_t)(packed>>32u))!=0u)return 11u;
 if(opencfw_em9305_command_count_3213b0()>=6u)return 7u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(24u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=267u;
 address=*(volatile uint32_t *)(input+4u);
 packed=opencfw_em9305_controller_pack_address(address);
 kind=*(volatile uint8_t *)(input+2u);role=*(volatile uint8_t *)(input+1u);
 *(volatile uint32_t *)(message+12u)=(uint32_t)(packed>>32u);
 *(volatile uint32_t *)(message+8u)=(uint32_t)packed;
 *(volatile uint8_t *)(message+7u)=(uint8_t)kind;
 *(volatile uint8_t *)(message+6u)=(uint8_t)role;
 *(volatile uint32_t *)(message+16u)=*(volatile uint32_t *)(input+8u);
 uint32_t flags=*(volatile uint8_t *)input,last=*(volatile uint8_t *)(input+12u);
 *(volatile uint8_t *)(message+21u)=(uint8_t)last;
 uint32_t bit1=(flags>>1u)&1u;
 *(volatile uint8_t *)(message+5u)=(uint8_t)bit1;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+20u)=(uint8_t)(bit1?0u:(flags>>2u)&1u);
 *(volatile uint8_t *)(message+4u)=(uint8_t)(flags&1u);
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

static void setup(void){memset((void *)input,0,16);*(uint8_t *)(input+1)=7;*(uint8_t *)(input+2)=1;*(uint32_t *)(input+4)=address;*(uint16_t *)(input+8)=499;*(uint16_t *)(input+10)=10;*(uint8_t *)(input+12)=30;*(uint8_t *)0x805a9e=0;*(uint8_t *)0x8051a4=0;*(uint8_t *)0x805b18=9;for(unsigned i=0;i<6;i++)*(uint8_t *)(uintptr_t)(0x803d78+i*784)=0;memset(message,0xa5,24);allocs=sends=duplicate=fail=0;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);for(unsigned j=0;j<6;j++)*(uint8_t *)(address+j)=j*37+11;unsigned cases=0;
for(unsigned timing=0;timing<65536;timing++){setup();*(uint16_t *)(input+10)=timing;*(uint8_t *)input=timing&7;unsigned valid=timing>=10&&timing<=16384;assert(opencfw_em9305_command_create_30c488(input)==(valid?0u:18u)&&allocs==valid&&sends==valid);if(valid){uint64_t packed=opencfw_em9305_controller_pack_address(address);unsigned flags=timing&7;assert(*(uint16_t *)(message+2)==267&&message[4]==(flags&1)&&message[5]==((flags>>1)&1)&&message[6]==7&&message[7]==1&&*(uint32_t *)(message+8)==(uint32_t)packed&&*(uint32_t *)(message+12)==packed>>32&&*(uint32_t *)(message+16)==(499u|(timing<<16))&&message[20]==((flags&2)?0:(flags>>2)&1)&&message[21]==30&&message[0]==0xa5&&message[1]==0xa5&&message[22]==0xa5&&message[23]==0xa5);}cases++;}
for(unsigned which=0;which<4;which++)for(unsigned value=0;value<256;value++){setup();unsigned off=which==0?0:which==1?1:which==2?2:12;*(uint8_t *)(input+off)=value;unsigned result=which==0&&value>=8?18:which==1&&value>=16?18:which==2&&value>=2?18:which==3&&value==31?12:0;assert(opencfw_em9305_command_create_30c488(input)==result&&sends==(result==0));cases++;}
for(unsigned count=0;count<256;count++){setup();*(uint8_t *)0x803d78=count;unsigned want=count>=6?7:0;assert(opencfw_em9305_command_create_30c488(input)==want&&sends==(want==0));cases++;}
for(unsigned mode=0;mode<16;mode++){setup();*(uint8_t *)0x805a9e=mode&1;*(uint8_t *)0x8051a4=(mode>>1)&1;duplicate=(mode>>2)&1;fail=(mode>>3)&1;unsigned want=(mode&3)?12:duplicate?11:0;assert(opencfw_em9305_command_create_30c488(input)==want&&sends==(want==0&&!fail));cases++;}
printf("PASS %u\n",cases);}
