/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_STORAGE_ADAPTERS_H
#define OPENCFW_TOUCH_STORAGE_ADAPTERS_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TOUCH_STORAGE_LIMIT 256u
#define OPEN_CFW_TOUCH_STORAGE_ACCEPTED_STATUS 0x093E0004u

typedef struct {
    uint32_t (*initialize)(uint32_t *descriptor, void *context);
    uint32_t (*read)(uint32_t offset, uint8_t *destination,
                     uint32_t size, void *context);
    uint32_t (*context_operation)(void *context);
} open_cfw_touch_storage_provider;

typedef struct {
    uint32_t descriptor;
    void *provider_context;
    uint32_t counter;
    uint8_t initialized;
} open_cfw_touch_storage_state;

uint32_t open_cfw_touch_storage_01d8_initialize(
    open_cfw_touch_storage_state *state,
    const open_cfw_touch_storage_provider *provider);
uint32_t open_cfw_touch_storage_0220_read(
    open_cfw_touch_storage_state *state,
    const open_cfw_touch_storage_provider *provider, uint32_t offset,
    uint8_t *destination, uint32_t size);
uint32_t open_cfw_touch_storage_02b0_context_operation(
    open_cfw_touch_storage_state *state,
    const open_cfw_touch_storage_provider *provider);
void open_cfw_touch_storage_02e4_increment(open_cfw_touch_storage_state *state);

#endif
