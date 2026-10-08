/* Independent reconstruction from locked bootloader instructions.
 * 0x422416: copy configuration. 0x4222a0: low-byte selector dispatch.
 * Child implementations and concurrent publication remain outside this module. */
#include <stdint.h>
extern uint32_t opencfw_boot_startup_select4(uint32_t,uint32_t);
extern uint32_t opencfw_boot_startup_select5(uint32_t,uint32_t);
extern uint32_t opencfw_boot_startup_select6(uint32_t,uint32_t);
uint32_t opencfw_boot_startup_clock_descriptor(const void *src) {
 if (!src) return 6;
 const uint8_t *p=src; volatile uint8_t *q=(volatile uint8_t *)0x2000007c;
 for (unsigned i=0;i<20;i++) q[i]=p[i];
 return 0;
}
uint32_t opencfw_boot_startup_clock_select(uint32_t selector,uint32_t first,uint32_t second) {
 switch ((uint8_t)selector) {
 case 4:return opencfw_boot_startup_select4(first,second);
 case 5:return opencfw_boot_startup_select5(first,second);
 case 6:return opencfw_boot_startup_select6(first,second);
 default:return 7;
 }
}
