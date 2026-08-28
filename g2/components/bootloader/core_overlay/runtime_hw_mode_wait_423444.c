/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 per-instance mode wait wrappers. */

typedef __UINT8_TYPE__ open_cfw_hwmw_u8;
typedef __UINT32_TYPE__ open_cfw_hwmw_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_mode_two_start_4234d8(void);
extern void open_cfw_bootloader_hw_mode_three_start_4234fa(void);
extern void open_cfw_bootloader_retained_hw_primary_progress_423524(void);
extern void open_cfw_bootloader_retained_hw_secondary_progress_423608(void);
extern void open_cfw_bootloader_retained_delay_41d1c0(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_mode_zero_wait_423444(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r5, r0\n"
        "movs r6, r1\n"
        "movs r7, #0\n"
        "movs r4, r5\n"
        "movs r1, r6\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_mode_two_start_4234d8\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "1:\n"
        "ldrb.w r0, [r4, #0x119]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_retained_hw_primary_progress_423524\n"
        "mov.w r0, #0x3e8\n"
        "bl open_cfw_bootloader_retained_delay_41d1c0\n"
        "ldr r0, [r6, #0xc]\n"
        "cmn.w r0, #1\n"
        "beq 1b\n"
        "adds r7, r7, #1\n"
        "ldr r0, [r6, #0xc]\n"
        "cmp r7, r0\n"
        "bne 1b\n"
        "movs r0, #0\n"
        "strb.w r0, [r4, #0x119]\n"
        "movs r0, #4\n"
        "b 3f\n"
        "2:\n"
        "movs r0, #0\n"
        "3:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_mode_one_wait_42348e(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r5, r0\n"
        "movs r6, r1\n"
        "movs r7, #0\n"
        "movs r4, r5\n"
        "movs r1, r6\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_mode_three_start_4234fa\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "1:\n"
        "ldrb.w r0, [r4, #0x11a]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_retained_hw_secondary_progress_423608\n"
        "mov.w r0, #0x3e8\n"
        "bl open_cfw_bootloader_retained_delay_41d1c0\n"
        "ldr r0, [r6, #0xc]\n"
        "cmn.w r0, #1\n"
        "beq 1b\n"
        "adds r7, r7, #1\n"
        "ldr r0, [r6, #0xc]\n"
        "cmp r7, r0\n"
        "bne 1b\n"
        "movs r0, #0\n"
        "strb.w r0, [r4, #0x11a]\n"
        "movs r0, #4\n"
        "b 3f\n"
        "2:\n"
        "movs r0, #0\n"
        "3:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n");
}
#else
typedef struct open_cfw_hwmw_instance { open_cfw_hwmw_u8 bytes[0x11c]; } open_cfw_hwmw_instance;
typedef struct open_cfw_hwmw_request { open_cfw_hwmw_u8 bytes[0x38]; } open_cfw_hwmw_request;
extern open_cfw_hwmw_u32 open_cfw_hwmw_host_mode_two_start(open_cfw_hwmw_instance *, open_cfw_hwmw_request *);
extern open_cfw_hwmw_u32 open_cfw_hwmw_host_mode_three_start(open_cfw_hwmw_instance *, open_cfw_hwmw_request *);
extern void open_cfw_hwmw_host_primary_progress(open_cfw_hwmw_instance *);
extern void open_cfw_hwmw_host_secondary_progress(open_cfw_hwmw_instance *);
extern void open_cfw_hwmw_host_delay(open_cfw_hwmw_u32);

static open_cfw_hwmw_u32 open_cfw_hwmw_read32(const open_cfw_hwmw_u8 *p)
{
    return (open_cfw_hwmw_u32)p[0] | ((open_cfw_hwmw_u32)p[1] << 8) |
           ((open_cfw_hwmw_u32)p[2] << 16) | ((open_cfw_hwmw_u32)p[3] << 24);
}

static open_cfw_hwmw_u32 open_cfw_hwmw_wait(open_cfw_hwmw_instance *instance,
    open_cfw_hwmw_request *request, open_cfw_hwmw_u32 active_offset,
    open_cfw_hwmw_u32 (*start)(open_cfw_hwmw_instance *, open_cfw_hwmw_request *),
    void (*progress)(open_cfw_hwmw_instance *))
{
    open_cfw_hwmw_u32 status = start(instance, request), count = 0U;
    if (status != 0U) return status;
    while (instance->bytes[active_offset] != 0U) {
        progress(instance); open_cfw_hwmw_host_delay(1000U);
        open_cfw_hwmw_u32 timeout = open_cfw_hwmw_read32(request->bytes + 0x0c);
        if (timeout != 0xffffffffU && ++count == timeout) {
            instance->bytes[active_offset] = 0U; return 4U;
        }
    }
    return 0U;
}

open_cfw_hwmw_u32 open_cfw_bootloader_hw_mode_zero_wait_423444(open_cfw_hwmw_instance *instance, open_cfw_hwmw_request *request)
{ return open_cfw_hwmw_wait(instance, request, 0x119U, open_cfw_hwmw_host_mode_two_start, open_cfw_hwmw_host_primary_progress); }
open_cfw_hwmw_u32 open_cfw_bootloader_hw_mode_one_wait_42348e(open_cfw_hwmw_instance *instance, open_cfw_hwmw_request *request)
{ return open_cfw_hwmw_wait(instance, request, 0x11aU, open_cfw_hwmw_host_mode_three_start, open_cfw_hwmw_host_secondary_progress); }
#endif
