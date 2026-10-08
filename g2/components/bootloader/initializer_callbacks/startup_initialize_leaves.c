/* SPDX-License-Identifier: MIT. Independent locked-f89a4c46 reconstruction.
 * SCR and implementation register semantics beyond observed bytes unresolved. */
#include "startup_initialize_leaves.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
NI uint32_t opencfw_boot_startup_sleep_fields_write(uint32_t packed){
 if((W(0xe000ed14u)&0x20000u)||(W(0xe000ed14u)&0x10000u)){
  if((uint8_t)packed==3)return 1;
 }
 W(0xe001e300u)=((packed&255u)<<8)|(((packed>>8)&255u)<<4)|((packed>>16)&255u);
 return 0;
}
NI void opencfw_boot_startup_sleep_fields_read(uint8_t output[3]){
 uint32_t value=W(0xe001e300u);output[0]=(value>>8)&3;output[1]=(value>>4)&3;output[2]=value&3;
}
#define HOOK(name,offset) NI uint32_t name(void){if(W(0x20026e38u+offset))return ((uint32_t(*)(void))(uintptr_t)W(0x20026e38u+offset))();return 0;}
HOOK(opencfw_boot_startup_hook20,0x20u)
HOOK(opencfw_boot_startup_hook28,0x28u)
HOOK(opencfw_boot_startup_hook30,0x30u)
HOOK(opencfw_boot_startup_hook34,0x34u)
HOOK(opencfw_boot_startup_hook38,0x38u)
NI uint32_t opencfw_boot_startup_hook24(uint32_t first,uint32_t second){
 if(W(0x20026e5cu))return ((uint32_t(*)(uint32_t,uint32_t))(uintptr_t)W(0x20026e5cu))((uint8_t)first,(uint8_t)second);
 return 0;
}
