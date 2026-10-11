/* Native 0x310a4c..0x310aa8. Explicit R0/R1 wide-return facade for
 * 0x30f2d8 and compiler runtime facade 0x302748 remain unresolved. */
#include <stdint.h>
extern uint64_t opencfw_em9305_sleep_sync_convert(uint32_t,uint32_t); /* 0x30f2d8 */
extern uint64_t opencfw_em9305_sleep_sync_divide(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x302748 */
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fd2cu; }
uint32_t opencfw_em9305_sleep_sync_update(uint32_t incoming)
{
 (void)incoming;
 uint32_t state=*(volatile uint32_t *)(context()+76u);
 if(state!=1) return state;
 *(volatile uint32_t *)(uintptr_t)0xf00820u=512;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf00814u=512;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf00808u=512;
 uint32_t captured=*(volatile uint32_t *)(context()+72u);
 uint32_t previous=*(volatile uint32_t *)(context()+68u);
 uint64_t converted=opencfw_em9305_sleep_sync_convert(captured-previous,captured);
 uint32_t divisor=*(volatile uint8_t *)(uintptr_t)0xf01804u+1u;
 uint64_t divided=opencfw_em9305_sleep_sync_divide((uint32_t)converted,(uint32_t)(converted>>32),divisor,0);
 *(volatile uint32_t *)(uintptr_t)0xf01814u=(uint32_t)divided;
 *(volatile uint32_t *)(uintptr_t)0xf01800u=1024;
 uintptr_t c=context(); *(volatile uint32_t *)(c+76u)=2;
 return (uint32_t)c;
}
