#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <spl/spl.h>
volatile struct boot_info gx8002_stage1_boot_info;
int32_t gx8002_image_b_stage1_loader_10000d4c(void);
static uint32_t package,word,alternate;static unsigned calls,resets;
uint32_t gx8002_image_b_stage1_flash_read_10000fdc(uint32_t source,void*destination,uint32_t bytes){
 if(calls++==0){assert(bytes==4);assert(source==package+(alternate?0x323b0u:0x3000u));*(uint32_t*)destination=word;}
 else{assert(calls==2);assert(source==(alternate?word+0x323b4u:package+0x3000u+word+4u));assert((uintptr_t)destination==(alternate?0x20000000u:0x10003000u));assert(bytes==(alternate?0u:0x1408cu));}return 0xdeadbeefu;}
void gx8002_image_b_stage1_reset_10000100(void){assert(alternate&&calls==2);assert(*(uint32_t*)0x2002d3e4u==(uint32_t)(uintptr_t)gx8002_image_b_stage1_reset_10000100);++resets;}
void gx8002_image_b_stage2_reset_10003100(void){assert(!alternate&&calls==2);assert(*(uint32_t*)0x2002d3e4u==(uint32_t)(uintptr_t)gx8002_image_b_stage2_reset_10003100);++resets;}
int main(void){assert(mmap((void*)0x2002d000u,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x2002d000u);assert(mmap((void*)0x20033000u,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x20033000u);uint32_t edges[]={0,0x15400u,0xfffffffcu,0xffffffffu};for(unsigned b=0;b<2;b++)for(unsigned i=0;i<4;i++)for(unsigned j=0;j<4;j++){alternate=b;package=edges[i];word=edges[j];calls=resets=0;gx8002_stage1_boot_info.info.value=package;*(uint32_t*)0x20033ffcu=b?0xaabbccddu:0xaabbccdeu;assert(gx8002_image_b_stage1_loader_10000d4c()==0);assert(calls==2&&resets==1);}return 0;}
