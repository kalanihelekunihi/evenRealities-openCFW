/* Native QF_run0x311230..0x31125e. Its nonreturning idle loop is real
 * decoded behavior. Idle routine overwrites incoming R0 before use.
 */
#include <stdint.h>
extern uint32_t QK_sched_(void);
extern void QK_activate_(void);
extern void opencfw_em9305_startup_hook(void);
extern void QK_onIdle(void); /* 0x3115e4 */
/* Stock0x302518 is exactly NOP_S then return; not a fabricated body. */
void opencfw_em9305_startup_lower(void) { __builtin_arc_nop(); }
/* Stock 0x00311230 (QF_run) */
_Noreturn void QF_run(void)
{
    (void)__builtin_arc_clri(); __builtin_arc_sync();
    *(volatile uint8_t *)(uintptr_t)UINT32_C(0x801396) = 0;
    if (QK_sched_() != 0) QK_activate_();
    opencfw_em9305_startup_hook();
    __builtin_arc_seti(0);
    for (;;) QK_onIdle();
}
