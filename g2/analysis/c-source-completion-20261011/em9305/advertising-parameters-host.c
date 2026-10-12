#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,packcalls,fail,mutate;
static uint32_t opencfw_em9305_ll_connection_gate_30e524(void){if(mutate)*(uint32_t*)0x805a94^=64;return gate;}
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t b){return (a&65535)*(b&65535);}
static uint64_t opencfw_em9305_controller_pack_address(uintptr_t a){packcalls++;uint64_t x=0;for(unsigned j=0;j<6;j++)x|=(uint64_t)*(uint8_t*)(a+j)<<(j*8);return x;}
/* Native30ce18..30cee0: captured capability, full interval/mode/address
 * validation and sparse live advertising-state projection. */
uint32_t opencfw_em9305_command_advertising_parameters_30ce18(uint32_t minimum,uint32_t maximum,uint32_t type,uint32_t own,uint32_t peer,uintptr_t address,uint32_t channels,uint32_t filter)
{
 uint32_t capabilities=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t gate=opencfw_em9305_ll_connection_gate_30e524();
 if(*(volatile uint8_t *)(uintptr_t)0x805a71u!=0u||gate==0u)return 12u;
 if(type!=1u){if(type>=5u||maximum>=0x4001u||minimum<32u||maximum<minimum)return 17u;}
 uint32_t maximum_own=(capabilities&64u)?3u:1u;
 if(own>maximum_own)return 17u;
 if(type==1u||type==4u||(own&2u)!=0u){if(peer>=2u||address==0u)return 17u;}
 if(channels-1u>=7u)return 17u;
 if(filter>=4u&&type!=4u&&type!=1u)return 17u;
 uint32_t upper=opencfw_em9305_config_limit_mpyuw(maximum,625u),lower=opencfw_em9305_config_limit_mpyuw(minimum,625u);
 uintptr_t state=0x805b88u;
 *(volatile uint8_t *)(state+21u)=(uint8_t)filter;
 *(volatile uint8_t *)(state+20u)=(uint8_t)channels;
 *(volatile uint8_t *)(state+10u)=(uint8_t)peer;
 *(volatile uint8_t *)(state+9u)=(uint8_t)own;
 *(volatile uint8_t *)(state+8u)=(uint8_t)type;
 *(volatile uint32_t *)(state+4u)=upper;
 *(volatile uint32_t *)state=lower;
 uint64_t value=opencfw_em9305_controller_pack_address(address);
 *(volatile uint32_t *)(state+12u)=(uint32_t)value;
 *(volatile uint32_t *)(state+16u)=(uint32_t)(value>>32u);
 return 0u;
}

static unsigned run(unsigned min,unsigned max,unsigned type,unsigned own,unsigned peer,unsigned channels,unsigned filter,unsigned cap,unsigned busy){
 uintptr_t addr=0x810000;for(unsigned j=0;j<6;j++)*(uint8_t*)(addr+j)=17*j+type;*(uint32_t*)0x805a94=cap;*(uint8_t*)0x805a71=busy==1;gate=busy!=2;mutate=1;memset((void*)0x805b88,0xa5,24);packcalls=0;
 unsigned want=0;
 if(busy)want=12;else if(type!=1&&(type>4||max>16384||min<32||max<min))want=17;else if(own>(cap?3:1))want=17;else if((type==1||type==4||(own&2))&&peer>1)want=17;else if(!channels||channels>7)want=17;else if(filter>3&&type!=1&&type!=4)want=17;
 uint8_t exp[24];memset(exp,0xa5,24);if(!want){*(uint32_t*)exp=(min&65535)*625;*(uint32_t*)(exp+4)=(max&65535)*625;exp[8]=type;exp[9]=own;exp[10]=peer;memcpy(exp+12,(void*)addr,6);exp[18]=exp[19]=0;exp[20]=channels;exp[21]=filter;}
 unsigned got=opencfw_em9305_command_advertising_parameters_30ce18(min,max,type,own,peer,addr,channels,filter);
 if(got!=want||memcmp(exp,(void*)0x805b88,24)||packcalls!=!want)fail++;return 1;
}
int main(void){if(mmap((void*)0x800000,131072,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;unsigned cases=0;
 for(unsigned t=0;t<6;t++)for(unsigned o=0;o<5;o++)for(unsigned p=0;p<3;p++)for(unsigned c=0;c<9;c++)for(unsigned f=0;f<6;f++)for(unsigned cap=0;cap<2;cap++)for(unsigned busy=0;busy<3;busy++)cases+=run(32,64,t,o,p,c,f,cap*64,busy);
 unsigned bounds[]={0,31,32,16384,16385,65535,65536,0xffffffffu};for(unsigned a=0;a<8;a++)for(unsigned b=0;b<8;b++)for(unsigned t=0;t<256;t++)for(unsigned cap=0;cap<2;cap++)cases+=run(bounds[a],bounds[b],t,0,0,1,0,cap*64,0);
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
