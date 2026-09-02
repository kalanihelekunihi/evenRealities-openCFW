/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Apollo510 SPOT-manager internal-power-domain transition marker
 * authenticated at G2 bootloader address 0x0042A19C.
 */

typedef __UINT8_TYPE__ open_cfw_spotmgr_domain_u8;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_internal_power_domain_42a19c(
    open_cfw_spotmgr_domain_u8 requested_state __attribute__((unused)),
    open_cfw_spotmgr_domain_u8 prior_state __attribute__((unused)))
{
    __asm volatile(
        "uxtb r1, r1\n"
        "cmp r1, #1\n"
        "bne.n .Lspot_domain_return\n"
        "uxtb r0, r0\n"
        "cmp r0, #2\n"
        "bne.n .Lspot_domain_return\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xaf8]\n"
        "strb r0, [r1]\n"
        ".Lspot_domain_return:\n"
        "bx lr\n"
    );
}

#else

typedef struct open_cfw_spotmgr_domain_state {
    open_cfw_spotmgr_domain_u8 hp_to_deep_sleep;
} open_cfw_spotmgr_domain_state;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_internal_power_domain_42a19c(
    open_cfw_spotmgr_domain_u8 requested_state,
    open_cfw_spotmgr_domain_u8 prior_state,
    open_cfw_spotmgr_domain_state *state)
{
    if ((prior_state == 1U) && (requested_state == 2U)) {
        state->hp_to_deep_sleep = 1U;
    }
}

#endif
