#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t record[4096] __attribute__((aligned(4))),expected[4096],data[256],expectedbuffer[1024];static unsigned gate,found,durations,randoms,crcs;static uint32_t measured,lastsize,lastspacing,lastcount;
static uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){if(id!=7)abort();return found?(uintptr_t)record:0;}
static void*opencfw_em9305_memcpy(void*a,const void*b,size_t n){return memcpy(a,b,n);}
static uint32_t opencfw_em9305_pal_random_step(void){randoms++;return 0x89abcdef;}
static uint32_t opencfw_em9305_crc_update_304678(uint32_t seed,uint32_t count,uintptr_t input){if(seed!=0x89abcdef||input!=(uintptr_t)data)abort();crcs++;lastcount=count;return seed^count;}
static uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t req,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead){if(phy!=7||req||timing||extended!=1||mode!=2||overhead)abort();durations++;lastsize=size;lastspacing=spacing;return measured;}
static void set16(uint8_t*p,unsigned off,uint16_t v){memcpy(p+off,&v,2);}static void set32(uint8_t*p,unsigned off,uint32_t v){memcpy(p+off,&v,4);}
/* Native30904c..309242: all five periodic payload operations and native partial failure writes. */
uint32_t opencfw_em9305_command_periodic_data_lower_30904c(uint32_t id,uint32_t operation,uint32_t length,uintptr_t data)
{
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;if(*(volatile uint8_t *)(record+718u)==0u)return 12u;
 uint32_t busy=*(volatile uint8_t *)(record+369u);if((uint32_t)(operation-3u)>=2u){if(length==0u)return 18u;if(busy!=0u)return 12u;}
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t limit=*(volatile uint32_t *)(record+72u),spacing=*(volatile uint16_t *)(config+20u);uint32_t budget=*(volatile uint32_t *)(record+(busy==0u?712u:700u));if(limit>spacing)spacing=limit;uint32_t timing=0u;if(*(volatile uint8_t *)(record+804u)!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;if(callback!=0u)timing=((uint32_t (*)(void))callback)();}
 uintptr_t packet=record+1152u;uint32_t size=length;if((operation|2u)==2u)size=(uint16_t)(*(volatile uint16_t *)(packet-8u)+length);uint32_t phy=*(volatile uint8_t *)(record+63u);uint32_t duration=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,1u,2u,0u);if(budget<duration)return 69u;if(operation>=5u)return 18u;
 if(operation==0u||operation==2u){if(*(volatile uint8_t *)packet!=0u)return 18u;config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t old=*(volatile uint16_t *)(packet-8u),capacity=*(volatile uint16_t *)(config+16u);if(capacity<old+length){*(volatile uint8_t *)packet=0u;*(volatile uint16_t *)(packet-8u)=0u;return 69u;}}
 if(operation==3u){if(*(volatile uint8_t *)(record+368u)==1u){*(volatile uint8_t *)(packet+13u)=(uint8_t)length;(void)opencfw_em9305_memcpy((void *)(packet+16u),(const void *)data,length);uint32_t seed=opencfw_em9305_pal_random_step();uint32_t crc=opencfw_em9305_crc_update_304678(seed,length,data);*(volatile uint16_t *)(packet+14u)=(uint16_t)crc;*(volatile uint8_t *)(packet+12u)=1u;}else{uintptr_t destination=*(volatile uint32_t *)(packet-4u);(void)opencfw_em9305_memcpy((void *)destination,(const void *)data,length);*(volatile uint16_t *)(packet-8u)=(uint16_t)length;uint32_t seed=opencfw_em9305_pal_random_step();uint32_t crc=opencfw_em9305_crc_update_304678(seed,length,data);*(volatile uint8_t *)packet=1u;*(volatile uint16_t *)(packet-446u)=(uint16_t)crc;}}
 else if(operation==4u){if(length!=0u||*(volatile uint8_t *)(record+368u)==0u||*(volatile uint16_t *)(packet-8u)==0u)return 18u;if(*(volatile uint8_t *)(packet+12u)!=0u&&*(volatile uint8_t *)(packet+13u)==0u)return 18u;uint32_t seed=opencfw_em9305_pal_random_step();uint32_t crc=opencfw_em9305_crc_update_304678(seed,0u,data);*(volatile uint8_t *)packet=1u;*(volatile uint16_t *)(packet-446u)=(uint16_t)crc;}
 else {if(*(volatile uint8_t *)(record+368u)!=0u)return 12u;if(length==0u)return 18u;uintptr_t destination=*(volatile uint32_t *)(packet-4u);if(operation==0u||operation==2u){destination+=*(volatile uint16_t *)(packet-8u);(void)opencfw_em9305_memcpy((void *)destination,(const void *)data,length);uint32_t total=*(volatile uint16_t *)(packet-8u)+length;if(operation==0u)*(volatile uint8_t *)packet=0u;*(volatile uint16_t *)(packet-8u)=(uint16_t)total;if(operation!=0u){uint32_t seed=opencfw_em9305_pal_random_step();uint32_t crc=opencfw_em9305_crc_update_304678(seed,length,data);*(volatile uint8_t *)packet=1u;*(volatile uint16_t *)(packet-446u)=(uint16_t)crc;}}else{(void)opencfw_em9305_memcpy((void *)destination,(const void *)data,length);*(volatile uint16_t *)(packet-8u)=(uint16_t)length;*(volatile uint8_t *)packet=0u;}}
 *(volatile uint8_t *)(record+1156u)=1u;return 0u;
}
/* Native30dac8..30daf6: saved arguments and gate-before-id/operation validation. */
uint32_t opencfw_em9305_command_periodic_data_30dac8(uint32_t id,uint32_t operation,uint32_t length,uintptr_t data)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;if(id>239u)return 48u;if(operation>=5u)return 18u;return opencfw_em9305_command_periodic_data_lower_30904c(id,operation,length,data);}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;for(unsigned i=0;i<256;i++)data[i]=i*17+11;uint64_t cases=0;
for(unsigned op=0;op<5;op++){for(unsigned len=0;len<256;len++){for(unsigned scenario=0;scenario<16;scenario++){memset(record,0xa5,4096);memset((void*)0x810000,0xa5,1024);memcpy(expectedbuffer,(void*)0x810000,1024);gate=scenario!=0;found=scenario!=1;record[718]=scenario!=2;record[369]=scenario==3;record[804]=0;record[63]=7;record[368]=scenario==4?1:scenario==5?2:0;record[1152]=scenario==6?1:0;record[1164]=scenario==9?1:0;record[1165]=scenario==9?0:7;unsigned old=scenario==7?0:13;set16(record,1144,old);set32(record,1148,0x810000);set32(record,72,scenario==10?0x10000022:31);set32(record,712,100);set32(record,700,50);*(uint32_t*)0x805cac=0x80f000;*(uint16_t*)0x80f014=33;*(uint16_t*)0x80f010=scenario==8?14:1024;measured=scenario==11?101:scenario==12?51:0;durations=randoms=crcs=0;memcpy(expected,record,4096);
unsigned early=!gate?12:!found?66:scenario==2?12:(op!=3&&op!=4&&!len)?18:(op!=3&&op!=4&&scenario==3)?12:0;unsigned reached=!early;unsigned error=early;unsigned checksum=0;unsigned size=(op==0||op==2)?(uint16_t)(old+len):len;
if(!error&&measured>(scenario==3?50:100))error=69;
if(!error&&(op==0||op==2)){if(scenario==6)error=18;else if((scenario==8?14:1024)<old+len){error=69;expected[1152]=0;set16(expected,1144,0);}}
if(!error){if(op==3){if(scenario==4){expected[1165]=len;memcpy(expected+1168,data,len);set16(expected,1166,0xcdef^len);expected[1164]=1;}else{memcpy(expectedbuffer,data,len);set16(expected,1144,len);expected[1152]=1;set16(expected,706,0xcdef^len);}checksum=1;}
else if(op==4){if(len||!record[368]||!old||(record[1164]&&!record[1165]))error=18;else{expected[1152]=1;set16(expected,706,0xcdef);checksum=1;}}
else if(record[368]){error=12;}else{if(op==1){memcpy(expectedbuffer,data,len);set16(expected,1144,len);expected[1152]=0;}else{memcpy(expectedbuffer+old,data,len);set16(expected,1144,old+len);expected[1152]=op==2;if(op==2){set16(expected,706,0xcdef^len);checksum=1;}}}
if(!error)expected[1156]=1;}
unsigned r=opencfw_em9305_command_periodic_data_30dac8(7,op,len,(uintptr_t)data);if(r!=error||durations!=reached||randoms!=checksum||crcs!=checksum||(checksum&&lastcount!=len)||memcmp(record,expected,4096)||memcmp((void*)0x810000,expectedbuffer,1024)||(reached&&(lastsize!=size||lastspacing!=(scenario==10?34:33)))){fprintf(stderr,"FAIL %u %u %u ret%u/%u\n",op,len,scenario,r,error);return 1;}cases++;}}}printf("PASS %llu\n",(unsigned long long)cases);return 0;}
