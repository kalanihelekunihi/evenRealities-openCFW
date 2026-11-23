/* Native 0x310cec..0x310d18: restore selected peripheral capture and
 * clear the selected low control bit. Return is the full native R0 mask,
 * not the resulting byte stored to MMIO. */
#include <stdint.h>
#include "em9305_ram.h"
uint32_t opencfw_em9305_sleep_sync_restore(uint32_t incoming)
{
 (void)incoming;
 uint32_t index=em9305_ram_80fd2c.u8_80fd34;
 uint32_t captured=*(volatile uint32_t *)(uintptr_t)(0xf00480u+index*4u);
 uintptr_t context=em9305_ram_80fd2c.u32_80fd2c;
 *(volatile uint32_t *)(context+72u)=captured;
 index=em9305_ram_80fd2c.u8_80fd34;
 uint32_t bit=1;
 bit<<=(index&31u);
 uint32_t old=*(volatile uint8_t *)(uintptr_t)0xf0047au;
 uint32_t mask=(~bit)|240u;
 *(volatile uint8_t *)(uintptr_t)0xf0047au=(uint8_t)(old&mask);
 return mask;
}
