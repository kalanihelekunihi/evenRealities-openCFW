/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009190 Thumb compact jump-table dispatcher.
 * The caller places a maximum index byte immediately before LR and relative
 * halfword target bytes at LR. R3 is the selector; other argument registers
 * pass through to the selected case. This is architecture-level source.
 */
__attribute__((naked)) void case_boot_jump_table_dispatch_9190(void)
{
    __asm__ volatile(
        "push {r4, r5}\n"
        "mov r4, lr\n"
        "subs r4, #1\n"
        "ldrb r5, [r4, #0]\n"
        "adds r4, #1\n"
        "cmp r3, r5\n"
        "bhs 1f\n"
        "mov r5, r3\n"
        "1: ldrb r3, [r4, r5]\n"
        "lsls r3, r3, #1\n"
        "adds r3, r4, r3\n"
        "pop {r4, r5}\n"
        "bx r3\n");
}
