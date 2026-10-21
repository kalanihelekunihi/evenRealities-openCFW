/* Native 0x310cec..0x310d18: restore selected peripheral capture and
 * clear the selected low control bit. Return is the full native R0 mask,
 * not the resulting byte stored to MMIO. */
#include <stdint.h>
uint32_t opencfw_em9305_sleep_sync_restore(uint32_t incoming)
{
 (void)incoming;
 uint32_t index=*(volatile uint8_t *)(uintptr_t)0x80fd34u;
 uint32_t captured=*(volatile uint32_t *)(uintptr_t)(0xf00480u+index*4u);
 uintptr_t context=*(volatile uint32_t *)(uintptr_t)0x80fd2cu;
 *(volatile uint32_t *)(context+72u)=captured;
 index=*(volatile uint8_t *)(uintptr_t)0x80fd34u;
 uint32_t bit=1;
 __asm__ volatile("asl %0,%0,%1" : "+r"(bit) : "r"(index));
 uint32_t old=*(volatile uint8_t *)(uintptr_t)0xf0047au;
 uint32_t mask=(~bit)|240u;
 *(volatile uint8_t *)(uintptr_t)0xf0047au=(uint8_t)(old&mask);
 return mask;
}
