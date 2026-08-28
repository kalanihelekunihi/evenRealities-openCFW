/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_configuration_bootstrap.h"

static uint16_t load_le16(const uint8_t *source)
{
    return (uint16_t)((uint16_t)source[0] | ((uint16_t)source[1] << 8u));
}

static void store_le16(uint8_t *destination, uint16_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
}

static uint32_t load_le32(const uint8_t *source)
{
    return (uint32_t)source[0] | ((uint32_t)source[1] << 8u) |
           ((uint32_t)source[2] << 16u) | ((uint32_t)source[3] << 24u);
}

static void store_le32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
    destination[2] = (uint8_t)(value >> 16u);
    destination[3] = (uint8_t)(value >> 24u);
}

uint32_t open_cfw_touch_config_065c_bootstrap(
    open_cfw_touch_storage_state *storage,
    const open_cfw_touch_storage_provider *provider,
    open_cfw_touch_storage_write_provider write_provider,
    open_cfw_touch_delay_provider delay_provider, uint8_t config[8])
{
    uint32_t status;

    if (config == NULL) {
        return 4u;
    }
    status = open_cfw_touch_storage_01d8_initialize(storage, provider);
    if (status != 0u) {
        return 1u;
    }
    status = open_cfw_touch_storage_0220_read(storage, provider, 0u, config, 8u);
    if (status == 0u && load_le32(config) == OPEN_CFW_TOUCH_BOOTSTRAP_MAGIC) {
        if (load_le16(&config[6]) == 0u) {
            store_le16(&config[6], OPEN_CFW_TOUCH_BOOTSTRAP_DEFAULT_TIMEOUT_MS);
        }
        return 0u;
    }
    if (open_cfw_touch_storage_02b0_context_operation(storage, provider) != 0u) {
        return 2u;
    }
    if (delay_provider == NULL || write_provider == NULL) {
        return 3u;
    }
    delay_provider(10u);
    store_le32(config, OPEN_CFW_TOUCH_BOOTSTRAP_MAGIC);
    store_le16(&config[4], 0u);
    store_le16(&config[6], OPEN_CFW_TOUCH_BOOTSTRAP_DEFAULT_TIMEOUT_MS);
    status = write_provider(0u, config, 8u, storage->provider_context);
    if (status != 0u && status != OPEN_CFW_TOUCH_STORAGE_ACCEPTED_STATUS) {
        return 3u;
    }
    return 0u;
}
