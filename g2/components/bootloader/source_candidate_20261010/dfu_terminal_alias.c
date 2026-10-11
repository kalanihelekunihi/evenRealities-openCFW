/* Stock 0x42e1da DFU manager terminal loop. */
__attribute__((naked, noreturn)) void opencfw_boot_dfu_terminal(void)
{
    __asm__ volatile("b.w opencfw_dfu_terminal_native");
}
