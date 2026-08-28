/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 per-instance mode dispatch/start helpers. */

typedef __UINT8_TYPE__ open_cfw_hwmd_u8;
typedef __UINT32_TYPE__ open_cfw_hwmd_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_hw_mode_zero_423444(void);
extern void open_cfw_bootloader_retained_hw_mode_one_42348e(void);
extern void open_cfw_bootloader_hw_mode_two_start_4234d8(void);
extern void open_cfw_bootloader_hw_mode_three_start_4234fa(void);
extern void open_cfw_bootloader_hw_config_latch_422ee2(void);
extern void open_cfw_bootloader_hw_config_latch_secondary_422f4c(void);
extern void open_cfw_bootloader_retained_hw_primary_progress_423524(void);
extern void open_cfw_bootloader_retained_hw_secondary_progress_423608(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_mode_dispatch_4233e8(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldr r2, [r0]\n"
        "bic r2, r2, #0xfe000000\n"
        "ldr.w r3, [pc, #0x438]\n"
        "cmp r2, r3\n"
        "beq 1f\n"
        "5:\n"
        "movs r0, #2\n"
        "b 6f\n"
        "1:\n"
        "ldrb.w r2, [r1, #0x34]\n"
        "cmp r2, #0\n"
        "beq 2f\n"
        "cmp r2, #2\n"
        "beq 3f\n"
        "blo 4f\n"
        "cmp r2, #3\n"
        "beq 7f\n"
        "b 8f\n"
        "2:\n"
        "bl open_cfw_bootloader_retained_hw_mode_zero_423444\n"
        "b 6f\n"
        "4:\n"
        "bl open_cfw_bootloader_retained_hw_mode_one_42348e\n"
        "b 6f\n"
        "3:\n"
        "bl open_cfw_bootloader_hw_mode_two_start_4234d8\n"
        "b 6f\n"
        "7:\n"
        "bl open_cfw_bootloader_hw_mode_three_start_4234fa\n"
        "b 6f\n"
        "8:\n"
        "movs r0, #1\n"
        "6:\n"
        "pop {r1, pc}\n");
}

#if !defined(OPEN_CFW_HWMD_DISPATCH_ONLY)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_mode_two_start_4234d8(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "movs r4, r0\n"
        "ldr r0, [r1, #8]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r2, #0\n"
        "str r2, [r0]\n"
        "1:\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_config_latch_422ee2\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_retained_hw_primary_progress_423524\n"
        "movs r0, #0\n"
        "2:\n"
        "pop {r4, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_mode_three_start_4234fa(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "movs r5, r0\n"
        "movs r0, #0\n"
        "ldr r0, [r1, #8]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r2, #0\n"
        "str r2, [r0]\n"
        "1:\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_config_latch_secondary_422f4c\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        "beq 2f\n"
        "movs r0, r4\n"
        "b 3f\n"
        "2:\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_retained_hw_secondary_progress_423608\n"
        "movs r0, r4\n"
        "3:\n"
        "pop {r1, r4, r5, pc}\n");
}
#endif
#else
typedef struct open_cfw_hwmd_instance {
    open_cfw_hwmd_u8 bytes[0x11c];
} open_cfw_hwmd_instance;

typedef struct open_cfw_hwmd_request {
    open_cfw_hwmd_u8 bytes[0x38];
} open_cfw_hwmd_request;

extern open_cfw_hwmd_u32 open_cfw_hwmd_host_mode_zero(open_cfw_hwmd_instance *, open_cfw_hwmd_request *);
extern open_cfw_hwmd_u32 open_cfw_hwmd_host_mode_one(open_cfw_hwmd_instance *, open_cfw_hwmd_request *);
extern open_cfw_hwmd_u32 open_cfw_hwmd_host_primary_latch(open_cfw_hwmd_instance *);
extern open_cfw_hwmd_u32 open_cfw_hwmd_host_secondary_latch(open_cfw_hwmd_instance *);
extern void open_cfw_hwmd_host_primary_progress(open_cfw_hwmd_instance *);
extern void open_cfw_hwmd_host_secondary_progress(open_cfw_hwmd_instance *);
extern void open_cfw_hwmd_host_clear_status(open_cfw_hwmd_request *);

static open_cfw_hwmd_u32 open_cfw_hwmd_read32(const open_cfw_hwmd_u8 *p)
{
    return (open_cfw_hwmd_u32)p[0] | ((open_cfw_hwmd_u32)p[1] << 8) |
           ((open_cfw_hwmd_u32)p[2] << 16) | ((open_cfw_hwmd_u32)p[3] << 24);
}

open_cfw_hwmd_u32 open_cfw_bootloader_hw_mode_two_start_4234d8(open_cfw_hwmd_instance *instance, open_cfw_hwmd_request *request)
{
    open_cfw_hwmd_u32 pointer = open_cfw_hwmd_read32(request->bytes + 8);
    if (pointer != 0U) open_cfw_hwmd_host_clear_status(request);
    open_cfw_hwmd_u32 status = open_cfw_hwmd_host_primary_latch(instance);
    if (status == 0U) open_cfw_hwmd_host_primary_progress(instance);
    return status;
}

open_cfw_hwmd_u32 open_cfw_bootloader_hw_mode_three_start_4234fa(open_cfw_hwmd_instance *instance, open_cfw_hwmd_request *request)
{
    open_cfw_hwmd_u32 pointer = open_cfw_hwmd_read32(request->bytes + 8);
    if (pointer != 0U) open_cfw_hwmd_host_clear_status(request);
    open_cfw_hwmd_u32 status = open_cfw_hwmd_host_secondary_latch(instance);
    if (status == 0U) open_cfw_hwmd_host_secondary_progress(instance);
    return status;
}

open_cfw_hwmd_u32 open_cfw_bootloader_hw_mode_dispatch_4233e8(open_cfw_hwmd_instance *instance, open_cfw_hwmd_request *request)
{
    if (instance == (open_cfw_hwmd_instance *)0 ||
        (open_cfw_hwmd_read32(instance->bytes) & 0x01ffffffU) != 0x01ea9e06U)
        return 2U;
    switch (request->bytes[0x34]) {
    case 0U: return open_cfw_hwmd_host_mode_zero(instance, request);
    case 1U: return open_cfw_hwmd_host_mode_one(instance, request);
    case 2U: return open_cfw_bootloader_hw_mode_two_start_4234d8(instance, request);
    case 3U: return open_cfw_bootloader_hw_mode_three_start_4234fa(instance, request);
    default: return 1U;
    }
}
#endif
