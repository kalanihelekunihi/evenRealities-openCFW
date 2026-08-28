/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bounded rotate-to-front helper. */

typedef __UINT8_TYPE__ open_cfw_mrf_u8;
typedef __SIZE_TYPE__ open_cfw_mrf_size;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_memcpy_41568c(void);
extern void open_cfw_bootloader_memmove_4276bc(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_memory_rotate_front_423928(void)
{
    __asm__ volatile(
        "push.w {r3, r4, r5, r6, r7, r8, r9, lr}\n"
        "mov r5, r0\n"
        "mov r9, r1\n"
        "mov r7, r2\n"
        "sub.w r8, r9, r5\n"
        "sub sp, #0x80\n"
        "add r8, r7\n"
        "movs r4, r7\n"
        "b 2f\n"
        "1:\n"
        "movs r6, #0x80\n"
        "cmp r4, #0x80\n"
        "it ls\n"
        "movls r6, r4\n"
        "subs r1, r7, r6\n"
        "mov r2, r6\n"
        "add r1, r9\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "sub.w r2, r8, r6\n"
        "mov r1, r5\n"
        "adds r0, r5, r6\n"
        "bl open_cfw_bootloader_memmove_4276bc\n"
        "mov r2, r6\n"
        "mov r1, sp\n"
        "mov r0, r5\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "subs r4, r4, r6\n"
        "2:\n"
        "bne 1b\n"
        "add sp, #0x84\n"
        "pop.w {r4, r5, r6, r7, r8, r9, pc}\n");
}
#else
extern void *open_cfw_mrf_host_memcpy(void *, const void *, open_cfw_mrf_size);
extern void *open_cfw_mrf_host_memmove(void *, const void *, open_cfw_mrf_size);

void open_cfw_bootloader_memory_rotate_front_423928(
    void *first_pointer, const void *last_pointer, open_cfw_mrf_size width)
{
    open_cfw_mrf_u8 scratch[128];
    open_cfw_mrf_u8 *first = (open_cfw_mrf_u8 *)first_pointer;
    const open_cfw_mrf_u8 *last = (const open_cfw_mrf_u8 *)last_pointer;
    open_cfw_mrf_size total = (open_cfw_mrf_size)(last - first) + width;
    open_cfw_mrf_size remaining = width;
    while (remaining != 0U) {
        open_cfw_mrf_size chunk = remaining <= 128U ? remaining : 128U;
        open_cfw_mrf_host_memcpy(scratch, last + width - chunk, chunk);
        open_cfw_mrf_host_memmove(first + chunk, first, total - chunk);
        open_cfw_mrf_host_memcpy(first, scratch, chunk);
        remaining -= chunk;
    }
}
#endif
