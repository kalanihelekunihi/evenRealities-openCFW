/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader row-five client services. */

typedef __UINT8_TYPE__ open_cfw_row5_u8;
typedef __UINT32_TYPE__ open_cfw_row5_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_row5_u32 open_cfw_bootloader_bitmap_any_4215ae(open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_row5_u32, open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_bitmap_count_4215fe(open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_bitmap_update_421632(open_cfw_row5_u32, open_cfw_row5_u32, open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_row5_u32 open_cfw_bootloader_mode0_enable_421bd2(open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_mode1_enable_421b08(open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_mode0_disable_421cce(open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_mode1_disable_421b5c(open_cfw_row5_u32);
extern void open_cfw_bootloader_row4_poll_cleanup_421e8c(open_cfw_row5_u32 *);
extern open_cfw_row5_u32 open_cfw_bootloader_dual_switch_426c8c(open_cfw_row5_u32);
extern open_cfw_row5_u32 open_cfw_bootloader_dual_commit_426ccc(open_cfw_row5_u8 *);
extern open_cfw_row5_u32 open_cfw_bootloader_dual_null_commit_426d1e(void);
#define OPEN_CFW_ROW5_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_row5_u32 open_cfw_row5_host_bitmap_any(open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_bitmap_test(open_cfw_row5_u32, open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_bitmap_count(open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_bitmap_update(open_cfw_row5_u32, open_cfw_row5_u32, open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_critical_save(void);
void open_cfw_row5_host_critical_restore(open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_mode_enable(open_cfw_row5_u8, open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_mode_disable(open_cfw_row5_u8, open_cfw_row5_u32);
void open_cfw_row5_host_cleanup(open_cfw_row5_u32 *);
open_cfw_row5_u32 open_cfw_row5_host_switch(open_cfw_row5_u32);
open_cfw_row5_u32 open_cfw_row5_host_commit(open_cfw_row5_u8 *);
open_cfw_row5_u32 open_cfw_row5_host_null_commit(void);
extern open_cfw_row5_u8 open_cfw_row5_host_active;
extern open_cfw_row5_u8 open_cfw_row5_host_ready;
extern open_cfw_row5_u8 open_cfw_row5_host_pending;
extern open_cfw_row5_u8 open_cfw_row5_host_selector;
extern open_cfw_row5_u8 open_cfw_row5_host_controller_present;
extern open_cfw_row5_u32 *open_cfw_row5_host_state_pointer;
#define OPEN_CFW_ROW5_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_ROW5_ATTR
open_cfw_row5_u32 open_cfw_bootloader_row5_enable_421eba(open_cfw_row5_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, r6, r7, lr}\n"
        "movs r5, r0\n"
        "movs r4, #0\n"
        "movs r0, #0x32\n"
        "str r0, [sp]\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "ldr.w r0, [pc, #0x574]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr.w r0, [pc, #0x570]\n"
        "ldr r0, [r0]\n"
        "ldr r0, [r0]\n"
        "str r0, [sp]\n"
        "1:\n"
        "mov r0, sp\n"
        "ldr.w r1, [pc, #0x564]\n"
        "str r0, [r1]\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_row4_poll_cleanup_421e8c\n"
        "movs r0, #0\n"
        "b 14f\n"
        "2:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0x540]\n"
        "strb r0, [r1]\n"
        "3:\n"
        "movs r2, #1\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "ldr.w r6, [pc, #0x3bc]\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "beq 6f\n"
        "ldr.w r0, [pc, #0x3a0]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 6f\n"
        "ldr.w r0, [pc, #0x3a4]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 4f\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_enable_421bd2\n"
        "movs r4, r0\n"
        "b 5f\n"
        "4:\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_enable_421b08\n"
        "movs r4, r0\n"
        "5:\n"
        "cmp r4, #0\n"
        "beq 6f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "movs r2, #0\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "6:\n"
        "cmp r4, #0\n"
        "bne 11f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "ldr.w r7, [pc, #0x4c8]\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "beq 7f\n"
        "ldr.w r0, [pc, #0x4c4]\n"
        "ldr r0, [r0]\n"
        "ldr r0, [r0]\n"
        "str r0, [sp]\n"
        "7:\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "bne 8f\n"
        "movs r4, #1\n"
        "8:\n"
        "cmp r4, #0\n"
        "bne 10f\n"
        "ldr.w r1, [pc, #0x4b0]\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 10f\n"
        "movs r0, #0\n"
        "strb r0, [r1]\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_dual_switch_426c8c\n"
        "ldr.w r0, [pc, #0x320]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 10f\n"
        "ldr.w r0, [pc, #0x324]\n"
        "bl open_cfw_bootloader_dual_commit_426ccc\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        "bne 9f\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "bne 10f\n"
        "movs r0, #1\n"
        "strb r0, [r7]\n"
        "b 10f\n"
        "9:\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_dual_switch_426c8c\n"
        "10:\n"
        "cmp r4, #0\n"
        "beq 10f\n"
        "movs r2, #0\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "10:\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "beq 10f\n"
        "mov r0, sp\n"
        "ldr.w r1, [pc, #0x458]\n"
        "str r0, [r1]\n"
        "10:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "11:\n"
        "cmp r4, #0\n"
        "beq 13f\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "beq 13f\n"
        "ldr.w r0, [pc, #0x2c8]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 13f\n"
        "ldr.w r0, [pc, #0x2cc]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 12f\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "movs r4, r0\n"
        "b 13f\n"
        "12:\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "movs r4, r0\n"
        "13:\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_row4_poll_cleanup_421e8c\n"
        "movs r0, r4\n"
        "14:\n"
        "pop {r1, r2, r3, r4, r5, r6, r7, pc}\n");
#else
    open_cfw_row5_u32 status = 0U;
    open_cfw_row5_u32 remaining = 50U;
    open_cfw_row5_u32 mask;
    if (open_cfw_row5_host_bitmap_test(5U, (open_cfw_row5_u8)bit) != 0U) {
        mask = open_cfw_row5_host_critical_save();
        if (open_cfw_row5_host_active != 0U && open_cfw_row5_host_state_pointer != (open_cfw_row5_u32 *)0) remaining = *open_cfw_row5_host_state_pointer;
        open_cfw_row5_host_state_pointer = &remaining;
        open_cfw_row5_host_critical_restore(mask);
        open_cfw_row5_host_cleanup(&remaining);
        return 0U;
    }
    mask = open_cfw_row5_host_critical_save();
    if (open_cfw_row5_host_bitmap_count(5U) == 0U) open_cfw_row5_host_pending = 1U;
    (void)open_cfw_row5_host_bitmap_update(5U, (open_cfw_row5_u8)bit, 1U);
    open_cfw_row5_host_critical_restore(mask);
    if (open_cfw_row5_host_ready != 0U && open_cfw_row5_host_controller_present != 0U) {
        status = open_cfw_row5_host_mode_enable(open_cfw_row5_host_selector, 0x36U);
        if (status != 0U) {
            mask = open_cfw_row5_host_critical_save();
            (void)open_cfw_row5_host_bitmap_update(5U, (open_cfw_row5_u8)bit, 0U);
            open_cfw_row5_host_critical_restore(mask);
        }
    }
    if (status == 0U) {
        mask = open_cfw_row5_host_critical_save();
        if (open_cfw_row5_host_active != 0U && open_cfw_row5_host_state_pointer != (open_cfw_row5_u32 *)0) remaining = *open_cfw_row5_host_state_pointer;
        if (open_cfw_row5_host_ready == 0U) status = 1U;
        if (status == 0U && open_cfw_row5_host_pending != 0U) {
            open_cfw_row5_host_pending = 0U;
            (void)open_cfw_row5_host_switch(1U);
            if (open_cfw_row5_host_controller_present != 0U) {
                status = open_cfw_row5_host_commit(&open_cfw_row5_host_selector);
                if (status == 0U) {
                    if (open_cfw_row5_host_active == 0U) open_cfw_row5_host_active = 1U;
                } else (void)open_cfw_row5_host_switch(0U);
            }
        }
        if (status != 0U) (void)open_cfw_row5_host_bitmap_update(5U, (open_cfw_row5_u8)bit, 0U);
        if (open_cfw_row5_host_active != 0U) open_cfw_row5_host_state_pointer = &remaining;
        open_cfw_row5_host_critical_restore(mask);
    }
    if (status != 0U && open_cfw_row5_host_ready != 0U && open_cfw_row5_host_controller_present != 0U)
        status = open_cfw_row5_host_mode_disable(open_cfw_row5_host_selector, 0x36U);
    open_cfw_row5_host_cleanup(&remaining);
    return status;
#endif
}

OPEN_CFW_ROW5_ATTR
open_cfw_row5_u32 open_cfw_bootloader_row5_disable_422040(open_cfw_row5_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r4, r0\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #0\n"
        "b 4f\n"
        "1:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r2, #0\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_any_4215ae\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "ldr r0, [pc, #0x268]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x3d8]\n"
        "strb r0, [r1]\n"
        "bl open_cfw_bootloader_dual_null_commit_426d1e\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x3b8]\n"
        "strb r0, [r1]\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x3b4]\n"
        "str r0, [r1]\n"
        "2:\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_dual_switch_426c8c\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, #0\n"
        "4:\n"
        "pop {r1, r2, r4, pc}\n");
#else
    open_cfw_row5_u32 mask;
    if (open_cfw_row5_host_bitmap_test(5U, (open_cfw_row5_u8)bit) == 0U) return 0U;
    mask = open_cfw_row5_host_critical_save();
    (void)open_cfw_row5_host_bitmap_update(5U, (open_cfw_row5_u8)bit, 0U);
    if (open_cfw_row5_host_bitmap_any(5U) == 0U) {
        if (open_cfw_row5_host_controller_present != 0U) {
            open_cfw_row5_host_pending = 0U;
            (void)open_cfw_row5_host_null_commit();
            (void)open_cfw_row5_host_mode_disable(0U, 0x36U);
            (void)open_cfw_row5_host_mode_disable(1U, 0x36U);
            open_cfw_row5_host_active = 0U;
            open_cfw_row5_host_state_pointer = (open_cfw_row5_u32 *)0;
        }
        (void)open_cfw_row5_host_switch(0U);
    }
    open_cfw_row5_host_critical_restore(mask);
    return 0U;
#endif
}
