/* Idle entry 0x4189ac calls stock cleanup at 0x418a98 with no arguments.
 * The stock cleanup body and selected opencfw_boot_idle_cleanup are compared
 * in idle-native-integrated/idle-comparison.json (24 cases, 60/60 bytes).
 * All incoming registers pass unchanged to the selected body. */
__attribute__((naked)) void cleanup(void)
{
    __asm__ volatile("b.w opencfw_boot_idle_cleanup");
}
