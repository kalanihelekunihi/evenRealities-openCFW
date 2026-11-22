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
