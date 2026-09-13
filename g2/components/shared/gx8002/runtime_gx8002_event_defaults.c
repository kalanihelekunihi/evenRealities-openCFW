/* SPDX-License-Identifier: MIT */
/* Initialized event state at package 0x18d44. UINT32_MAX lies outside the
 * three-bit VAD domain, causing the first observed VAD state to be notified.
 * I2S start/stop and the event handler share the same pending byte.
 */
#include <stdint.h>
#include <stddef.h>
struct event_state { uint32_t last_vad; uint8_t pending; };
struct event_state open_cfw_gx8002_event_state
    __attribute__((section(".data.event_state"))) = {
        .last_vad = UINT32_MAX, .pending = 1
    };
_Static_assert(sizeof(struct event_state) == 8, "event state size");
_Static_assert(offsetof(struct event_state, pending) == 4, "I2S pending alias");
