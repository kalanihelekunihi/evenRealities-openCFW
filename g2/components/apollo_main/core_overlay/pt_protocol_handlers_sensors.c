/*
 * SPDX-License-Identifier: MIT
 *
 * PT sensor and hardware-identification handlers.  The selector surfaces are
 * software-complete; physical qualification is blocked by unavailable physical
 * evidence.
 */

#include "pt_protocol_handlers_sensors.h"

static int open_cfw_pt_sensor_valid(
    const uint8_t *request, uint8_t length, uint8_t minimum)
{
    return request != NULL && length >= minimum;
}

static void open_cfw_pt_sensor_u16_le(uint8_t *output, uint16_t value)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8U);
}

static void open_cfw_pt_sensor_u32_le(uint8_t *output, uint32_t value)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8U);
    output[2] = (uint8_t)(value >> 16U);
    output[3] = (uint8_t)(value >> 24U);
}

static int open_cfw_pt_sensor_header(
    uint8_t command, uint8_t length, uint8_t *payload, uint8_t *payload_length)
{
    if (payload == NULL || payload_length == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    payload[0] = command; payload[1] = 1U; payload[2] = 3U; payload[3] = length;
    *payload_length = (uint8_t)(4U + length);
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_sensor_13(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_sensor_providers *providers = c;
    if (!open_cfw_pt_sensor_valid(r, n, 4U) || providers == NULL ||
        providers->read_latest_imu_sample_36 == NULL ||
        open_cfw_pt_sensor_header(0x17U, 36U, p, l) != 0)
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    return providers->read_latest_imu_sample_36(
        p + 4U, 36U, providers->context) == 0 ?
        OPEN_CFW_PT_OK : OPEN_CFW_PT_HANDLER_FAILED;
}

static int open_cfw_pt_sensor_17(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_sensor_providers *providers = c;
    int16_t differences[5];
    size_t index;
    if (!open_cfw_pt_sensor_valid(r, n, 4U) || providers == NULL ||
        providers->read_touch_differences == NULL ||
        providers->read_touch_differences(differences, providers->context) != 0 ||
        open_cfw_pt_sensor_header(0x18U, 8U, p, l) != 0)
        return OPEN_CFW_PT_HANDLER_FAILED;
    for (index = 0U; index < 4U; ++index)
        open_cfw_pt_sensor_u16_le(p + 4U + index * 2U,
            (uint16_t)differences[index]);
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_sensor_43(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_sensor_providers *providers = c;
    uint8_t orientation[12];
    int matches;
    size_t index;
    if (!open_cfw_pt_sensor_valid(r, n, 4U) || providers == NULL ||
        providers->read_calibration_and_orientation == NULL ||
        providers->read_calibration_and_orientation(
            &matches, orientation, providers->context) != 0 ||
        open_cfw_pt_sensor_header(0x45U, 13U, p, l) != 0)
        return OPEN_CFW_PT_HANDLER_FAILED;
    p[4] = matches != 0 ? 1U : 0U;
    for (index = 0U; index < 12U; ++index) p[5U + index] = orientation[index];
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_sensor_identifier(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l,
    const struct open_cfw_pt_sensor_providers *providers,
    open_cfw_pt_sensor_id_fn provider, uint8_t maximum_selector,
    uint8_t response_command)
{
    uint32_t identifier;
    if (!open_cfw_pt_sensor_valid(r, n, 5U) || providers == NULL ||
        provider == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    if (r[4] > maximum_selector) {
        return open_cfw_pt_make_status_payload(0x48U, 3U, 3U, p, l);
    }
    if (provider(r[4], &identifier, providers->context) != 0 ||
        open_cfw_pt_sensor_header(response_command, 4U, p, l) != 0)
        return OPEN_CFW_PT_HANDLER_FAILED;
    open_cfw_pt_sensor_u32_le(p + 4U, identifier);
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_sensor_47(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_sensor_providers *providers = c;
    return open_cfw_pt_sensor_identifier(r, n, p, l, providers,
        providers == NULL ? NULL : providers->read_hardware_identifier,
        7U, 0x47U);
}

static int open_cfw_pt_sensor_48(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_sensor_providers *providers = c;
    return open_cfw_pt_sensor_identifier(r, n, p, l, providers,
        providers == NULL ? NULL : providers->read_platform_identifier,
        2U, 0x48U);
}

int open_cfw_pt_bind_sensor_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_sensor_providers *providers)
{
    static const struct { uint8_t command; open_cfw_pt_handler_fn handler; }
        bindings[] = {
            {0x13U, open_cfw_pt_sensor_13}, {0x17U, open_cfw_pt_sensor_17},
            {0x43U, open_cfw_pt_sensor_43}, {0x47U, open_cfw_pt_sensor_47},
            {0x48U, open_cfw_pt_sensor_48},
        };
    size_t index;
    if (protocol == NULL || providers == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    for (index = 0U; index < sizeof(bindings) / sizeof(bindings[0]); ++index)
        if (open_cfw_pt_protocol_bind(protocol, bindings[index].command,
                bindings[index].handler, (void *)providers) != 0)
            return OPEN_CFW_PT_HANDLER_FAILED;
    return OPEN_CFW_PT_OK;
}
