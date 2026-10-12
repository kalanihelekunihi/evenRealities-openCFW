#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_ll_stream_gate_30e510(void)
{
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a9eu;
 if(busy==0u) *(volatile uint8_t *)(uintptr_t)0x805a9fu=1u;
 return busy==0u;
}
uint32_t opencfw_em9305_address_busy_307cb8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==1u;}
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
 volatile uint8_t *bytes=(volatile uint8_t *)address;
 uint32_t second=bytes[1],third=bytes[2],first=bytes[0];
 uint32_t sixth=bytes[5],fourth=bytes[3],fifth=bytes[4];
 uint32_t low=first|(second<<8)|(third<<16)|(fourth<<24);
 uint32_t high=fifth|(sixth<<8);
 return ((uint64_t)high<<32)|low;
}
/* Native303674..3036b2: bounded byte index makes MPYUW stride12 exact in C. */
uint32_t opencfw_em9305_address_append_303674(uint32_t kind,uint32_t low,uint32_t high,uint32_t selector)
{
 uint32_t capacity=*(volatile uint8_t *)(uintptr_t)0x80160bu;
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80160au;
 if(count>=capacity)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805bfcu;
 *(volatile uint8_t *)(uintptr_t)0x80160au=(uint8_t)(count+1u);
 uintptr_t row=base+count*12u;
 *(volatile uint32_t *)(row+4u)=high;
 *(volatile uint32_t *)row=low;
 *(volatile uint8_t *)(row+8u)=(uint8_t)kind;
 *(volatile uint8_t *)(row+9u)=(uint8_t)selector;
 return 1u;
}
/* Native3036b4..3036fe: captured count, full-word address comparisons. */
uint32_t opencfw_em9305_address_contains_3036b4(uint32_t kind,uint32_t low,uint32_t high,uint32_t selector)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80160au;
 if(count==0u)return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805bfcu;
 for(uint32_t i=0u;i<count;++i,row+=12u){
  if(*(volatile uint8_t *)(row+8u)!=kind)continue;
  uint32_t upper=*(volatile uint32_t *)(row+4u),lower=*(volatile uint32_t *)row;
  if(((upper^high)|(lower^low))!=0u)continue;
  if(*(volatile uint8_t *)(row+9u)==selector)return 1u;
 }
 return 0u;
}
/* Native30aed4..30af30: gate/argument/busy/duplicate guards and fresh fields. */
uint32_t opencfw_em9305_command_address_add_30aed4(uintptr_t input)
{
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x805a77u;
 if(flag!=0u||gate==0u)return 12u;
 if(*(volatile uint8_t *)input>=2u)return 18u;
 if(*(volatile uint8_t *)(input+8u)>=16u)return 18u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 uintptr_t address=*(volatile uint32_t *)(input+4u);
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 uint32_t low=(uint32_t)packed,high=(uint32_t)(packed>>32u);
 uint32_t selector=*(volatile uint8_t *)(input+8u),kind=*(volatile uint8_t *)input;
 if(opencfw_em9305_address_contains_3036b4(kind,low,high,selector)!=0u)return 18u;
 selector=*(volatile uint8_t *)(input+8u);kind=*(volatile uint8_t *)input;
 return opencfw_em9305_address_append_303674(kind,low,high,selector)!=0u?0u:7u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t table=0x820000;*(uint32_t *)0x805bfc=table;
for(unsigned count=0;count<256;count++)for(unsigned cap=0;cap<256;cap++){memset((void *)table,0xa5,3072);*(uint8_t *)0x80160a=count;*(uint8_t *)0x80160b=cap;unsigned ok=count<cap;assert(opencfw_em9305_address_append_303674(0x1234,0x12345678,0xabcdef01,0x5678)==ok);assert(*(uint8_t *)0x80160a==(ok?count+1:count));uintptr_t row=table+count*12;if(ok){assert(*(uint32_t *)row==0x12345678&&*(uint32_t *)(row+4)==0xabcdef01&&*(uint8_t *)(row+8)==0x34&&*(uint8_t *)(row+9)==0x78&&*(uint16_t *)(row+10)==0xa5a5);assert(opencfw_em9305_address_contains_3036b4(0x34,0x12345678,0xabcdef01,0x78)==1);assert(opencfw_em9305_address_contains_3036b4(0x1234,0x12345678,0xabcdef01,0x78)==0);}else assert(*(uint32_t *)row==0xa5a5a5a5);cases++;}
uint8_t *in=(void *)0x810000;uint8_t *address=(void *)0x810020;for(unsigned j=0;j<6;j++)address[j]=j*37+11;*(uint32_t *)(in+4)=(uintptr_t)address;*(uint8_t *)0x805a9e=0;*(uint8_t *)0x805a77=0;*(uint8_t *)0x8051a4=0;
for(unsigned kind=0;kind<256;kind++)for(unsigned selector=0;selector<256;selector++){in[0]=kind;in[8]=selector;*(uint8_t *)0x80160a=0;*(uint8_t *)0x80160b=2;unsigned valid=kind<2&&selector<16;assert(opencfw_em9305_command_address_add_30aed4((uintptr_t)in)==(valid?0u:18u));assert(*(uint8_t *)0x80160a==valid);assert(opencfw_em9305_command_address_add_30aed4((uintptr_t)in)==18);cases++;}
for(unsigned mode=0;mode<16;mode++){in[0]=0;in[8]=0;*(uint8_t *)0x805a9e=mode&1;*(uint8_t *)0x805a77=(mode>>1)&1;*(uint8_t *)0x8051a4=(mode>>2)&1;*(uint8_t *)0x80160a=0;*(uint8_t *)0x80160b=(mode>>3)&1;unsigned blocked=mode&7;assert(opencfw_em9305_command_address_add_30aed4((uintptr_t)in)==(blocked?12u:mode&8?0u:7u));cases++;}
printf("PASS %u\n",cases);}
