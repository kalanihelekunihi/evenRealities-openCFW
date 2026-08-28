/* SPDX-License-Identifier: BSD-3-Clause */
/* Source-equivalent adapter for AmbiqSuite 5.1.0 mspi_dummy_callback. */

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_dummy_callback_424976(void)
{
    __asm__ volatile("bx lr\n");
}
