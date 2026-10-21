#include "native_stacmd.h"
#include <stdint.h>
/* Native0x5c0fa: 209 iterations of four explicit NOPs. Compiler scheduling
 * and physical timing remain separate from the emitted-NOP-count contract. */
uint32_t r1_stacmd_recovery_delay_native(void)
{
    for (uint32_t i=0;i<209;i++) {
        __asm__ volatile("nop\nnop\nnop\nnop");
    }
    return 0;
}
