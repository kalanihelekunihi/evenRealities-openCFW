/* Nordic nrf_fuel_gauge (GCC-built in stock, 0x439fe4..0x43bfa8) uses fused VFMA, so this unit
 * keeps clang's default in-expression contraction; the g2-apollo-main profiles set -ffp-contract=off
 * because the IAR-built remainder of the image never emits VFMA. */
#pragma clang fp contract(on)
/* SPDX-License-Identifier: MIT
 * Stock 0x0058EABC..0x0058EAC2: read cached TTE from model state.
 */
#include "g2c_fuel_gauge_model_tte.h"
#include <stddef.h>

_Static_assert(offsetof(struct nrf_model_state_tte_view, tte_seconds) == 0x84,
               "stock TTE model field offset");

__attribute__((noinline))
float nrf_model_tte_cached_58eabc(const struct nrf_model_state_tte_view *state)
{
    return state->tte_seconds;
}
