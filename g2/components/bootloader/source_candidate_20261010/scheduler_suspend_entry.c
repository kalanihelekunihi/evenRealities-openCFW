/* Idle loop calls stock 0x4181d8 with no arguments. Its selected source
 * body is opencfw_bl_scheduler_suspend in scheduler_resume.c. */
__attribute__((naked)) void suspend_scheduler(void)
{
    __asm__ volatile("b.w opencfw_bl_scheduler_suspend");
}
