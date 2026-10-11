/* Stock 0x41b5f6 RTOS heap-failure hook. */
__attribute__((naked, noreturn)) void opencfw_bl_malloc_failed(void)
{
    __asm__ volatile("b.w opencfw_malloc_failed_native");
}
