#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned limits,commons,counts,callback_calls,mode;static uintptr_t chosen;
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static void*opencfw_em9305_memset(void*p,uint32_t value,uint32_t bytes){if((uintptr_t)p!=chosen||value||bytes!=912)abort();memset(p,value,bytes);*(uint32_t*)0x805cac=0x804100;return p;}
static uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t slot,uintptr_t input){if(slot!=chosen||input!=chosen+(limits?566:574)||limits>1||*(uint16_t*)(slot+76)!=257||*(uint8_t*)slot!=1)abort();limits++;return limits==1?0x1234:0x5678;}
static uint32_t opencfw_em9305_command_count_30e4bc(void){counts++;if(*(uint8_t*)0x805a70!=255)abort();return 0;}
static uint32_t opencfw_em9305_common_request_30455c(uint32_t n){if(n!=1||*(uint8_t*)0x805a70)abort();commons++;*(uint32_t*)0x805c70=0x80d000;return 0;}
static uint32_t callback(uint32_t id,uintptr_t callee){if(callee!=(uintptr_t)callback||0x808000+id*912!=chosen||*(uint16_t*)(chosen+592)!=0x1234||*(uint16_t*)(chosen+590)!=0x5678)abort();callback_calls++;*(uint32_t*)0x805c70=0x80c000;*(uint32_t*)0x805cac=0x804200;*(uint8_t*)(chosen+548)=(mode&2)?2:0;return 0;}
#include "init-connection-allocate-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;unsigned caps[]={0,1,251,252,65535};
 for(unsigned count=0;count<5;count++)for(unsigned free=0;free<=count;free++)for(mode=0;mode<8;mode++)for(unsigned cap=0;cap<5;cap++){
 memset((void*)0x800000,0,0x10000);limits=commons=counts=callback_calls=0;
 *(uint32_t*)0x805cac=0x804000;*(uint8_t*)0x804022=count;*(uint32_t*)0x805c70=0x808000;
 for(unsigned i=0;i<count;i++){memset((void*)(uintptr_t)(0x808000+i*912),0xa5,912);*(uint8_t*)(uintptr_t)(0x808000+i*912)=i==free?0:1;}
 chosen=0x808000+free*912;*(uint8_t*)0x805b18=0x61;*(uint8_t*)0x805a70=255;
 *(uint32_t*)0x805a94=0x12345678;*(uint32_t*)0x805a98=0xabcdef02;*(uint32_t*)0x805a84=0x89abcdef;*(uint32_t*)0x805a88=0x1234;*(uint8_t*)0x805a85=(mode&4)?128:0;
 *(uint16_t*)0x804126=caps[cap];*(uint8_t*)0x804142=0x51;*(uint8_t*)0x804143=0x52;*(uint8_t*)0x804242=0x71;*(uint8_t*)0x804243=0x72;
 *(uint16_t*)0x805ab6=0x1122;*(uint16_t*)0x805ab8=0x3344;*(uint16_t*)0x805ac8=0x5566;*(uint8_t*)0x805aca=0x77;*(uint8_t*)0x805acb=0x88;*(uint32_t*)0x805acc=0xabcdef01;*(uint32_t*)0x805ad0=0x76543210;*(uint32_t*)0x805ad4=0xfedcba98;*(uint16_t*)0x805ad8=0x9876;*(uint8_t*)0x805aa8=0x99;
 if(mode&1){*(uint32_t*)0x805cd8=0x804300;*(uint32_t*)0x804300=(uint32_t)(uintptr_t)callback;}
 uintptr_t out=opencfw_em9305_init_connection_allocate_316c58();
 if(free==count){if(out||limits||commons||counts||callback_calls)abort();}
 else {
 unsigned capped=caps[cap]>251?251:caps[cap];unsigned optional=(mode&4)&&((mode&1)?(mode&2):1);
 if(out!=0x80d000+free*912||limits!=2||commons!=1||counts!=1||callback_calls!=!!(mode&1)||*(uint16_t*)(chosen+566)!=capped||*(uint16_t*)(chosen+568)!=capped*64+976||*(uint16_t*)(chosen+574)!=27||*(uint16_t*)(chosen+592)!=0x1234||*(uint16_t*)(chosen+590)!=0x5678||*(uint8_t*)(chosen+396)!=0x61||*(uint16_t*)(chosen+388)!=free||*(uint16_t*)(chosen+732)!=free||*(uint32_t*)(chosen+836)!=0x76543210||*(uint16_t*)(chosen+844)!=0x9876||*(uint8_t*)chosen!=1)abort();
 if(optional){if(*(uint8_t*)(chosen+778)!=((mode&1)?0x71:0x51)||*(uint8_t*)(chosen+779)!=((mode&1)?0x72:0x52)||*(uint8_t*)(chosen+770)!=1||*(uint8_t*)(chosen+561)!=255||*(uint8_t*)(chosen+564)!=255)abort();}
 else if(*(uint8_t*)(chosen+778)||*(uint8_t*)(chosen+779)||*(uint8_t*)(chosen+770))abort();
 for(unsigned i=0;i<count;i++)if(i!=free&&*(uint8_t*)(uintptr_t)(0x808000+i*912)!=1)abort();
 }
 cases++;
 }
 printf("PASS %u isolated allocator ordering/selection cases\n",cases);return 0;}
