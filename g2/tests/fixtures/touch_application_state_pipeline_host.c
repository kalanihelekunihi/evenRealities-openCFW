/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

static uint8_t *host_pointers[256];
static uint32_t temporary_token = 240u;

void open_cfw_touch_host_register_pointer(uint32_t token, uint8_t *pointer)
{
    if (token < 256u) {
        host_pointers[token] = pointer;
    }
}

uint8_t *open_cfw_touch_host_resolve_pointer(uint32_t token)
{
    return token < 256u ? host_pointers[token] : NULL;
}

uint32_t open_cfw_touch_host_register_temporary(uint8_t *pointer)
{
    uint32_t token = temporary_token;
    temporary_token = temporary_token == 255u ? 240u : temporary_token + 1u;
    host_pointers[token] = pointer;
    return token;
}
