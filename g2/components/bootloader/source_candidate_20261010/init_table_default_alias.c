/* SPDX-License-Identifier: MIT
 * Startup's no-argument stock Thumb entry 0x41f9f9.
 */
__attribute__((naked)) void opencfw_provider_41f9f8(void)
{
    __asm__ volatile("b.w opencfw_boot_init_table_default");
}
