/* Native71714/71db6 engine-state setup. Preserve exact clear spans,
 * raw sentinel values,mode bytes and cached previous-state pointer. */
#include "native_gomore_engine_state.h"
#include <stdint.h>
#include <stddef.h>
extern void *memset(void *,int,size_t);
static void W(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void H(uintptr_t p,uint32_t o,uint16_t v){*(volatile uint16_t *)(p+o)=v;}
static void Y(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
void r1_gomore_native_engine_header_initialize(void *record)
{
 uintptr_t p=(uintptr_t)record;memset(record,0,0x1f8);
 W(p,0x10,0xbf800000u);W(p,0x6c,0xbf800000u);W(p,0xdc,0xbf800000u);W(p,0xe4,0xbf800000u);
 W(p,0x14,0xbf800000u);W(p,0x18,0xbf800000u);W(p,0x1c,0xbf800000u);
 for(uint32_t i=0;i<8;++i)W(p,0x140+i*4u,0xbf800000u);
 W(p,0x164,0xffffffffu);W(p,0x168,0xffffffffu);H(p,0x180,0);
 Y(p,0x94,1);Y(p,0xc,1);Y(p,0x34,1);
 W(p,0x5c,0xc97423f0u);W(p,0x58,0xc479c000u);W(p,0x54,0xc479c000u);W(p,0x60,0xbf800000u);W(p,0x64,0xbf800000u);Y(p,0x1c0,1);
}
void r1_gomore_native_engine_state_initialize(void *record,const void *previous)
{
 uintptr_t p=(uintptr_t)record;memset(record,0,0x3894);W(p,0x3890,(uint32_t)(uintptr_t)previous);r1_gomore_native_engine_header_initialize(record);
}
