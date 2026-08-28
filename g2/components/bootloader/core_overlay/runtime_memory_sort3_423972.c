/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 three-element compare/exchange helper. */

typedef __SIZE_TYPE__ open_cfw_ms3_size;
typedef int (*open_cfw_ms3_compare)(const void *, const void *);

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_memory_swap_423864(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_memory_sort3_423972(void)
{
    __asm__ volatile(
        "push.w {r4, r5, r6, r7, r8, lr}\n"
        "mov r4, r0\n"
        "mov r5, r1\n"
        "ldr r7, [sp, #0x18]\n"
        "mov r6, r2\n"
        "mov r8, r3\n"
        "mov r1, r4\n"
        "mov r0, r5\n"
        "blx r7\n"
        "cmp r0, #0\n"
        "bpl 1f\n"
        "mov r2, r8\n"
        "mov r1, r5\n"
        "mov r0, r4\n"
        "bl open_cfw_bootloader_memory_swap_423864\n"
        "1:\n"
        "mov r1, r5\n"
        "mov r0, r6\n"
        "blx r7\n"
        "cmp r0, #0\n"
        "bpl 2f\n"
        "mov r2, r8\n"
        "mov r1, r6\n"
        "mov r0, r5\n"
        "bl open_cfw_bootloader_memory_swap_423864\n"
        "2:\n"
        "mov r1, r4\n"
        "mov r0, r5\n"
        "blx r7\n"
        "cmp r0, #0\n"
        "bpl 3f\n"
        "mov r2, r8\n"
        "mov r1, r5\n"
        "mov r0, r4\n"
        "pop.w {r4, r5, r6, r7, r8, lr}\n"
        /* Exact narrow tail relocation from 0x004239BC to 0x00423864. */
        "b.n .\n"
        ".reloc . - 2, R_ARM_THM_JUMP11, "
        "open_cfw_bootloader_memory_swap_423864\n"
        "3:\n"
        "pop.w {r4, r5, r6, r7, r8, pc}\n");
}
#else
extern void open_cfw_ms3_host_swap(void *, void *, open_cfw_ms3_size);

void open_cfw_bootloader_memory_sort3_423972(
    void *first, void *second, void *third, open_cfw_ms3_size width,
    open_cfw_ms3_compare compare)
{
    if (compare(second, first) < 0) open_cfw_ms3_host_swap(first, second, width);
    if (compare(third, second) < 0) open_cfw_ms3_host_swap(second, third, width);
    if (compare(second, first) < 0) open_cfw_ms3_host_swap(first, second, width);
}
#endif
