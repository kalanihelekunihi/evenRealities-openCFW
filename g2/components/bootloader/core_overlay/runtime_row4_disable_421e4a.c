/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader row-four disable services. */

typedef __UINT8_TYPE__ open_cfw_row4_disable_u8;
typedef __UINT32_TYPE__ open_cfw_row4_disable_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_row4_disable_u32 open_cfw_bootloader_bitmap_any_4215ae(open_cfw_row4_disable_u32);
extern open_cfw_row4_disable_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_row4_disable_u32, open_cfw_row4_disable_u32);
extern open_cfw_row4_disable_u32 open_cfw_bootloader_bitmap_update_421632(open_cfw_row4_disable_u32, open_cfw_row4_disable_u32, open_cfw_row4_disable_u32);
extern void open_cfw_bootloader_poll_delay_4216b2(open_cfw_row4_disable_u32 *);
extern open_cfw_row4_disable_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_row4_disable_u32 open_cfw_bootloader_row4_switch_426c58(open_cfw_row4_disable_u32);
#define OPEN_CFW_ROW4_DISABLE_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_row4_disable_u32 open_cfw_row4_disable_host_bitmap_any(open_cfw_row4_disable_u32);
open_cfw_row4_disable_u32 open_cfw_row4_disable_host_bitmap_test(open_cfw_row4_disable_u32, open_cfw_row4_disable_u32);
open_cfw_row4_disable_u32 open_cfw_row4_disable_host_bitmap_update(open_cfw_row4_disable_u32, open_cfw_row4_disable_u32, open_cfw_row4_disable_u32);
void open_cfw_row4_disable_host_poll(open_cfw_row4_disable_u32 *);
open_cfw_row4_disable_u32 open_cfw_row4_disable_host_critical_save(void);
void open_cfw_row4_disable_host_critical_restore(open_cfw_row4_disable_u32);
open_cfw_row4_disable_u32 open_cfw_row4_disable_host_switch(open_cfw_row4_disable_u32);
extern open_cfw_row4_disable_u8 open_cfw_row4_disable_host_active;
extern open_cfw_row4_disable_u32 *open_cfw_row4_disable_host_state_pointer;
#define OPEN_CFW_ROW4_DISABLE_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_ROW4_DISABLE_ATTR
open_cfw_row4_disable_u32 open_cfw_bootloader_row4_disable_421e4a(open_cfw_row4_disable_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r4, r0\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #4\n"
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
        "movs r0, #4\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_bitmap_any_4215ae\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_row4_switch_426c58\n"
        "2:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, #0\n"
        "3:\n"
        "pop {r1, r2, r4, pc}\n");
#else
    open_cfw_row4_disable_u32 mask;
    if (open_cfw_row4_disable_host_bitmap_test(4U, (open_cfw_row4_disable_u8)bit) == 0U) return 0U;
    mask = open_cfw_row4_disable_host_critical_save();
    (void)open_cfw_row4_disable_host_bitmap_update(4U, (open_cfw_row4_disable_u8)bit, 0U);
    if (open_cfw_row4_disable_host_bitmap_any(4U) == 0U) (void)open_cfw_row4_disable_host_switch(0U);
    open_cfw_row4_disable_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_ROW4_DISABLE_ATTR
void open_cfw_bootloader_row4_poll_cleanup_421e8c(open_cfw_row4_disable_u32 *remaining)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r1, r0\n"
        "ldr.w r4, [pc, #0x5bc]\n"
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
        "ldr.w r1, [pc, #0x5a4]\n"
        "str r0, [r1]\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "1:\n"
        "pop {r0, r1, r4, pc}\n");
#else
    open_cfw_row4_disable_u32 mask;
    (void)remaining;
    if (open_cfw_row4_disable_host_active == 0U) return;
    open_cfw_row4_disable_host_poll((open_cfw_row4_disable_u32 *)&open_cfw_row4_disable_host_active);
    mask = open_cfw_row4_disable_host_critical_save();
    open_cfw_row4_disable_host_active = 0U;
    open_cfw_row4_disable_host_state_pointer = (open_cfw_row4_disable_u32 *)0;
    open_cfw_row4_disable_host_critical_restore(mask);
#endif
}
