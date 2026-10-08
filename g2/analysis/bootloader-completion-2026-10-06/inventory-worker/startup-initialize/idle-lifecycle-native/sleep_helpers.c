/* Locked CPDLP config/get and nullable low-power callback wrappers. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
void cp_get(uint8_t *out){uint32_t v=W(0xe001e300);out[0]=(v>>8)&3;out[1]=(v>>4)&3;out[2]=v&3;}
uint32_t cp_set(uint32_t config){
 if((W(0xe000ed14)&0x20000)||(W(0xe000ed14)&0x10000))if((uint8_t)config==3)return 1;
 W(0xe001e300)=((config&255)<<8)|(((config>>8)&255)<<4)|((config>>16)&255);return 0;
}
uint32_t lp_enable(void){uint32_t p=W(0x20026e6c);return p?((uint32_t(*)(void))(uintptr_t)W(0x20026e6c))():0;}
uint32_t lp_disable(void){uint32_t p=W(0x20026e70);return p?((uint32_t(*)(void))(uintptr_t)W(0x20026e70))():0;}
