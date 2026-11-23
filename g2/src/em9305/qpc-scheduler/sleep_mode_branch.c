/* Extracted complete mode!=0 && mode!=1 branch of native sleep body:
 * 0x312774..0x312808 then common IRQ-disabled return0x31281a.
 * Synthetic C helper, not a claimed stock function boundary or full sleep.
 */
#include <stdint.h>
#include "em9305_ram.h"
extern uint32_t opencfw_em9305_sleep_rom_action(uint32_t deep); /* 0x101d50 */
extern void opencfw_em9305_controller_sleep_mode(uint32_t mode); /* 0x30f374 */
static uint32_t save_irq(void) { uint32_t s; s=(uint32_t)__builtin_arc_clri(); __builtin_arc_sync(); return s; }
static void restore_irq(uint32_t s) { __builtin_arc_seti((int)s); }
static void notify(uint32_t event)
{
    const uintptr_t object = em9305_ram_801090.u32_801090;
    if (object != 0) {
        const uintptr_t callback = *(volatile uint32_t *)(object + 12u);
        if (callback != 0) ((void (*)(uint32_t))callback)(event);
    }
}
uint32_t opencfw_em9305_sleep_mode_branch(uint32_t mode)
{
    notify(1);
    volatile uint8_t *const control = (volatile uint8_t *)(uintptr_t)UINT32_C(0xf00407);
    volatile uint8_t *const state = (volatile uint8_t *)(uintptr_t)UINT32_C(0xf00405);
    uint32_t irq = save_irq();
    const uint8_t old_control = *control;
    *control = (uint8_t)(old_control | 4u);
    restore_irq(irq);
    irq = save_irq();
    const uint8_t old_state = *state;
    *state = (uint8_t)(old_state | 1u);
    restore_irq(irq);
    uint32_t link;
    /* ILINK (r29) is a core register with no C or builtin access; asm stays. */
    __asm__ volatile("mov %0,ilink" : "=r"(link) :: "memory");
    if (link == 0) {
        const uint32_t deep = mode == 3;
        (void)opencfw_em9305_sleep_rom_action(deep);
        opencfw_em9305_controller_sleep_mode(deep + 5u);
    }
    irq = save_irq();
    const uint8_t state_after_sleep = *state;
    *state = (uint8_t)(state_after_sleep & ~1u);
    restore_irq(irq);
    irq = save_irq();
    const uint8_t state_after_clear = *state;
    *state = (uint8_t)(state_after_clear & ~2u);
    restore_irq(irq);
    notify(0);
    return save_irq();
}
