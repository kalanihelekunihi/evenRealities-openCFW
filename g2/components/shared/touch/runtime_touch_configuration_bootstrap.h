/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_CONFIGURATION_BOOTSTRAP_H
#define OPENCFW_TOUCH_CONFIGURATION_BOOTSTRAP_H

#include <stdint.h>

#include "runtime_touch_storage_adapters.h"

#define OPEN_CFW_TOUCH_BOOTSTRAP_MAGIC 0x45564E55u
#define OPEN_CFW_TOUCH_BOOTSTRAP_DEFAULT_TIMEOUT_MS 1000u

typedef uint32_t (*open_cfw_touch_storage_write_provider)(
    uint32_t offset, const uint8_t *source, uint32_t size, void *context);
typedef void (*open_cfw_touch_delay_provider)(uint32_t milliseconds);

uint32_t open_cfw_touch_config_065c_bootstrap(
    open_cfw_touch_storage_state *storage,
    const open_cfw_touch_storage_provider *provider,
    open_cfw_touch_storage_write_provider write_provider,
    open_cfw_touch_delay_provider delay_provider, uint8_t config[8]);

#endif
