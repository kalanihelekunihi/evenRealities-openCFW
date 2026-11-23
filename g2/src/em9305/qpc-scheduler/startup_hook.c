/* Native QF_onStartup0x311154..0x31119e. First child0x302518 decodes
 * to NOP/return and consumes no input; product callback ABI remains open.
 */
#include <stdint.h>
#include "em9305_ram.h"
extern void opencfw_em9305_startup_lower(void); /* 0x302518 */
void opencfw_em9305_startup_hook(void)
{
    opencfw_em9305_startup_lower();
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)UINT32_C(0xf00a74);
    registers[0] = 3;
    uintptr_t callback = em9305_ram_80fde0.u32_80fe10;
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    callback = em9305_ram_80fde0.u32_80fe0c;
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    uint32_t irq;
    irq=(uint32_t)__builtin_arc_clri(); __builtin_arc_sync();
    volatile uint8_t *const nesting = &em9305_ram_801398.u8_801398;
    if (*nesting != 0) { const uint8_t old = *nesting; *nesting = (uint8_t)(old - 1u); }
    registers[3] = 1;
    __builtin_arc_seti((int)irq);
}
