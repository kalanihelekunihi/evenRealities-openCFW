/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 bootloader mode-one services. */

typedef __UINT8_TYPE__ open_cfw_mode1_u8;
typedef __UINT32_TYPE__ open_cfw_mode1_u32;
typedef __UINTPTR_TYPE__ open_cfw_mode1_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_mode1_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_mode1_u32, open_cfw_mode1_u32);
extern open_cfw_mode1_u32 open_cfw_bootloader_bitmap_update_421632(open_cfw_mode1_u32, open_cfw_mode1_u32, open_cfw_mode1_u32);
extern open_cfw_mode1_u32 open_cfw_bootloader_bitmap_any_4215ae(open_cfw_mode1_u32);
extern open_cfw_mode1_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_mode1_u32 open_cfw_bootloader_mode1_control_41d92c(open_cfw_mode1_u32, open_cfw_mode1_u32);
extern void open_cfw_bootloader_poll_delay_4216b2(open_cfw_mode1_u32 *, open_cfw_mode1_u8 *);
#define OPEN_CFW_MODE1_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_mode1_u32 open_cfw_mode1_host_bitmap_test(open_cfw_mode1_u32, open_cfw_mode1_u32);
open_cfw_mode1_u32 open_cfw_mode1_host_bitmap_update(open_cfw_mode1_u32, open_cfw_mode1_u32, open_cfw_mode1_u32);
open_cfw_mode1_u32 open_cfw_mode1_host_bitmap_any(open_cfw_mode1_u32);
open_cfw_mode1_u32 open_cfw_mode1_host_critical_save(void);
void open_cfw_mode1_host_critical_restore(open_cfw_mode1_u32);
open_cfw_mode1_u32 open_cfw_mode1_host_control(open_cfw_mode1_u32, open_cfw_mode1_u32);
void open_cfw_mode1_host_poll_delay(open_cfw_mode1_u32 *, open_cfw_mode1_u8 *);
extern open_cfw_mode1_uintptr open_cfw_mode1_host_controller;
extern open_cfw_mode1_u32 open_cfw_mode1_host_enable_word;
extern open_cfw_mode1_u32 open_cfw_mode1_host_disable_word;
extern open_cfw_mode1_u8 open_cfw_mode1_host_active;
extern open_cfw_mode1_u32 open_cfw_mode1_host_state;
#define OPEN_CFW_MODE1_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_MODE1_ATTR
open_cfw_mode1_u32 open_cfw_bootloader_mode1_enable_421b08(open_cfw_mode1_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "movs r4, r0\n"
        "ldr.w r0, [pc, #0x92c]\n"
        "ldr r5, [r0]\n"
        "movs r0, #0xa\n"
        "bfi r5, r0, #0, #4\n"
        "ldr.w r0, [pc, #0x700]\n"
        "ldr r0, [r0, #0x10]\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #7\n"
        "b 3f\n"
        "1:\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #3\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, #0\n"
        "b 3f\n"
        "2:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r1, r5\n"
        "movs r0, #0xf\n"
        "bl open_cfw_bootloader_mode1_control_41d92c\n"
        "movs r2, #1\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #3\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, #0\n"
        "3:\n"
        "pop {r1, r4, r5, pc}\n");
#else
    open_cfw_mode1_u32 mask;
    open_cfw_mode1_u32 word = (open_cfw_mode1_host_enable_word & ~15U) | 10U;
    if (open_cfw_mode1_host_controller == 0U) return 7U;
    if (open_cfw_mode1_host_bitmap_test(3U, (open_cfw_mode1_u8)bit) != 0U) return 0U;
    mask = open_cfw_mode1_host_critical_save();
    (void)open_cfw_mode1_host_control(15U, word);
    (void)open_cfw_mode1_host_bitmap_update(3U, (open_cfw_mode1_u8)bit, 1U);
    open_cfw_mode1_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_MODE1_ATTR
open_cfw_mode1_u32 open_cfw_bootloader_mode1_disable_421b5c(open_cfw_mode1_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r4, r0\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #3\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #0\n"
        "b 3f\n"
        "1:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r2, #0\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #3\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "movs r0, #3\n"
        "bl open_cfw_bootloader_bitmap_any_4215ae\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "ldr.w r0, [pc, #0x8b0]\n"
        "ldr r1, [r0]\n"
        "movs r0, #0xf\n"
        "bl open_cfw_bootloader_mode1_control_41d92c\n"
        "2:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, #0\n"
        "3:\n"
        "pop {r1, r2, r4, pc}\n");
#else
    open_cfw_mode1_u32 mask;
    if (open_cfw_mode1_host_bitmap_test(3U, (open_cfw_mode1_u8)bit) == 0U) return 0U;
    mask = open_cfw_mode1_host_critical_save();
    (void)open_cfw_mode1_host_bitmap_update(3U, (open_cfw_mode1_u8)bit, 0U);
    if (open_cfw_mode1_host_bitmap_any(3U) == 0U) {
        (void)open_cfw_mode1_host_control(15U, open_cfw_mode1_host_disable_word);
    }
    open_cfw_mode1_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_MODE1_ATTR
void open_cfw_bootloader_mode1_poll_cleanup_421ba4(open_cfw_mode1_u32 *remaining)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r1, r0\n"
        "ldr.w r4, [pc, #0x898]\n"
        "ldrb r0, [r4]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_poll_delay_4216b2\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r0, #0\n"
        "strb r0, [r4]\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x880]\n"
        "str r0, [r1]\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "1:\n"
        "pop {r0, r1, r4, pc}\n");
#else
    open_cfw_mode1_u32 mask;
    if (open_cfw_mode1_host_active == 0U) return;
    open_cfw_mode1_host_poll_delay(remaining, &open_cfw_mode1_host_active);
    mask = open_cfw_mode1_host_critical_save();
    open_cfw_mode1_host_active = 0U;
    open_cfw_mode1_host_state = 0U;
    open_cfw_mode1_host_critical_restore(mask);
#endif
}
