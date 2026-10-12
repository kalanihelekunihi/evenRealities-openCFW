#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_guard_31a988(uintptr_t,uint32_t,uint32_t);
static unsigned expected(const uint8_t *p,unsigned selector,unsigned category,
                         unsigned ambient)
{
 switch(selector){
 case 1:return p[2]==1u?category!=0u:category!=4u;
 case 2:return category!=0u||p[2]!=1u||(p[544]&8u)!=0u;
 case 3:return p[category==2u?525u:526u]==0u;
 case 4:return (p[544]&32u)!=0u;
 case 5:return p[2]==0u?category!=0u:
               (category==4u?0u:(category!=0u?1u:(p[546]&1u)!=0u));
 case 6:return category==4u?0u:(category!=0u?1u:ambient!=0u);
 case 7:return (p[547]&4u)!=0u;
 case 8:case 9:return (p[548]&128u)!=0u;
 default:return 1u;
 }
}
int main(void)
{
 assert(mmap((void *)0x804000u,0x4000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 uint8_t *p=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(p!=(void *)-1);
 unsigned cases=0u;
 for(unsigned selector=0u;selector<11u;selector++)
 for(unsigned category=0u;category<8u;category++)
 for(unsigned pattern=0u;pattern<16u;pattern++){
  p[2]=(uint8_t)((pattern>>0u)&1u);
  p[525]=(uint8_t)((pattern>>1u)&1u);
  p[526]=(uint8_t)((pattern>>2u)&1u);
  p[544]=(uint8_t)(((pattern&1u)?8u:0u)|((pattern&2u)?32u:0u));
  p[546]=(uint8_t)((pattern>>2u)&1u);
  p[547]=(uint8_t)((pattern&4u)?4u:0u);
  p[548]=(uint8_t)((pattern&8u)?128u:0u);
  *(volatile uint8_t *)(uintptr_t)0x805a97u=(uint8_t)((pattern>>3u)&1u);
  assert(opencfw_em9305_mode_guard_31a988((uintptr_t)p,selector,category)==
         expected(p,selector,category,(pattern>>3u)&1u));
  ++cases;
 }
 assert(cases==1408u);
 return 0;
}
