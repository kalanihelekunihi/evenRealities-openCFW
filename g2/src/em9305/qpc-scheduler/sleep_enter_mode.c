/* Native enter-mode 0x30f468..0x30f4b0 and lock aggregation
 * 0x302df4..0x302e14. ROM and actual lock-child ABI remain contracts. */
#include <stdint.h>
/* Native 0x302d20..0x302d40: seventeen optional callback table entries. */
uint32_t opencfw_em9305_sleep_lock_update(uint32_t selector)
{
 uint32_t result=selector;
 for(uint32_t index=0;index<17;index++) {
  uintptr_t object=*(volatile uint32_t *)(uintptr_t)(0x80faecu+4u*index);
  result=(uint32_t)object;
  if(object!=0) {
   uintptr_t callback=*(volatile uint32_t *)(object+selector*4u);
   result=(uint32_t)callback;
   if(callback!=0) result=((uint32_t (*)(uintptr_t))callback)(callback);
  }
 }
 return result;
}
extern uint32_t opencfw_em9305_sleep_rom_prepare(uint32_t); /* 0x103ab4 */
extern uint32_t opencfw_em9305_sleep_rom_enter(uint32_t); /* 0x103724 */
uint32_t opencfw_em9305_sleep_aggregate_locks(void)
{
 (void)opencfw_em9305_sleep_lock_update(1);
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x8018ecu;
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x8018f0u;
 uint32_t locks=high|low;
 *(volatile uint32_t *)(uintptr_t)0x801104u=locks;
 return locks;
}
static void set_state(uint32_t bit)
{
 uint32_t irq; __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0xf00405u;
 *state=(uint8_t)(*state|bit);
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
}
uint32_t opencfw_em9305_sleep_enter_mode(uint32_t mode)
{
 set_state(1);set_state(2);
 (void)opencfw_em9305_sleep_aggregate_locks();
 if(mode-5u<2u) {
  (void)opencfw_em9305_sleep_rom_prepare(0);
  (void)opencfw_em9305_sleep_rom_enter(mode);
 }
 return 0;
}
