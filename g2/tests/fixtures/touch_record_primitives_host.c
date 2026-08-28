/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>
#include "runtime_touch_record_primitives.h"

void touch_host_record_copy_gate(
    const uint8_t *config, const uint8_t *source, uint8_t *destination,
    uint8_t *gate, int gate_available)
{
    open_cfw_touch_record_1b36_copy_gate(
        config, source, destination, gate_available ? gate : NULL);
}
