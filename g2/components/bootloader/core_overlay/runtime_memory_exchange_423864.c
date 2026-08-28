/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bounded memory-exchange helpers. */

typedef __UINT8_TYPE__ open_cfw_mx_u8;
typedef __SIZE_TYPE__ open_cfw_mx_size;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_memcpy_41568c(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_memory_swap_423864(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "mov r4, r2\n"
        "cmp r4, #0x40\n"
        "sub sp, #0x80\n"
        "mov r5, r0\n"
        "mov r6, r1\n"
        "bhs 3f\n"
        "cbz r4, 4f\n"
        "1:\n"
        "ldrb r0, [r5]\n"
        "ldrb r1, [r6]\n"
        "strb r1, [r5], #1\n"
        "subs r4, r4, #1\n"
        "strb r0, [r6], #1\n"
        "bne 1b\n"
        "4:\n"
        "add sp, #0x84\n"
        "pop {r4, r5, r6, r7, pc}\n"
        "3:\n"
        "movs r7, #0x80\n"
        "cmp r4, #0x80\n"
        "it ls\n"
        "movls r7, r4\n"
        "mov r2, r7\n"
        "mov r1, r5\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "mov r2, r7\n"
        "mov r1, r6\n"
        "mov r0, r5\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "mov r2, r7\n"
        "mov r1, sp\n"
        "mov r0, r6\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "subs r4, r4, r7\n"
        "add r5, r7\n"
        "add r6, r7\n"
        "bne 3b\n"
        "add sp, #0x84\n"
        "pop {r4, r5, r6, r7, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_memory_rotate3_4238ba(void)
{
    __asm__ volatile(
        "push.w {r4, r5, r6, r7, r8, lr}\n"
        "mov r4, r3\n"
        "cmp r4, #0x40\n"
        "sub sp, #0x80\n"
        "mov r5, r0\n"
        "mov r6, r1\n"
        "mov r8, r2\n"
        "bhs 3f\n"
        "cbz r4, 4f\n"
        "1:\n"
        "ldrb r0, [r5]\n"
        "ldrb.w r1, [r8]\n"
        "strb r1, [r5], #1\n"
        "subs r4, r4, #1\n"
        "ldrb r2, [r6]\n"
        "strb r2, [r8], #1\n"
        "strb r0, [r6], #1\n"
        "bne 1b\n"
        "4:\n"
        "b 5f\n"
        "3:\n"
        "movs r7, #0x80\n"
        "cmp r4, #0x80\n"
        "it ls\n"
        "movls r7, r4\n"
        "mov r2, r7\n"
        "mov r1, r5\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "mov r2, r7\n"
        "mov r1, r8\n"
        "mov r0, r5\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "mov r2, r7\n"
        "mov r1, r6\n"
        "mov r0, r8\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "mov r2, r7\n"
        "mov r1, sp\n"
        "mov r0, r6\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "subs r4, r4, r7\n"
        "add r5, r7\n"
        "add r6, r7\n"
        "add r8, r7\n"
        "bne 3b\n"
        "5:\n"
        "add sp, #0x80\n"
        "pop.w {r4, r5, r6, r7, r8, pc}\n");
}
#else
void open_cfw_bootloader_memory_swap_423864(
    void *left_pointer, void *right_pointer, open_cfw_mx_size size)
{
    open_cfw_mx_u8 *left = (open_cfw_mx_u8 *)left_pointer;
    open_cfw_mx_u8 *right = (open_cfw_mx_u8 *)right_pointer;
    while (size != 0U) {
        open_cfw_mx_u8 value = *left;
        *left++ = *right;
        *right++ = value;
        --size;
    }
}

void open_cfw_bootloader_memory_rotate3_4238ba(
    void *first_pointer, void *second_pointer, void *third_pointer,
    open_cfw_mx_size size)
{
    open_cfw_mx_u8 *first = (open_cfw_mx_u8 *)first_pointer;
    open_cfw_mx_u8 *second = (open_cfw_mx_u8 *)second_pointer;
    open_cfw_mx_u8 *third = (open_cfw_mx_u8 *)third_pointer;
    while (size != 0U) {
        open_cfw_mx_u8 value = *first;
        *first++ = *third;
        *third++ = *second;
        *second++ = value;
        --size;
    }
}
#endif
