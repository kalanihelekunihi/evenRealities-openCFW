/* Stock 0x41b390 RTOS task-return entry. */
__attribute__((naked)) void opencfw_bl_task_return(void)
{
    __asm__ volatile("b.w opencfw_task_return_native");
}
