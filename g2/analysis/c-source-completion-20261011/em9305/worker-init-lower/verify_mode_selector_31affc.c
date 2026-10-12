#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_selector_31affc(uintptr_t,uint32_t);
static const uint8_t events22[14]={1,0,255,255,255,2,3,255,255,4,255,5,6,7};
static const uint8_t events102[10]={3,2,4,255,0,9,8,255,255,255};
static const uint8_t event12[42]={
 1,0,255,255,255,255,254,2,2,255,255,3,253,2,255,255,253,255,255,
 4,4,255,255,255,5,255,255,6,7,7,255,255,255,255,255,255,255,255,
 255,8,9,6};
int main(void)
{
 assert(mmap((void *)0x800000u,0x30000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 uint8_t *c=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(c!=(void *)-1);
 for(unsigned i=0;i<14u;i++)
  assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,22u+i)==events22[i]);
 c[635]=7u;
 for(unsigned i=0;i<10u;i++){
  unsigned expected=events102[i]==255u?255u:events102[i];
  if(i==8u)expected=7u;
  assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,102u+i)==expected);
 }
 for(unsigned code=1u;code<=42u;code++){
  *(volatile uint8_t *)(uintptr_t)0x802818u=(uint8_t)code;
  uint32_t want=event12[code-1u];
  if(want==253u)want=7u;
  if(want==254u)continue;
  assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,12u)==want);
 }
 *(volatile uint8_t *)(uintptr_t)0x802818u=7u;
 const uint8_t special_codes[]={1,2,8,9,12,14,20,21,29,30,35,36,37,40,41,42};
 const uint8_t special_wants[]={1,0,2,2,3,2,4,4,7,7,28,28,27,8,9,255};
 for(unsigned i=0;i<sizeof special_codes;i++){
  *(volatile uint8_t *)(uintptr_t)0x80281cu=special_codes[i];
  assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,12u)==special_wants[i]);
 }
 c[1]=3u;
 assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,112u)==255u);
 c[1]=0u;
 *(volatile uint32_t *)(c+652u)=1u;
 *(volatile uint32_t *)(c+656u)=99u;
 assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,112u)==0u);
 assert(*(volatile uint32_t *)(c+652u)==0u&&*(volatile uint32_t *)(c+656u)==0u);
 *(volatile uint32_t *)(c+652u)=1u<<5u;
 *(volatile uint32_t *)(c+656u)=99u;
 assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,112u)==5u);
 assert(*(volatile uint32_t *)(c+652u)==0u&&*(volatile uint32_t *)(c+656u)==0u);
 *(volatile uint32_t *)(c+644u)=1u<<7u;
 *(volatile uint32_t *)(c+648u)=99u;
 c[631]=1u;c[626]=1u;c[620]=0u;
 assert(opencfw_em9305_mode_selector_31affc((uintptr_t)c,112u)==7u);
 assert(*(volatile uint32_t *)(c+644u)==0u&&*(volatile uint32_t *)(c+648u)==0u);
 assert(c[631]==0u&&c[620]==1u&&c[635]==7u);
 return 0;
}
