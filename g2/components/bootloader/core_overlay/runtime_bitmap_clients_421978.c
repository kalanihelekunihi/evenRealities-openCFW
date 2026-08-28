/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader bitmap client services. */

typedef __UINT8_TYPE__ open_cfw_clients_u8;
typedef __UINT32_TYPE__ open_cfw_clients_u32;
typedef __UINTPTR_TYPE__ open_cfw_clients_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_clients_u32 open_cfw_bootloader_client_query_427160(
    open_cfw_clients_u32 *, open_cfw_clients_uintptr, open_cfw_clients_uintptr);
extern open_cfw_clients_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_clients_u32 open_cfw_bootloader_bitmap_count_4215fe(open_cfw_clients_u32);
extern open_cfw_clients_u32 open_cfw_bootloader_bitmap_test_4215dc(
    open_cfw_clients_u32, open_cfw_clients_u32);
extern open_cfw_clients_u32 open_cfw_bootloader_bitmap_update_421632(
    open_cfw_clients_u32, open_cfw_clients_u32, open_cfw_clients_u32);
extern void *open_cfw_bootloader_memcpy_41568c(
    void *, const void *, open_cfw_clients_u32);
#define OPEN_CFW_CLIENTS_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_clients_u32 open_cfw_clients_host_query(
    open_cfw_clients_u32 *, open_cfw_clients_uintptr, open_cfw_clients_uintptr);
open_cfw_clients_u32 open_cfw_clients_host_critical_save(void);
void open_cfw_clients_host_critical_restore(open_cfw_clients_u32);
open_cfw_clients_u32 open_cfw_clients_host_bitmap_count(open_cfw_clients_u32);
open_cfw_clients_u32 open_cfw_clients_host_bitmap_test(
    open_cfw_clients_u32, open_cfw_clients_u32);
open_cfw_clients_u32 open_cfw_clients_host_bitmap_update(
    open_cfw_clients_u32, open_cfw_clients_u32, open_cfw_clients_u32);
void open_cfw_clients_host_copy(void *, const void *, open_cfw_clients_u32);
extern open_cfw_clients_uintptr open_cfw_clients_host_controller0;
extern open_cfw_clients_uintptr open_cfw_clients_host_controller1;
extern open_cfw_clients_uintptr open_cfw_clients_host_controller_required;
extern open_cfw_clients_u32 open_cfw_clients_host_configuration[3];
extern open_cfw_clients_uintptr open_cfw_clients_host_current;
extern open_cfw_clients_u8 open_cfw_clients_host_ready;
#define OPEN_CFW_CLIENTS_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_CLIENTS_ATTR
open_cfw_clients_u32 open_cfw_bootloader_bitmap_client_service_421978(
    open_cfw_clients_uintptr instance,
    const open_cfw_clients_u32 *configuration)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "sub sp, #0x10\n"
        "movs r6, r0\n"
        "movs r5, r1\n"
        "movs r4, #0\n"
        "add r0, sp, #4\n"
        "movs r1, #0\n"
        "movs r2, #0\n"
        "movs r3, #0\n"
        "stm.w r0, {r1, r2, r3}\n"
        "cmp r5, #0\n"
        "bne 5f\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x884]\n"
        "ldr r0, [r1, #4]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, #0\n"
        "strb.w r0, [sp, #4]\n"
        "ldr r1, [r1, #4]\n"
        "1:\n"
        "movs r2, r6\n"
        "add r0, sp, #4\n"
        "bl open_cfw_bootloader_client_query_427160\n"
        "movs r4, r0\n"
        "add r5, sp, #4\n"
        "11:\n"
        "cmp r4, #0\n"
        "bne 9f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r0, #6\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "cmp r0, #0\n"
        "beq 7f\n"
        "movs r4, #3\n"
        "7:\n"
        "cmp r4, #0\n"
        "bne 8f\n"
        "movs r2, #0xc\n"
        "ldr.w r7, [pc, #0xa60]\n"
        "movs r1, r5\n"
        "movs r0, r7\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "ldr.w r0, [pc, #0xa58]\n"
        "str r6, [r0]\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xa54]\n"
        "strb r0, [r1]\n"
        "8:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "9:\n"
        "movs r0, r4\n"
        "10:\n"
        "add sp, #0x14\n"
        "pop {r4, r5, r6, r7, pc}\n"
        "2:\n"
        "ldr r0, [r1, #0x10]\n"
        "cmp r0, #0\n"
        "beq 4f\n"
        "movs r0, #1\n"
        "strb.w r0, [sp, #4]\n"
        "ldr r1, [r1, #0x10]\n"
        "b 1b\n"
        "4:\n"
        "movs r0, #7\n"
        "b 10b\n"
        "5:\n"
        "ldrb r0, [r5]\n"
        "cmp r0, #0\n"
        "bne 6f\n"
        "ldr.w r0, [pc, #0x80c]\n"
        "ldr r0, [r0, #4]\n"
        "cmp r0, #0\n"
        "bne 6f\n"
        "movs r0, #7\n"
        "b 10b\n"
        "6:\n"
        "ldrb r0, [r5]\n"
        "cmp r0, #1\n"
        "bne 11b\n"
        "ldr.w r0, [pc, #0x7f8]\n"
        "ldr r0, [r0, #0x10]\n"
        "cmp r0, #0\n"
        "bne 11b\n"
        "movs r0, #7\n"
        "b 10b\n");
