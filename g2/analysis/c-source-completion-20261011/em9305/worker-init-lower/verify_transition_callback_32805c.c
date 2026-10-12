#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_callback_32805c(uintptr_t);
static uint32_t step,allocation;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes)
{assert(step==0u&&bytes==24u);step=1u;return allocation?0x804000u:0u;}
uint32_t opencfw_em9305_ll_event_enqueue(
    uintptr_t queue,uint32_t handler,uintptr_t event)
{assert(step==1u&&queue==0x8053f8u&&handler==0u&&event==0x804000u);
 assert(*(uint8_t *)(event+12u)==0xaau&&*(uint8_t *)event==0xbbu);
 assert(*(uint32_t *)(event+20u)==0x4444u);
 assert(*(uint32_t *)(event+16u)==0x3333u);
 assert(*(uint32_t *)(event+8u)==0x2222u);
 assert(*(uint32_t *)(event+4u)==0x1111u);
 step=2u;return 0u;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t bits)
{assert(step==2u&&handler==0x13u&&bits==1024u);step=3u;return 0xfeedu;}
static void reset(void)
{memset((void *)(uintptr_t)0x800000u,0,0x70000u);step=0u;allocation=1u;
 *(uint32_t *)(uintptr_t)0x80102cu=0x802000u;
 *(uint8_t *)(uintptr_t)0x802094u=3u;
 *(uint8_t *)(uintptr_t)0x802098u=1u;
 *(uint8_t *)(uintptr_t)0x802095u=12u;
 *(uint32_t *)(uintptr_t)0x80206cu=1u;
 *(uint8_t *)(uintptr_t)0x805becu=1u;
 *(uint8_t *)(uintptr_t)0x802096u=0xbbu;
 *(uint8_t *)(uintptr_t)0x802097u=0xaau;
 *(uint32_t *)(uintptr_t)0x802084u=0x1111u;
 *(uint32_t *)(uintptr_t)0x802088u=0x2222u;
 *(uint32_t *)(uintptr_t)0x80208cu=0x3333u;
 *(uint32_t *)(uintptr_t)0x802090u=0x4444u;
 *(uint8_t *)(uintptr_t)0x805b18u=0x13u;}
int main(void)
{void *p=mmap((void *)(uintptr_t)0x800000u,0x70000u,
    PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(p!=(void *)-1);
 reset();assert(opencfw_em9305_init_transition_callback_32805c(0x801000u)==0xfeedu);
 assert(step==3u);
 reset();allocation=0u;
 assert(opencfw_em9305_init_transition_callback_32805c(0x801000u)==0u);
 assert(step==1u);
 for(unsigned gate=0;gate<5u;gate++){
  reset();
  switch(gate){case 0:*(uint8_t *)(uintptr_t)0x802094u=2u;break;
   case 1:*(uint8_t *)(uintptr_t)0x802098u=0u;break;
   case 2:*(uint8_t *)(uintptr_t)0x802095u=11u;break;
   case 3:*(uint32_t *)(uintptr_t)0x80206cu=0u;break;
   default:*(uint8_t *)(uintptr_t)0x805becu=0u;break;}
  uint32_t expected=gate==0u?2u:(gate==2u?11u:0u);
  assert(opencfw_em9305_init_transition_callback_32805c(0x801000u)==expected);
  assert(step==0u);
 }
 return 0;}
