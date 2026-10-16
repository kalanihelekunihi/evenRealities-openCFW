/* Native sleep outer paths0x3126e0..0x31272c,0x312756..0x312774,
 * 0x312808..0x312824. Controller-state branch is compiled separately with explicit lower
 * contracts; not a claim that full controller firmware is implemented.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_mode_query(uint32_t r0,uint32_t r1); /* ROM0x101e34 */
extern uint32_t opencfw_em9305_sleep_rom_action(uint32_t r0); /* ROM0x101d50 */
extern uint32_t opencfw_em9305_sleep_controller_query(uint32_t r0); /* 0x30f60c */
extern uint32_t opencfw_em9305_sleep_state_query(uint32_t r0); /* 0x302de4 */
extern uint32_t opencfw_em9305_sleep_ready_query(uint32_t r0); /* 0x30f568 */
extern uint32_t opencfw_em9305_sleep_mode_branch(uint32_t mode);
/* Child composes actual metadata query0x3125a4 and state-dependent branch;
 * requires preserving stack-output/callback/MMIO/IRQ behavior. No stub body.
 */
extern uint32_t opencfw_em9305_sleep_controller_branch(void);
static uint32_t save_irq(void) { uint32_t state; __asm__ volatile("clri %0\n\tsync" : "=r"(state) :: "memory"); return state; }
uint32_t opencfw_em9305_sleep_lower(uint32_t incoming_irq,uint32_t incoming_link)
{
    __asm__ volatile("mov ilink,0" ::: "r29","memory");
    __asm__ volatile("seti %0" :: "r"(incoming_irq) : "memory");
    const uint32_t mode = opencfw_em9305_sleep_mode_query(incoming_irq,incoming_link);
    uint32_t result, shallow = 0;
    if (mode != 0 && mode != 1) return opencfw_em9305_sleep_mode_branch(mode);
    if (mode == 1) {
        result = opencfw_em9305_sleep_rom_action(mode);
    } else {
        result = opencfw_em9305_sleep_controller_query(mode);
        if (result != 0) {
            result = opencfw_em9305_sleep_state_query(result);
            shallow = 1;
            if (result != 0) return opencfw_em9305_sleep_controller_branch();
        }
    }
    result = opencfw_em9305_sleep_ready_query(result);
    if (result != 0) {
        const uint32_t irq = save_irq();
        uint32_t link;
        __asm__ volatile("mov %0,ilink" : "=r"(link) :: "memory");
        if (link == 0) {
            const uint32_t sleep_state = shallow != 0 ? irq & 31u : irq | 32u;
            __asm__ volatile("sleep %0" :: "r"(sleep_state) : "memory");
        } else {
            __asm__ volatile("seti %0" :: "r"(irq) : "memory");
        }
    }
    return save_irq();
}
