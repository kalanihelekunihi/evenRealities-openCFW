/* SPDX-License-Identifier: BSD-3-Clause */
#include <stdint.h>

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_dummy_callback_424976(void)
{
    __asm__ volatile("bx lr\n");
}
#else
void open_cfw_bootloader_mspi_dummy_callback_424976(void *callback_context,
                                                    uint32_t status)
{
    (void)callback_context;
    (void)status;
}
#endif
