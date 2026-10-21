/* Independent CMSIS wrappera888; kernel bodies remain explicit dependencies. */
#include "events.h"
#include <stddef.h>
extern int32_t xEventGroupSetBitsFromISR(void *,uint32_t,int32_t *);
extern uint32_t xEventGroupSetBits(void *,uint32_t);
uint32_t case_event_flags_set(void *id,uint32_t flags){
 if(!id || (flags&0xff000000u))return 0xfffffffcu;
 uint32_t ipsr;__asm volatile("mrs %0, ipsr":"=r"(ipsr));
 if(!ipsr)return xEventGroupSetBits(id,flags);
 int32_t yield=0;
 if(xEventGroupSetBitsFromISR(id,flags,&yield)==0)return 0xfffffffdu;
 if(yield)*(volatile uint32_t *)0xe000ed04u=0x10000000u;
 return flags;
}
