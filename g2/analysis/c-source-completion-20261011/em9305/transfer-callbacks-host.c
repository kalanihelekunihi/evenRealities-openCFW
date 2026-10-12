#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls;
uint32_t opencfw_em9305_radio_cb_31dfd0(uintptr_t p){assert(p==0x880000&&*(uint8_t *)0x802a38==0&&*(uint8_t *)0x802a34==0);calls++;return 99;}
/* Native31df6c..31df8c: clear pending only when both source bytes are
 * nonzero; native R0 return is always source+379. */
uint32_t opencfw_em9305_radio_cb_31df6c(uintptr_t event)
{
 uintptr_t source=*(volatile uint32_t *)(event+36u);
 uintptr_t pending=source+379u;
 if(*(volatile uint8_t *)pending!=0u&&*(volatile uint8_t *)(source+380u)!=0u)
  *(volatile uint8_t *)pending=0u;
 return (uint32_t)pending;
}
/* Native31dc68..31dca0: clear shared flags before true tail callback. */
uint32_t opencfw_em9305_radio_cb_31dc68(uintptr_t event)
{
 uintptr_t source=*(volatile uint32_t *)(event+36u);
 uintptr_t pending=source+379u;
 if(*(volatile uint8_t *)pending!=0u&&*(volatile uint8_t *)(source+380u)!=0u)
  *(volatile uint8_t *)pending=0u;
 if(*(volatile uint8_t *)(source+1u)==0u) return (uint32_t)event;
 *(volatile uint8_t *)(uintptr_t)0x802a38u=0u;
 *(volatile uint8_t *)(uintptr_t)0x802a34u=0u;
 return opencfw_em9305_radio_cb_31dfd0(event);
}
/* Native31e7c8..31e7fc: status gate before event dereference; counter
 * wraps on halfword store but untruncated R0 is retained on plain path. */
uint32_t opencfw_em9305_radio_cb_31e7c8(uintptr_t event,uint32_t status)
{
 if(status!=0u) return (uint32_t)event;
 uintptr_t source=*(volatile uint32_t *)(event+36u);
 uint32_t mode=*(volatile uint8_t *)(source+341u);
 uint32_t count=*(volatile uint16_t *)(source+904u);
 *(volatile uint8_t *)(source+630u)=1u;
 uint32_t next=count+1u;
 *(volatile uint16_t *)(source+904u)=(uint16_t)next;
 if(mode==0u) return next;
 count=*(volatile uint16_t *)(uintptr_t)0x802a40u;
 *(volatile uint16_t *)(uintptr_t)0x802a40u=(uint16_t)(count+1u);
 return 0x802a40u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t event=0x880000,source=0x860000;*(uint32_t *)(event+36)=source;unsigned cases=0;
for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){*(uint8_t *)(source+379)=a;*(uint8_t *)(source+380)=c;assert(opencfw_em9305_radio_cb_31df6c(event)==source+379);assert(*(uint8_t *)(source+379)==(a&&c?0:a));cases++;}
for(unsigned mode=0;mode<256;mode++)for(unsigned a=0;a<2;a++)for(unsigned c=0;c<2;c++){*(uint8_t *)(source+379)=a;*(uint8_t *)(source+380)=c;*(uint8_t *)(source+1)=mode;*(uint8_t *)0x802a38=12;*(uint8_t *)0x802a34=13;calls=0;assert(opencfw_em9305_radio_cb_31dc68(event)==(mode?99:event));assert(calls==(mode!=0));assert(*(uint8_t *)(source+379)==(a&&c?0:a));assert(*(uint8_t *)0x802a38==(mode?0:12)&&*(uint8_t *)0x802a34==(mode?0:13));cases++;}
for(unsigned mode=0;mode<2;mode++)for(unsigned count=0;count<=65535;count++){*(uint8_t *)(source+341)=mode;*(uint8_t *)(source+630)=7;*(uint16_t *)(source+904)=count;*(uint16_t *)0x802a40=count;assert(opencfw_em9305_radio_cb_31e7c8(event,0)==(mode?0x802a40:count+1));assert(*(uint8_t *)(source+630)==1&&*(uint16_t *)(source+904)==(uint16_t)(count+1));assert(*(uint16_t *)0x802a40==(mode?(uint16_t)(count+1):count));cases++;}
assert(opencfw_em9305_radio_cb_31e7c8(0,1)==0);assert(opencfw_em9305_radio_cb_31e7c8(123,0xffffffff)==123);cases+=2;printf("PASS %u\n",cases);}
