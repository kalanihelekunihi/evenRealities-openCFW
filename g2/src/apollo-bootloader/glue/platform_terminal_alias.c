/* Stock 0x4329c4 platform terminal entry, retaining incoming R0. */
__attribute__((naked, noreturn)) void opencfw_boot_platform_terminal(void)
{
    __asm__ volatile("b.w opencfw_platform_terminal_native");
}