#else
    open_cfw_clients_u32 local[3] = {0U, 0U, 0U};
    open_cfw_clients_u32 status = 0U;
    open_cfw_clients_u32 mask;
    if (configuration == (const open_cfw_clients_u32 *)0) {
        if (open_cfw_clients_host_controller0 != 0U) {
            ((open_cfw_clients_u8 *)local)[0] = 0U;
            status = open_cfw_clients_host_query(
                local, open_cfw_clients_host_controller0, instance);
        } else if (open_cfw_clients_host_controller1 != 0U) {
            ((open_cfw_clients_u8 *)local)[0] = 1U;
            status = open_cfw_clients_host_query(
                local, open_cfw_clients_host_controller1, instance);
        } else {
            return 7U;
        }
        configuration = local;
    } else {
        open_cfw_clients_u8 mode = ((const open_cfw_clients_u8 *)configuration)[0];
        if ((mode == 0U && open_cfw_clients_host_controller0 == 0U) ||
            (mode == 1U && open_cfw_clients_host_controller1 == 0U)) {
            return 7U;
        }
    }
    if (status != 0U) {
        return status;
    }
    mask = open_cfw_clients_host_critical_save();
    if (open_cfw_clients_host_bitmap_count(6U) != 0U) {
        status = 3U;
    }
    if (status == 0U) {
        open_cfw_clients_host_copy(open_cfw_clients_host_configuration,
                                   configuration, 12U);
        open_cfw_clients_host_current = instance;
        open_cfw_clients_host_ready = 1U;
    }
    open_cfw_clients_host_critical_restore(mask);
    return status;
#endif
}

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_CLIENTS_BITMAP_BODY(row, enabled, present_branch) \
    __asm__ volatile( \
        "push {r2, r3, r4, lr}\n" \
        "movs r4, r0\n" \
        "movs r1, r4\n" \
        "uxtb r1, r1\n" \
        "movs r0, #" #row "\n" \
        "bl open_cfw_bootloader_bitmap_test_4215dc\n" \
        "cmp r0, #0\n" \
        present_branch " 1f\n" \
        "movs r0, #0\n" \
        "b 2f\n" \
        "1:\n" \
        "bl open_cfw_bootloader_critical_save_41b8ec\n" \
        "str r0, [sp]\n" \
        "movs r2, #" #enabled "\n" \
        "movs r1, r4\n" \
        "uxtb r1, r1\n" \
        "movs r0, #" #row "\n" \
        "bl open_cfw_bootloader_bitmap_update_421632\n" \
        "ldr r0, [sp]\n" \
        "msr primask, r0\n" \
        "movs r0, #0\n" \
        "2:\n" \
        "pop {r1, r2, r4, pc}\n")
#endif

OPEN_CFW_CLIENTS_ATTR
open_cfw_clients_u32 open_cfw_bootloader_bitmap_row0_set_421a30(open_cfw_clients_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    OPEN_CFW_CLIENTS_BITMAP_BODY(0, 1, "beq");
#else
    open_cfw_clients_u32 mask;
    if (open_cfw_clients_host_bitmap_test(0U, (open_cfw_clients_u8)bit) != 0U) return 0U;
    mask = open_cfw_clients_host_critical_save();
    (void)open_cfw_clients_host_bitmap_update(0U, (open_cfw_clients_u8)bit, 1U);
    open_cfw_clients_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_CLIENTS_ATTR
open_cfw_clients_u32 open_cfw_bootloader_bitmap_row0_clear_421a62(open_cfw_clients_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    OPEN_CFW_CLIENTS_BITMAP_BODY(0, 0, "bne");
#else
    open_cfw_clients_u32 mask;
    if (open_cfw_clients_host_bitmap_test(0U, (open_cfw_clients_u8)bit) == 0U) return 0U;
    mask = open_cfw_clients_host_critical_save();
    (void)open_cfw_clients_host_bitmap_update(0U, (open_cfw_clients_u8)bit, 0U);
    open_cfw_clients_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_CLIENTS_ATTR
open_cfw_clients_u32 open_cfw_bootloader_bitmap_row1_set_421a94(open_cfw_clients_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "movs r4, r0\n"
        "movs r5, #0\n"
        "ldr.w r0, [pc, #0x780]\n"
        "ldr r0, [r0, #0xc]\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #7\n"
        "b 3f\n"
        "1:\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, #0\n"
        "b 3f\n"
        "2:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r2, #1\n"
        "movs r1, r4\n"
        "uxtb r1, r1\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r5\n"
        "3:\n"
        "pop {r1, r4, r5, pc}\n");
#else
    open_cfw_clients_u32 mask;
    if (open_cfw_clients_host_controller_required == 0U) return 7U;
    if (open_cfw_clients_host_bitmap_test(1U, (open_cfw_clients_u8)bit) != 0U) return 0U;
    mask = open_cfw_clients_host_critical_save();
    (void)open_cfw_clients_host_bitmap_update(1U, (open_cfw_clients_u8)bit, 1U);
    open_cfw_clients_host_critical_restore(mask);
    return 0U;
#endif
}

OPEN_CFW_CLIENTS_ATTR
open_cfw_clients_u32 open_cfw_bootloader_bitmap_row1_clear_421ad6(open_cfw_clients_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    OPEN_CFW_CLIENTS_BITMAP_BODY(1, 0, "bne");
#else
    open_cfw_clients_u32 mask;
    if (open_cfw_clients_host_bitmap_test(1U, (open_cfw_clients_u8)bit) == 0U) return 0U;
    mask = open_cfw_clients_host_critical_save();
    (void)open_cfw_clients_host_bitmap_update(1U, (open_cfw_clients_u8)bit, 0U);
    open_cfw_clients_host_critical_restore(mask);
    return 0U;
#endif
}
