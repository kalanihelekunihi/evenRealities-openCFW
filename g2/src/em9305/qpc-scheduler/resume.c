/* Native QF_onResume0x3110f4..0x31114c and QF_resume0x311218..0x311230.
 * Product callback slots and controller root retain authenticated identities.
 */
#include <stdint.h>
#include "em9305_ram.h"
extern void QK_onIdle(void);
void opencfw_em9305_resume_hook(void)
{
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)UINT32_C(0xf00a74);
    registers[0] = 3;
    uintptr_t callback = em9305_ram_80fde0.u32_80fe08;
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    callback = em9305_ram_80fde0.u32_80fe04;
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    const uintptr_t controller = em9305_ram_801090.u32_801090;
    if (controller != 0) {
        const uintptr_t handler = *(volatile uint32_t *)(controller + 12u);
        if (handler != 0) ((void (*)(uint32_t))handler)(0);
    }
    uint32_t irq;
    irq=(uint32_t)__builtin_arc_clri(); __builtin_arc_sync();
    volatile uint8_t *const nesting = &em9305_ram_801398.u8_801398;
    if (*nesting != 0) { const uint8_t old = *nesting; *nesting = (uint8_t)(old - 1u); }
    registers[3] = 1;
    __builtin_arc_seti((int)irq);
}
_Noreturn void opencfw_em9305_framework_resume(void)
{
    (void)__builtin_arc_clri(); __builtin_arc_sync();
    opencfw_em9305_resume_hook();
    __builtin_arc_seti(0);
    for (;;) QK_onIdle();
}
