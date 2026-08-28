/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader IAR thread-pointer leaf. */

typedef __UINTPTR_TYPE__ open_cfw_thread_uintptr;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_thread_pointer_422874(void)
{
    __asm__ volatile(
        "ldr r0, [pc, #0]\n"
        "bx lr\n"
        ".word 0x20000518\n");
}
#else
open_cfw_thread_uintptr open_cfw_bootloader_thread_pointer_422874(void)
{
    return (open_cfw_thread_uintptr)0x20000518U;
}
#endif
