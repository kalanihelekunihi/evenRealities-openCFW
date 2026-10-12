#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned release,aux,mutate;
static uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==3);release++;return 99;}
static uint32_t opencfw_em9305_auxiliary_release_303ecc(void){assert(*(uint8_t *)0x8058dc==3);aux++;if(mutate){*(uint8_t *)0x8058e0=77;*(uint8_t *)0x8058dc=4;}return 98;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){*(uint8_t *)0x805a79-=1;return 0x805a79;}
static void *opencfw_em9305_memcpy(void *o,const void *i,uint32_t n){assert(n==20);return memcpy(o,i,n);}
static void *opencfw_em9305_memset(void *o,uint32_t v,uint32_t n){assert(v==0&&n==20);return memset(o,v,n);}
/* Native stop30b654..30b6bc: state1/kind3 fast release; otherwise
 * state1/2 transition3, optional report copy, then exact20-byte clear. */
uint32_t opencfw_em9305_command_stop_30b654(uintptr_t output)
{
 uintptr_t state=0x8058dcu;
 uint32_t captured=*(volatile uint8_t *)state;
 if(captured==1u){
  uint32_t kind=*(volatile uint8_t *)(state+185u);
  if(kind==3u){
   (void)opencfw_em9305_common_release_304588(3u);
   *(volatile uint8_t *)(uintptr_t)0x805a78u=0u;
   *(volatile uint8_t *)state=0u;
   (void)opencfw_em9305_command_count_down_30e48c();
   return 0u;
  }
 }
 if(captured==2u){
  *(volatile uint8_t *)state=3u;
  (void)opencfw_em9305_auxiliary_release_303ecc();
 }else if(captured==1u){
  *(volatile uint8_t *)state=3u;
 }else return 12u;
 uintptr_t report=state+4u;
 if(output!=0u)(void)opencfw_em9305_memcpy((void *)output,(const void *)report,20u);
 (void)opencfw_em9305_memset((void *)report,0u,20u);
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned counts[]={0,1,255};
for(unsigned state=0;state<6;state++)for(unsigned kind=0;kind<5;kind++)for(unsigned output=0;output<2;output++)for(unsigned ci=0;ci<3;ci++)for(mutate=0;mutate<2;mutate++){*(uint8_t *)0x8058dc=state;*(uint8_t *)0x805995=kind;*(uint8_t *)0x805a78=1;*(uint8_t *)0x805a79=counts[ci];for(unsigned j=0;j<20;j++)*(uint8_t *)(uintptr_t)(0x8058e0+j)=j+1;memset((void *)0x840000,0xa5,24);aux=release=0;unsigned quick=state==1&&kind==3;unsigned valid=state==1||state==2;assert(opencfw_em9305_command_stop_30b654(output?0x840000:0)==(valid?0:12)&&release==quick&&aux==(state==2));assert(*(uint8_t *)0x8058dc==(quick?0:state==2&&mutate?4:valid?3:state));assert(*(uint8_t *)0x805a79==(quick?(uint8_t)(counts[ci]-1):counts[ci])&&*(uint8_t *)0x805a78==(quick?0:1));for(unsigned j=0;j<20;j++){assert(*(uint8_t *)(uintptr_t)(0x8058e0+j)==(valid&&!quick?0:j+1));unsigned expected=output&&valid&&!quick?(state==2&&mutate&&j==0?77:j+1):0xa5;assert(*(uint8_t *)(uintptr_t)(0x840000+j)==expected);}assert(*(uint8_t *)0x840014==0xa5);cases++;}
printf("PASS %u\n",cases);}
