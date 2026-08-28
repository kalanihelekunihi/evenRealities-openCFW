/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 Floyd max-heap sift helper. */

typedef __SIZE_TYPE__ open_cfw_mhs_size;
typedef int (*open_cfw_mhs_compare)(const void *, const void *);

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_memory_swap_423864(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_memory_heap_sift_4239c2(void)
{
    __asm__ volatile(
        "push.w {r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}\n"
        "lsls r7, r1, #1\n"
        "mul r4, r3, r1\n"
        "adds r7, r7, #2\n"
        "add.w r11, r0, r4\n"
        "mul r4, r3, r7\n"
        "ldr.w r8, [sp, #0x28]\n"
        "str r1, [sp]\n"
        "adds r6, r0, r4\n"
        "mov r5, r0\n"
        "mov r4, r1\n"
        "mov r9, r2\n"
        "mov r10, r3\n"
        "b 4f\n"
        "1:\n"
        "rsb.w r0, r10, #0\n"
        "adds r4, r6, r0\n"
        "cmp r7, r9\n"
        "beq 2f\n"
        "mov r1, r4\n"
        "mov r0, r6\n"
        "blx r8\n"
        "cmp r0, #0\n"
        "bpl 3f\n"
        "2:\n"
        "subs r7, r7, #1\n"
        "mov r6, r4\n"
        "3:\n"
        "mov r2, r10\n"
        "mov r1, r6\n"
        "mov r0, r11\n"
        "mov r4, r7\n"
        "bl open_cfw_bootloader_memory_swap_423864\n"
        "lsls r7, r7, #1\n"
        "adds r7, r7, #2\n"
        "mov r11, r6\n"
        "mul r0, r10, r7\n"
        "adds r6, r5, r0\n"
        "4:\n"
        "cmp r9, r7\n"
        "bhs 1b\n"
        "5:\n"
        "ldr r1, [sp]\n"
        "cmp r1, r4\n"
        "bhs 7f\n"
        "subs r4, r4, #1\n"
        "lsrs r4, r4, #1\n"
        "mul r0, r10, r4\n"
        "adds r7, r5, r0\n"
        "mov r1, r7\n"
        "mov r0, r11\n"
        "blx r8\n"
        "cmp r0, #0\n"
        "ble 7f\n"
        "mov r2, r10\n"
        "mov r1, r11\n"
        "mov r0, r7\n"
        "bl open_cfw_bootloader_memory_swap_423864\n"
        "mov r11, r7\n"
        "b 5b\n"
        "7:\n"
        "pop.w {r0, r4, r5, r6, r7, r8, r9, r10, r11, pc}\n");
}
#else
extern void open_cfw_mhs_host_swap(void *, void *, open_cfw_mhs_size);

void open_cfw_bootloader_memory_heap_sift_4239c2(
    void *base_pointer, open_cfw_mhs_size start, open_cfw_mhs_size count,
    open_cfw_mhs_size width, open_cfw_mhs_compare compare)
{
    unsigned char *base = (unsigned char *)base_pointer;
    open_cfw_mhs_size current = start;
    open_cfw_mhs_size child = start * 2U + 2U;
    unsigned char *hole = base + start * width;
    unsigned char *right = base + child * width;

    while (count >= child) {
        unsigned char *selected = right;
        unsigned char *left = right - width;

        if (child == count || compare(right, left) < 0) {
            --child;
            selected = left;
        }
        open_cfw_mhs_host_swap(hole, selected, width);
        current = child;
        hole = selected;
        child = child * 2U + 2U;
        right = base + child * width;
    }

    while (start < current) {
        open_cfw_mhs_size parent = (current - 1U) / 2U;
        unsigned char *parent_pointer = base + parent * width;

        if (compare(hole, parent_pointer) <= 0) break;
        open_cfw_mhs_host_swap(parent_pointer, hole, width);
        current = parent;
        hole = parent_pointer;
    }
}
#endif
