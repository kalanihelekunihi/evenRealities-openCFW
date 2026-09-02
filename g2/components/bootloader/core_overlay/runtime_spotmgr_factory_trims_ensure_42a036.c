/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room realization of the authenticated G2 SPOT-manager factory-trim
 * readiness wrapper at 0x0042A036. The target body preserves the fixed shared
 * readiness literal and strict call edge; the host form exposes its branch.
 */

typedef __UINT32_TYPE__ open_cfw_factory_ensure_u32;
typedef __UINT8_TYPE__ open_cfw_factory_ensure_u8;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_spotmgr_load_factory_trims_429da4(void);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_factory_ensure_u32
open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036(void)
{
    __asm volatile(
        "push {r7, lr}\n"
        "ldr.w r0, [pc, #0x510]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "beq.n .Lfactory_trims_ready\n"
        "bl open_cfw_bootloader_spotmgr_load_factory_trims_429da4\n"
        ".Lfactory_trims_ready:\n"
        "movs r0, #0\n"
        "pop {r1, pc}\n"
    );
}

#else

typedef struct open_cfw_factory_ensure_state {
    open_cfw_factory_ensure_u8 factory_trims_pending;
    open_cfw_factory_ensure_u32 loader_calls;
} open_cfw_factory_ensure_state;

__attribute__((used, noinline, visibility("default")))
open_cfw_factory_ensure_u32
open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036(
    open_cfw_factory_ensure_state *state)
{
    if (state->factory_trims_pending != 0U) {
        state->loader_calls += 1U;
    }
    return 0U;
}

#endif
