/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 hardware-control state mapper. */

typedef __UINT8_TYPE__ open_cfw_hwsm_u8;
typedef __UINT32_TYPE__ open_cfw_hwsm_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_control_state_423e14(void)
{
    __asm__ volatile(
        "ldr.w r2, [r0, #0x838]\n"
        "cmp r2, #1\n"
        "beq 1f\n"
        "cmp r2, #2\n"
        "beq 2f\n"
        "b 3f\n"
        "1:\n"
        "orr r1, r1, #0x4000\n"
        "orrs r1, r1, #0xa0\n"
        "movs r2, #2\n"
        "str.w r2, [r0, #0x838]\n"
        "b 4f\n"
        "2:\n"
        "mov.w r1, #0x4000\n"
        "b 4f\n"
        "3:\n"
        "orrs r1, r1, #0x4080\n"
        "4:\n"
        "movs r0, r1\n"
        "bx lr\n");
}
#else
typedef struct open_cfw_hwsm_context {
    open_cfw_hwsm_u8 prefix[0x838];
    open_cfw_hwsm_u32 state;
} open_cfw_hwsm_context;

open_cfw_hwsm_u32 open_cfw_bootloader_hw_control_state_423e14(
    open_cfw_hwsm_context *context, open_cfw_hwsm_u32 flags)
{
    if (context->state == 1U) {
        context->state = 2U;
        return flags | 0x40a0U;
    }
    if (context->state == 2U) return 0x4000U;
    return flags | 0x4080U;
}
#endif
