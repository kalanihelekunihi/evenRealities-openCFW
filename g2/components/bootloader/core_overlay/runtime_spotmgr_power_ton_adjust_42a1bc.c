/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Apollo510 SPOT-manager VDDC/VDDF Ton trim selector authenticated at G2
 * bootloader address 0x0042A1BC.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_ton_u32;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc(
    open_cfw_spotmgr_ton_u32 ton_state __attribute__((unused)),
    open_cfw_spotmgr_ton_u32 power_state __attribute__((unused)))
{
    __asm volatile(
        "cmp r1, #8\n"
        "bne.n .Lspot_ton_dispatch\n"
        "movs r0, #7\n"
        ".Lspot_ton_dispatch:\n"
        "cmp r0, #0\n"
        "beq.n .Lspot_ton_case0\n"
        "cmp r0, #2\n"
        "beq.n .Lspot_ton_case2\n"
        "blo.n .Lspot_ton_case1\n"
        "cmp r0, #4\n"
        "beq.n .Lspot_ton_case4\n"
        "blo.n .Lspot_ton_case3\n"
        "cmp r0, #6\n"
        "beq.n .Lspot_ton_case6\n"
        "blo.n .Lspot_ton_case5\n"
        "cmp r0, #7\n"
        "beq.n .Lspot_ton_case7\n"
        "b.n .Lspot_ton_default\n"
        ".Lspot_ton_case0:\n"
        "ldr.w r1, [pc, #0xa70]\n"
        "ldrb.w r0, [r1, #0x5c]\n"
        "ands r0, r0, #31\n"
        "ldr r1, [r1, #0x5c]\n"
        "ubfx r1, r1, #10, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case1:\n"
        "ldr.w r1, [pc, #0xa5c]\n"
        "ldr r0, [r1, #0x5c]\n"
        "ubfx r0, r0, #5, #5\n"
        "ldr r1, [r1, #0x5c]\n"
        "ubfx r1, r1, #15, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case2:\n"
        "ldr.w r1, [pc, #0xa48]\n"
        "ldrb.w r0, [r1, #0x54]\n"
        "ands r0, r0, #31\n"
        "ldrb.w r1, [r1, #0x58]\n"
        "ands r1, r1, #31\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case3:\n"
        "ldr.w r1, [pc, #0xa34]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #10, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #10, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case4:\n"
        "ldr.w r1, [pc, #0xa20]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #5, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #5, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case5:\n"
        "ldr.w r1, [pc, #0xa10]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #15, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #15, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case6:\n"
        "ldr.w r1, [pc, #0x9fc]\n"
        "ldrb.w r0, [r1, #0x60]\n"
        "ands r0, r0, #31\n"
        "ldr r1, [r1, #0x60]\n"
        "ubfx r1, r1, #10, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_case7:\n"
        "ldr.w r0, [pc, #0xa40]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #11, #5\n"
        "ldr.w r1, [pc, #0xa3c]\n"
        "ldr r1, [r1]\n"
        "ubfx r1, r1, #17, #5\n"
        "b.n .Lspot_ton_write\n"
        ".Lspot_ton_default:\n"
        "ldr.w r1, [pc, #0x9d4]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #15, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #15, #5\n"
        ".Lspot_ton_write:\n"
        "ldr.w r2, [pc, #0xa1c]\n"
        "ldr r3, [r2]\n"
        "bfi r3, r0, #25, #5\n"
        "str r3, [r2]\n"
        "ldr.w r0, [pc, #0xa18]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #8, #5\n"
        "str r2, [r0]\n"
        "bx lr\n"
    );
}

#else

typedef struct open_cfw_spotmgr_ton_state {
    open_cfw_spotmgr_ton_u32 gpu_vddc_ton;
    open_cfw_spotmgr_ton_u32 gpu_vddf_ton;
    open_cfw_spotmgr_ton_u32 stm_ton;
    open_cfw_spotmgr_ton_u32 default_ton;
    open_cfw_spotmgr_ton_u32 simobuck2;
    open_cfw_spotmgr_ton_u32 simobuck6;
    open_cfw_spotmgr_ton_u32 simobuck7;
} open_cfw_spotmgr_ton_state;

static open_cfw_spotmgr_ton_u32 open_cfw_spotmgr_ton_field(
    open_cfw_spotmgr_ton_u32 value,
    open_cfw_spotmgr_ton_u32 shift)
{
    return (value >> shift) & 31U;
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc(
    open_cfw_spotmgr_ton_u32 ton_state,
    open_cfw_spotmgr_ton_u32 power_state,
    open_cfw_spotmgr_ton_state *state)
{
    open_cfw_spotmgr_ton_u32 vddc;
    open_cfw_spotmgr_ton_u32 vddf;

    if (power_state == 8U) {
        ton_state = 7U;
    }
    switch (ton_state) {
    case 0U:
        vddc = open_cfw_spotmgr_ton_field(state->stm_ton, 0U);
        vddf = open_cfw_spotmgr_ton_field(state->stm_ton, 10U);
        break;
    case 1U:
        vddc = open_cfw_spotmgr_ton_field(state->stm_ton, 5U);
        vddf = open_cfw_spotmgr_ton_field(state->stm_ton, 15U);
        break;
    case 2U:
        vddc = open_cfw_spotmgr_ton_field(state->gpu_vddc_ton, 0U);
        vddf = open_cfw_spotmgr_ton_field(state->gpu_vddf_ton, 0U);
        break;
    case 3U:
        vddc = open_cfw_spotmgr_ton_field(state->gpu_vddc_ton, 10U);
        vddf = open_cfw_spotmgr_ton_field(state->gpu_vddf_ton, 10U);
        break;
    case 4U:
        vddc = open_cfw_spotmgr_ton_field(state->gpu_vddc_ton, 5U);
        vddf = open_cfw_spotmgr_ton_field(state->gpu_vddf_ton, 5U);
        break;
    case 6U:
        vddc = open_cfw_spotmgr_ton_field(state->default_ton, 0U);
        vddf = open_cfw_spotmgr_ton_field(state->default_ton, 10U);
        break;
    case 7U:
        vddc = open_cfw_spotmgr_ton_field(state->simobuck2, 11U);
        vddf = open_cfw_spotmgr_ton_field(state->simobuck6, 17U);
        break;
    case 5U:
    default:
        vddc = open_cfw_spotmgr_ton_field(state->gpu_vddc_ton, 15U);
        vddf = open_cfw_spotmgr_ton_field(state->gpu_vddf_ton, 15U);
        break;
    }
    state->simobuck2 = (state->simobuck2 & ~(31U << 25)) | (vddc << 25);
    state->simobuck7 = (state->simobuck7 & ~(31U << 8)) | (vddf << 8);
}

#endif
