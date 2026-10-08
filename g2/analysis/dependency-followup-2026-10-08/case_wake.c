/* Independent reconstruction of locked case 1.2.57, not copied vendor source.
 * Entry addresses 08005094 and 080050a8. Offline comparison module only. */
#include <stdint.h>
#define CR3 (*(volatile uint32_t *)0x40007008u)
#define CR4 (*(volatile uint32_t *)0x4000700cu)
void case_wake_disable(uint32_t arg) { CR3 = CR3 & ~(arg & 0x3fu); }
void case_wake_enable(uint32_t arg) {
    CR4 = (CR4 & ~(arg & 0x3fu)) | (arg >> 8);
    CR3 = CR3 | (arg & 0x3fu);
}
