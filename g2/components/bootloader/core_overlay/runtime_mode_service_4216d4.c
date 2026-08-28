/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader mode/configuration service. */

typedef __UINT8_TYPE__ open_cfw_mode_u8;
typedef __UINT32_TYPE__ open_cfw_mode_u32;
typedef __UINTPTR_TYPE__ open_cfw_mode_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_mode_u32 open_cfw_bootloader_mode_query_426c4e(
    open_cfw_mode_u32, open_cfw_mode_uintptr, open_cfw_mode_u32 *);
extern open_cfw_mode_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_mode_u32 open_cfw_bootloader_bitmap_count_4215fe(open_cfw_mode_u32);
extern open_cfw_mode_u32 open_cfw_bootloader_mode_disable_426c7e(void);
extern open_cfw_mode_u32 open_cfw_bootloader_mode_apply_426c72(open_cfw_mode_u32);
extern void *open_cfw_bootloader_memcpy_41568c(void *, const void *, open_cfw_mode_u32);
#define OPEN_CFW_MODE_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_mode_u32 open_cfw_mode_host_query(
    open_cfw_mode_u32, open_cfw_mode_uintptr, open_cfw_mode_u32 *);
open_cfw_mode_u32 open_cfw_mode_host_critical_save(void);
void open_cfw_mode_host_critical_restore(open_cfw_mode_u32);
open_cfw_mode_u32 open_cfw_mode_host_bitmap_count(open_cfw_mode_u32);
open_cfw_mode_u32 open_cfw_mode_host_disable(void);
open_cfw_mode_u32 open_cfw_mode_host_apply(open_cfw_mode_u32);
void open_cfw_mode_host_copy(void *, const void *, open_cfw_mode_u32);
extern open_cfw_mode_u32 open_cfw_mode_host_controller;
extern open_cfw_mode_uintptr open_cfw_mode_host_current;
extern open_cfw_mode_u32 open_cfw_mode_host_fallback[3];
extern open_cfw_mode_u8 open_cfw_mode_host_aux_flag;
extern open_cfw_mode_u32 open_cfw_mode_host_aux_word;
extern open_cfw_mode_u8 open_cfw_mode_host_ready;
#define OPEN_CFW_MODE_ATTR __attribute__((used, noinline))
#endif

#define OPEN_CFW_MODE_SPECIAL ((open_cfw_mode_uintptr)0x02DC6C00U)

