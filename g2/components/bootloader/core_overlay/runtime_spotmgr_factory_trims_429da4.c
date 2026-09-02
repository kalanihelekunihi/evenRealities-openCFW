/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room, reviewable realization of the trim-record loader authenticated
 * at G2 bootloader address 0x00429DA4. The target mnemonic body preserves the
 * fixed shared-literal topology; the host form makes the indexed extraction
 * semantics directly testable.
 */

typedef __UINT32_TYPE__ open_cfw_factory_trim_u32;
typedef __UINT8_TYPE__ open_cfw_factory_trim_u8;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_load_factory_trims_429da4(void)
{
    /*
     * Shared literals: LDOREG1 0x40020080, trim index 0x20000150,
     * trim table 0x20026BA0, VREFGEN2 0x40020044, ready byte 0x200271BC.
     */
    __asm volatile(
        "push {r4}\n"
        "ldr.w r0, [pc, #0x7a0]\n"
        "ldr.w r1, [pc, #0xabc]\n"
        "ldr r2, [pc, #0x2d4]\n"
        "ldr r3, [r1]\n"
        "add.w r3, r2, r3, lsl #2\n"
        "ldr r3, [r3, #4]\n"
        "lsrs r3, r3, #17\n"
        "ldr r4, [r0]\n"
        "bfi r4, r3, #10, #4\n"
        "str r4, [r0]\n"
        "ldr r3, [r1]\n"
        "add.w r3, r2, r3, lsl #2\n"
        "ldr r3, [r3, #4]\n"
        "lsrs r3, r3, #7\n"
        "ldr r4, [r0]\n"
        "bfi r4, r3, #0, #10\n"
        "str r4, [r0]\n"
        "ldr.w r0, [pc, #0xa94]\n"
        "ldr r1, [r1]\n"
        "add.w r1, r2, r1, lsl #2\n"
        "ldr r1, [r1, #4]\n"
        "lsrs r1, r1, #21\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #7\n"
        "str r2, [r0]\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x75c]\n"
        "strb r0, [r1]\n"
        "pop {r4}\n"
        "bx lr\n"
    );
}

#else

typedef struct open_cfw_factory_trim_state {
    open_cfw_factory_trim_u32 ldoreg1;
    open_cfw_factory_trim_u32 vrefgen2;
    open_cfw_factory_trim_u32 trim_index;
    open_cfw_factory_trim_u32 trim_words[17];
    open_cfw_factory_trim_u8 ready;
} open_cfw_factory_trim_state;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_load_factory_trims_429da4(
    open_cfw_factory_trim_state *state)
{
    open_cfw_factory_trim_u32 record =
        state->trim_words[state->trim_index + 1U];
    state->ldoreg1 = (state->ldoreg1 & ~(0xfU << 10)) |
        (((record >> 17) & 0xfU) << 10);
    state->ldoreg1 = (state->ldoreg1 & ~0x3ffU) |
        ((record >> 7) & 0x3ffU);
    state->vrefgen2 = (state->vrefgen2 & ~0x7fU) |
        ((record >> 21) & 0x7fU);
    state->ready = 0U;
}

#endif
