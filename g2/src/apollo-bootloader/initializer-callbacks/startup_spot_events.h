/* SPDX-License-Identifier: BSD-3-Clause. Recovered register contracts. */
#ifndef OPENCFW_STARTUP_SPOT_EVENTS_H
#define OPENCFW_STARTUP_SPOT_EVENTS_H
#include <stdint.h>
/* Selector0 optionalstatebyte, selector1 requiredstatebyte, selector2 required
 * three-float buffer(input,lowerEndpoint,upperEndpoint). Only low selectorbyte
 * is consumed; R1 is unused by this handler. */
uint32_t state_event_dispatch_42d562_native(uint32_t selector,uint32_t unused,uint8_t *state);
uint32_t state_event_flag_set_42d5c2_native(void);
uint32_t state_event_finalize_42d5cc_native(void);
uint32_t autosw_initialize_42d63a_native(void);
#endif
