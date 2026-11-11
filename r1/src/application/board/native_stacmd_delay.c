#include "native_stacmd.h"
#include <stdint.h>
/* Native 0x5c0fa: the four NOPs and exact increment form are timing
 * primitives. The C loop retains the unsigned bound; the tied operand
 * prevents countdown conversion and preserves the native instruction body. */
uint32_t r1_stacmd_recovery_delay_native(void)
{
    /* Five compiler intrinsics preserve the 209-iteration instruction count
     * after Clang rotates this loop into a decrement-and-branch form. */
    for (uint32_t i=0;i<209u;i++) {
        __builtin_arm_nop();
        __builtin_arm_nop();
        __builtin_arm_nop();
        __builtin_arm_nop();
        __builtin_arm_nop();
    }
    return 0;
}
