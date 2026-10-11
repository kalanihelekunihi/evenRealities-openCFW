/* Idle BL 0x4189ce targets stock 0x41b3d0, selected kernel reschedule. */
__attribute__((naked)) void reschedule(void)
{
    __asm__ volatile("b.w opencfw_bl_kernel_reschedule");
}
