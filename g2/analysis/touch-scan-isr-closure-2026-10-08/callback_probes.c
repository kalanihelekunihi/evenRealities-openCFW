/* Compiled synthetic callback bodies; ABI/order probes, not vendor logic. */
#include <stdint.h>
static volatile uint32_t *const log=(volatile uint32_t *)0x20009200u;
void touch_test_scan_end(void *arg){
 log[0]++;log[1]=(uint32_t)arg;log[2]=*(volatile uint32_t *)0x20003208u;log[3]=*(volatile uint32_t *)0x40000000u;
 register uint32_t residue __asm__("r0")=0xdeadbeefu;__asm__ volatile("" : "+r"(residue));
}
void touch_test_scan_start(void *arg){
 log[4]++;log[5]=(uint32_t)arg;log[6]=*(volatile uint16_t *)0x20003546u;log[7]=*(volatile uint32_t *)0x40000000u;
 if(log[15]&1u)*(volatile uint8_t *)0x20003561u=0;
 register uint32_t residue __asm__("r0")=0xdeadbeefu;__asm__ volatile("" : "+r"(residue));
}
