/* Native QF_run0x311230..0x31125e. Its nonreturning idle loop is real
 * decoded behavior. Idle routine overwrites incoming R0 before use.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_qk_sched(void);
extern void opencfw_em9305_qk_activate(void);
extern void opencfw_em9305_startup_hook(void);
extern void opencfw_em9305_idle(void); /* 0x3115e4 */
/* Stock0x302518 is exactly NOP_S then return; not a fabricated stub. */
void opencfw_em9305_startup_lower(void) { __asm__ volatile("nop_s"); }
/* Stock 0x00311230 (QF_run) */
_Noreturn void opencfw_em9305_framework_run(void)
{
    __asm__ volatile("clri 0\n\tsync" ::: "memory");
    *(volatile uint8_t *)(uintptr_t)UINT32_C(0x801396) = 0;
    if (opencfw_em9305_qk_sched() != 0) opencfw_em9305_qk_activate();
    opencfw_em9305_startup_hook();
    __asm__ volatile("seti 0" ::: "memory");
    for (;;) opencfw_em9305_idle();
}
