/* Shared C provider for native RX failure blocks 0x45068 and 0x921f0.
 * The ACLE compiler intrinsic emits the required CPU-register operation.
 * Fault-entry scratch registers and candidate instruction bytes differ from
 * stock; the provider is not instruction-qualified or device-validated. */
#include <stdint.h>
_Noreturn void r1_bae8_rx_allocation_fault(void)
{
    __builtin_arm_wsr("basepri",UINT32_C(64));
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
    for (;;) {}
}
