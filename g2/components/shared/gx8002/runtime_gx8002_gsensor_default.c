/* SPDX-License-Identifier: MIT */
/* Observed initialized diagnostic work-state word. The meaning of value one
 * and any indirect producers remain unresolved; do not label it an enum. */
#include <stdint.h>
volatile uint32_t open_cfw_gx8002_gsensor_state
    __attribute__((section(".data.gsensor_state"))) = 1;
