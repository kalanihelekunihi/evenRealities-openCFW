/* SPDX-License-Identifier: MIT */
#ifndef G2C_FUEL_GAUGE_MODEL_TTE_H
#define G2C_FUEL_GAUGE_MODEL_TTE_H

#include <stdint.h>

/* Recovered view of the stock model's cached TTE field at offset 0x84.
 * The preceding model fields are not yet reconstructed. */
struct nrf_model_state_tte_view {
    uint8_t opaque_before_tte[0x84];
    float tte_seconds;
};

float nrf_model_tte_cached_58eabc(const struct nrf_model_state_tte_view *state);

#endif