OPEN_CFW_MODE_ATTR
open_cfw_mode_u32 open_cfw_bootloader_mode_service_4216d4(
    open_cfw_mode_uintptr instance,
    const open_cfw_mode_u32 *configuration)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "sub sp, #0x10\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r5, #0\n"
        "add r0, sp, #4\n"
        "ldr.w r1, [pc, #0xb30]\n"
        "ldm.w r1, {r2, r3, r7}\n"
        "stm.w r0, {r2, r3, r7}\n"
        "cmp r4, #0\n"
        "beq 1f\n"
        "ldr.w r0, [pc, #0xb24]\n"
        "cmp r4, r0\n"
        "beq 1f\n"
        "movs r0, #5\n"
        "b 15f\n"
        "1:\n"
        "cmp r4, #0\n"
        "beq 3f\n"
        "ldr.w r3, [pc, #0xb18]\n"
        "ldr r0, [r3, #0xc]\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, #7\n"
        "b 15f\n"
        "2:\n"
        "cmp r6, #0\n"
        "bne 3f\n"
        "mov r2, sp\n"
        "movs r1, r4\n"
        "ldr r0, [r3, #0xc]\n"
        "bl open_cfw_bootloader_mode_query_426c4e\n"
        "movs r5, r0\n"
        "ldr r0, [sp]\n"
        "ldr r1, [sp, #4]\n"
        "bfi r1, r0, #8, #12\n"
        "str r1, [sp, #4]\n"
        "add r6, sp, #4\n"
        "3:\n"
        "cmp r5, #0\n"
        "bne 14f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "cmp r0, #0\n"
        "beq 9f\n"
        "movs r5, #3\n"
        "cmp r4, #0\n"
        "beq 4f\n"
        "ldr.w r0, [pc, #0xad0]\n"
        "cmp r4, r0\n"
        "bne 11f\n"
        "4:\n"
        "ldr.w r1, [pc, #0xb40]\n"
        "ldr r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldr r0, [r1]\n"
        "ldr.w r1, [pc, #0xabc]\n"
        "cmp r0, r1\n"
        "bne 11f\n"
        "5:\n"
        "cmp r4, #0\n"
        "bne 6f\n"
        "bl open_cfw_bootloader_mode_disable_426c7e\n"
        "movs r5, r0\n"
        "b 11f\n"
        "6:\n"
        "ldr r0, [r6]\n"
        "bl open_cfw_bootloader_mode_apply_426c72\n"
        "movs r5, r0\n"
        "cmp r5, #0\n"
        "beq 11f\n"
        "ldr.w r0, [pc, #0xb18]\n"
        "ldr r0, [r0]\n"
        "bl open_cfw_bootloader_mode_apply_426c72\n"
        "b 11f\n"
        "9:\n"
        "ldr.w r0, [pc, #0xb08]\n"
        "ldr r0, [r0]\n"
        "cmp r4, r0\n"
        "beq 11f\n"
        "bl open_cfw_bootloader_mode_disable_426c7e\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0xb00]\n"
        "strb r0, [r1]\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0xafc]\n"
        "str r0, [r1]\n"
        "11:\n"
        "cmp r5, #0\n"
        "bne 13f\n"
        "cmp r4, #0\n"
        "beq 12f\n"
        "movs r2, #0xc\n"
        "ldr.w r7, [pc, #0xae4]\n"
        "movs r1, r6\n"
        "movs r0, r7\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "12:\n"
        "ldr.w r0, [pc, #0xad4]\n"
        "str r4, [r0]\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xb10]\n"
        "strb r0, [r1]\n"
        "13:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "14:\n"
        "movs r0, r5\n"
        "15:\n"
        "add sp, #0x14\n"
        "pop {r4, r5, r6, r7, pc}\n");
#else
    open_cfw_mode_u32 local[3] = {0x0025B800U, 0U, 0U};
    open_cfw_mode_u32 derived = 0U;
    open_cfw_mode_u32 status = 0U;
    open_cfw_mode_u32 mask;

    if (instance != 0U && instance != OPEN_CFW_MODE_SPECIAL) {
        return 5U;
    }
    if (instance != 0U) {
        if (open_cfw_mode_host_controller == 0U) {
            return 7U;
        }
        if (configuration == (const open_cfw_mode_u32 *)0) {
            status = open_cfw_mode_host_query(
                open_cfw_mode_host_controller, instance, &derived);
            local[0] = (local[0] & ~0x000FFF00U) |
                ((derived & 0xFFFU) << 8U);
            configuration = local;
        }
    }
    if (status != 0U) {
        return status;
    }
    mask = open_cfw_mode_host_critical_save();
    if (open_cfw_mode_host_bitmap_count(4U) != 0U) {
        status = 3U;
        if ((instance == 0U || instance == OPEN_CFW_MODE_SPECIAL) &&
            (open_cfw_mode_host_current == 0U ||
             open_cfw_mode_host_current == OPEN_CFW_MODE_SPECIAL)) {
            if (instance == 0U) {
                status = open_cfw_mode_host_disable();
            } else {
                status = open_cfw_mode_host_apply(configuration[0]);
                if (status != 0U) {
                    (void)open_cfw_mode_host_apply(open_cfw_mode_host_fallback[0]);
                }
            }
        }
    } else if (instance != open_cfw_mode_host_current) {
        (void)open_cfw_mode_host_disable();
        open_cfw_mode_host_aux_flag = 0U;
        open_cfw_mode_host_aux_word = 0U;
    }
    if (status == 0U) {
        if (instance != 0U) {
            open_cfw_mode_host_copy(open_cfw_mode_host_fallback,
                                    configuration, 12U);
        }
        open_cfw_mode_host_current = instance;
        open_cfw_mode_host_ready = 1U;
    }
    open_cfw_mode_host_critical_restore(mask);
    return status;
#endif
}
