/* SPDX-License-Identifier: BSD-3-Clause */
/* Apollo510 SPOT-manager initialization at 0x0042ABBC. */

typedef __UINT32_TYPE__ open_cfw_spotmgr_init_u32;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_spotmgr_init_u32 open_cfw_bootloader_spotmgr_init_42abbc(void)
{
    __asm volatile(
        "push {r4, r5, lr}\n"
        "sub sp, #0x14\n"
        "ldr r0, [pc, #0x174]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #3, #1\n"
        "cmp r0, #0\n"
        "beq.n .Linit_gate_done\n"
        "ldr r0, [pc, #0x11c]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #27, #1\n"
        "ands r0, r0, #1\n"
        "eors r0, r0, #1\n"
        "b.n .Linit_gate_test\n"
        ".Linit_gate_done:\n"
        "movs r0, #0\n"
        ".Linit_gate_test:\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq.n .Linit_read\n"
        "movs r0, #7\n"
        "b.n .Linit_return\n"
        ".Linit_read:\n"
        "ldr r5, [pc, #0x64]\n"
        "adds r3, r5, #4\n"
        "movs r2, #0x14\n"
        "mov.w r1, #0x25c\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_mram_read_421548\n"
        "cmp r0, #0\n"
        "bne.n .Linit_return\n"
        "mov r3, sp\n"
        "movs r2, #5\n"
        "mov.w r1, #0x270\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_mram_read_421548\n"
        "cmp r0, #0\n"
        "bne.n .Linit_return\n"
        "ldr r0, [sp]\n"
        "str r0, [r5, #0x54]\n"
        "ldr r0, [sp, #4]\n"
        "str r0, [r5, #0x58]\n"
        "ldr r0, [sp, #8]\n"
        "str r0, [r5, #0x5c]\n"
        "ldr r0, [sp, #0xc]\n"
        "str r0, [r5, #0x60]\n"
        "ldr r0, [sp, #0x10]\n"
        "str r0, [r5, #0x64]\n"
        "mov r3, sp\n"
        "movs r2, #1\n"
        "mov.w r1, #0x278\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_mram_read_421548\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        "beq.n .Linit_commit\n"
        "movs r0, r4\n"
        "b.n .Linit_return\n"
        ".Linit_commit:\n"
        "ldr r0, [sp]\n"
        "str r0, [r5, #0x68]\n"
        "ldr r0, [pc, #0xa0]\n"
        "str r0, [r5]\n"
        "bl open_cfw_bootloader_spotmgr_runtime_init_41cc04\n"
        "movs r0, r4\n"
        ".Linit_return:\n"
        "add sp, #0x14\n"
        "pop {r4, r5, pc}\n"
    );
}

#else

typedef open_cfw_spotmgr_init_u32 (*open_cfw_spotmgr_read_hook)(
    open_cfw_spotmgr_init_u32 block, open_cfw_spotmgr_init_u32 offset,
    open_cfw_spotmgr_init_u32 words, open_cfw_spotmgr_init_u32 *destination,
    void *context);
typedef void (*open_cfw_spotmgr_init_hook)(void *context);

typedef struct open_cfw_spotmgr_init_state {
    open_cfw_spotmgr_init_u32 words[27];
} open_cfw_spotmgr_init_state;

__attribute__((used, noinline, visibility("default")))
open_cfw_spotmgr_init_u32 open_cfw_bootloader_spotmgr_init_42abbc(
    open_cfw_spotmgr_init_state *state, open_cfw_spotmgr_init_u32 power_ctrl,
    open_cfw_spotmgr_init_u32 mode_ctrl, open_cfw_spotmgr_read_hook read_hook,
    open_cfw_spotmgr_init_hook init_hook, void *context)
{
    open_cfw_spotmgr_init_u32 temporary[5];
    open_cfw_spotmgr_init_u32 status;
    if (((power_ctrl >> 3) & 1U) != 0U && ((mode_ctrl >> 27) & 1U) == 0U)
        return 7U;
    status = read_hook(1U, 0x25CU, 20U, &state->words[1], context);
    if (status != 0U) return status;
    status = read_hook(1U, 0x270U, 5U, temporary, context);
    if (status != 0U) return status;
    for (open_cfw_spotmgr_init_u32 index = 0U; index < 5U; ++index)
        state->words[21U + index] = temporary[index];
    status = read_hook(1U, 0x278U, 1U, temporary, context);
    if (status != 0U) return status;
    state->words[26] = temporary[0];
    state->words[0] = 0x1F01600DU;
    init_hook(context);
    return 0U;
}

#endif
