/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader row-six client services. */

typedef __UINT8_TYPE__ open_cfw_row6_u8;
typedef __UINT32_TYPE__ open_cfw_row6_u32;
typedef __UINTPTR_TYPE__ open_cfw_row6_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_row6_u32 open_cfw_bootloader_bitmap_any_4215ae(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_row6_u32, open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_bitmap_count_4215fe(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_bitmap_update_421632(open_cfw_row6_u32, open_cfw_row6_u32, open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_row6_u32 open_cfw_bootloader_mode0_enable_421bd2(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_mode1_enable_421b08(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_mode0_disable_421cce(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_mode1_disable_421b5c(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_row6_create_4272ac(open_cfw_row6_u32, open_cfw_row6_u32 *);
extern open_cfw_row6_u32 open_cfw_bootloader_row6_destroy_427310(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_row6_start_427360(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_row6_stop_4273dc(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_row6_configure_42740c(open_cfw_row6_u32, open_cfw_row6_u8 *);
extern open_cfw_row6_u32 open_cfw_bootloader_row6_finalize_427522(open_cfw_row6_u32);
extern open_cfw_row6_u32 open_cfw_bootloader_mode_service_4216d4(open_cfw_row6_uintptr, const open_cfw_row6_u32 *);
extern open_cfw_row6_u32 open_cfw_bootloader_dual_mode_service_4217d2(open_cfw_row6_uintptr, const open_cfw_row6_u32 *);
extern open_cfw_row6_u32 open_cfw_bootloader_bitmap_client_service_421978(open_cfw_row6_uintptr, const open_cfw_row6_u32 *);
#define OPEN_CFW_ROW6_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_row6_u32 open_cfw_row6_host_bitmap_any(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_bitmap_test(open_cfw_row6_u32, open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_bitmap_count(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_bitmap_update(open_cfw_row6_u32, open_cfw_row6_u32, open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_critical_save(void);
void open_cfw_row6_host_critical_restore(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_mode_enable(open_cfw_row6_u8, open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_mode_disable(open_cfw_row6_u8, open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_create(open_cfw_row6_u32, open_cfw_row6_u32 *);
open_cfw_row6_u32 open_cfw_row6_host_destroy(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_start(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_stop(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_configure(open_cfw_row6_u32, open_cfw_row6_u8 *);
open_cfw_row6_u32 open_cfw_row6_host_finalize(open_cfw_row6_u32);
open_cfw_row6_u32 open_cfw_row6_host_dispatch(open_cfw_row6_u8, open_cfw_row6_uintptr, const open_cfw_row6_u32 *);
extern open_cfw_row6_u8 open_cfw_row6_host_ready;
extern open_cfw_row6_u8 open_cfw_row6_host_selector;
extern open_cfw_row6_u8 open_cfw_row6_host_pending;
extern open_cfw_row6_u32 open_cfw_row6_host_handle;
#define OPEN_CFW_ROW6_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_ROW6_ATTR
open_cfw_row6_u32 open_cfw_bootloader_row6_enable_4220b2(open_cfw_row6_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push.w {r2, r3, r4, r5, r6, r7, r8, lr}\n"
        "movs r5, r0\n"
        "movs r6, #0\n"
        "movs r4, #0\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r0, #0\n"
        "b 12f\n"
        "1:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0x378]\n"
        "strb r0, [r1]\n"
        "2:\n"
        "movs r2, #1\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "ldr.w r7, [pc, #0x33c]\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "beq 4f\n"
        "ldr.w r0, [pc, #0x32c]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode0_enable_421bd2\n"
        "movs r4, r0\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode1_enable_421b08\n"
        "b 4f\n"
        "3:\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode1_enable_421b08\n"
        "movs r4, r0\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode0_enable_421bd2\n"
        "4:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "cmp r4, #0\n"
        "bne 9f\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "bne 5f\n"
        "movs r4, #1\n"
        "5:\n"
        "cmp r4, #0\n"
        "bne 10f\n"
        "ldr.w r1, [pc, #0x318]\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 10f\n"
        "movs r0, #0\n"
        "strb r0, [r1]\n"
        "ldr.w r8, [pc, #0x310]\n"
        "ldr.w r0, [r8]\n"
        "cmp r0, #0\n"
        "bne 6f\n"
        "mov r1, r8\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_row6_create_4272ac\n"
        "movs r4, r0\n"
        "6:\n"
        "cmp r4, #0\n"
        "bne 7f\n"
        "ldr.w r1, [pc, #0x2c4]\n"
        "ldr.w r0, [r8]\n"
        "bl open_cfw_bootloader_row6_configure_42740c\n"
        "movs r4, r0\n"
        "7:\n"
        "cmp r4, #0\n"
        "bne 8f\n"
        "ldr.w r0, [r8]\n"
        "bl open_cfw_bootloader_row6_start_427360\n"
        "movs r4, r0\n"
        "8:\n"
        "cmp r4, #0\n"
        "bne 8f\n"
        "movs r6, #1\n"
        "b 10f\n"
        "8:\n"
        "ldr.w r0, [r8]\n"
        "cmp r0, #0\n"
        "beq 10f\n"
        "ldr.w r0, [r8]\n"
        "bl open_cfw_bootloader_row6_destroy_427310\n"
        "movs r0, #0\n"
        "str.w r0, [r8]\n"
        "10:\n"
        "cmp r4, #0\n"
        "beq 11f\n"
        "movs r2, #0\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "b 11f\n"
        "9:\n"
        "movs r2, #0\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "11:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "beq 11f\n"
        "cmp r4, #0\n"
        "bne 10f\n"
        "ldr.w r0, [pc, #0x25c]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 9f\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "b 11f\n"
        "9:\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "b 11f\n"
        "10:\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "11:\n"
        "uxtb r6, r6\n"
        "cmp r6, #0\n"
        "beq 11f\n"
        "ldr.w r0, [pc, #0x260]\n"
        "ldr r0, [r0]\n"
        "bl open_cfw_bootloader_row6_finalize_427522\n"
        "movs r4, r0\n"
        "11:\n"
        "movs r0, r4\n"
        "12:\n"
        "pop.w {r1, r2, r4, r5, r6, r7, r8, pc}\n");
#else
    open_cfw_row6_u32 status = 0U, success = 0U, mask;
    if (open_cfw_row6_host_bitmap_test(6U, (open_cfw_row6_u8)bit) != 0U) return 0U;
    mask = open_cfw_row6_host_critical_save();
    if (open_cfw_row6_host_bitmap_count(6U) == 0U) open_cfw_row6_host_pending = 1U;
    (void)open_cfw_row6_host_bitmap_update(6U, (open_cfw_row6_u8)bit, 1U);
    open_cfw_row6_host_critical_restore(mask);
    if (open_cfw_row6_host_ready != 0U) {
        status = open_cfw_row6_host_mode_enable(open_cfw_row6_host_selector, 0x35U);
        (void)open_cfw_row6_host_mode_enable((open_cfw_row6_u8)(open_cfw_row6_host_selector ^ 1U), 0x35U);
    }
    mask = open_cfw_row6_host_critical_save();
    if (status == 0U) {
        if (open_cfw_row6_host_ready == 0U) status = 1U;
        if (status == 0U && open_cfw_row6_host_pending != 0U) {
            open_cfw_row6_host_pending = 0U;
            if (open_cfw_row6_host_handle == 0U) status = open_cfw_row6_host_create(0U, &open_cfw_row6_host_handle);
            if (status == 0U) status = open_cfw_row6_host_configure(open_cfw_row6_host_handle, &open_cfw_row6_host_selector);
            if (status == 0U) status = open_cfw_row6_host_start(open_cfw_row6_host_handle);
            if (status == 0U) success = 1U;
            else if (open_cfw_row6_host_handle != 0U) { (void)open_cfw_row6_host_destroy(open_cfw_row6_host_handle); open_cfw_row6_host_handle = 0U; }
        }
    }
    if (status != 0U) (void)open_cfw_row6_host_bitmap_update(6U, (open_cfw_row6_u8)bit, 0U);
    open_cfw_row6_host_critical_restore(mask);
    if (open_cfw_row6_host_ready != 0U) {
        if (status == 0U) (void)open_cfw_row6_host_mode_disable((open_cfw_row6_u8)(open_cfw_row6_host_selector ^ 1U), 0x35U);
        else { (void)open_cfw_row6_host_mode_disable(0U, 0x35U); (void)open_cfw_row6_host_mode_disable(1U, 0x35U); }
    }
    if (success != 0U) status = open_cfw_row6_host_finalize(open_cfw_row6_host_handle);
    return status;
#endif
}

OPEN_CFW_ROW6_ATTR
open_cfw_row6_u32 open_cfw_bootloader_row6_disable_422220(open_cfw_row6_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r4, r0\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #6\n"
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
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_any_4215ae\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x204]\n"
        "strb r0, [r1]\n"
        "ldr.w r4, [pc, #0x204]\n"
        "ldr r0, [r4]\n"
        "bl open_cfw_bootloader_row6_stop_4273dc\n"
        "ldr r0, [r4]\n"
        "bl open_cfw_bootloader_row6_destroy_427310\n"
        "movs r0, #0\n"
        "str r0, [r4]\n"
        "ldr r0, [pc, #0x1c0]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "b 3f\n"
        "2:\n"
        "movs r0, #0x35\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, #0\n"
        "4:\n"
        "pop {r1, r2, r4, pc}\n");
#else
    open_cfw_row6_u32 mask;
    if (open_cfw_row6_host_bitmap_test(6U, (open_cfw_row6_u8)bit) == 0U) return 0U;
    mask = open_cfw_row6_host_critical_save();
    (void)open_cfw_row6_host_bitmap_update(6U, (open_cfw_row6_u8)bit, 0U);
    if (open_cfw_row6_host_bitmap_any(6U) == 0U) {
        open_cfw_row6_host_pending = 0U;
        (void)open_cfw_row6_host_stop(open_cfw_row6_host_handle);
        (void)open_cfw_row6_host_destroy(open_cfw_row6_host_handle);
        open_cfw_row6_host_handle = 0U;
        (void)open_cfw_row6_host_mode_disable(open_cfw_row6_host_selector, 0x35U);
    }
    open_cfw_row6_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_ROW6_ATTR
open_cfw_row6_u32 open_cfw_bootloader_mode_dispatch_4222a0(
    open_cfw_row6_u32 kind,
    open_cfw_row6_uintptr instance,
    const open_cfw_row6_u32 *configuration)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r3, r1\n"
        "movs r1, r2\n"
        "uxtb r0, r0\n"
        "cmp r0, #4\n"
        "beq 1f\n"
        "blo 4f\n"
        "cmp r0, #6\n"
        "beq 3f\n"
        "blo 2f\n"
        "b 4f\n"
        "1:\n"
        "movs r0, r3\n"
        "bl open_cfw_bootloader_mode_service_4216d4\n"
        "b 5f\n"
        "2:\n"
        "movs r0, r3\n"
        "bl open_cfw_bootloader_dual_mode_service_4217d2\n"
        "b 5f\n"
        "3:\n"
        "movs r0, r3\n"
        "bl open_cfw_bootloader_bitmap_client_service_421978\n"
        "b 5f\n"
        "4:\n"
        "movs r0, #7\n"
        "5:\n"
        "pop {r1, pc}\n");
#else
    kind = (open_cfw_row6_u8)kind;
    if (kind < 4U || kind > 6U) return 7U;
    return open_cfw_row6_host_dispatch((open_cfw_row6_u8)kind, instance, configuration);
#endif
}
