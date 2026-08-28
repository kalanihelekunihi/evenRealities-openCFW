/* SPDX-License-Identifier: MIT */
#include "pt_protocol_handlers_config.h"

static int open_cfw_pt_config_valid(
    const uint8_t *request, uint8_t length, uint8_t minimum)
{
    return request != NULL && length >= minimum;
}

static uint32_t open_cfw_pt_config_u32_le(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8U) |
        ((uint32_t)data[2] << 16U) | ((uint32_t)data[3] << 24U);
}

static void open_cfw_pt_config_put_u32_le(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8U);
    data[2] = (uint8_t)(value >> 16U);
    data[3] = (uint8_t)(value >> 24U);
}

static int open_cfw_pt_config_mode(
    const struct open_cfw_pt_config_providers *providers)
{
    uint8_t mode;
    if (providers == NULL || providers->get_product_mode == NULL ||
        providers->get_product_mode(&mode, providers->context) != 0) {
        return -1;
    }
    return mode == 1U ? 1 : 0;
}

static int open_cfw_pt_config_01(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    uint8_t current;
    uint8_t result;
    if (!open_cfw_pt_config_valid(r, n, 5U) || providers == NULL ||
        providers->get_product_mode == NULL || providers->set_product_mode == NULL ||
        providers->get_product_mode(&current, providers->context) != 0) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    if (r[4] > 1U) {
        result = 3U;
    } else if (r[4] == current) {
        result = 4U;
    } else if (providers->set_product_mode(r[4], providers->context) != 0) {
        result = 1U;
    } else {
        result = 0U;
    }
    return open_cfw_pt_make_status_payload(0x01U, result, 3U, p, l);
}

static int open_cfw_pt_config_26(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    int mode;
    if (!open_cfw_pt_config_valid(r, n, 4U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_config_mode(c);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    return open_cfw_pt_make_status_payload(0x30U, mode == 1 ? 0U : 5U, 3U, p, l);
}

static int open_cfw_pt_config_29(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_config_valid(r, n, 4U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_config_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->production_reset_action != NULL &&
        providers->production_reset_action(providers->context) == 0) result = 0U;
    return open_cfw_pt_make_status_payload(0x31U, result, 3U, p, l);
}

static int open_cfw_pt_config_30(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    uint8_t proximity;
    int16_t difference;
    if (!open_cfw_pt_config_valid(r, n, 4U) || providers == NULL ||
        providers->read_touch_diagnostic == NULL ||
        providers->read_touch_diagnostic(
            &proximity, &difference, providers->context) != 0 ||
        p == NULL || l == NULL) return OPEN_CFW_PT_HANDLER_FAILED;
    p[0] = 0x42U; p[1] = 1U; p[2] = 3U; p[3] = 3U;
    p[4] = proximity; p[5] = (uint8_t)difference;
    p[6] = (uint8_t)((uint16_t)difference >> 8U); *l = 7U;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_config_38(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_config_valid(r, n, 18U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_config_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->write_and_verify_psn_14 != NULL) {
        result = providers->write_and_verify_psn_14(
            r + 4U, 14U, providers->context) == 0 ? 0U : 1U;
    }
    return open_cfw_pt_make_status_payload(0x1CU, result, 3U, p, l);
}

static int open_cfw_pt_config_3a(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_config_valid(r, n, 40U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_config_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->write_sensor_calibration_36 != NULL) {
        result = providers->write_sensor_calibration_36(
            r + 4U, 36U, providers->context) == 0 ? 0U : 1U;
    }
    return open_cfw_pt_make_status_payload(0x2DU, result, 3U, p, l);
}

static int open_cfw_pt_config_42(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    int mode;
    uint8_t result;
    if (!open_cfw_pt_config_valid(r, n, 5U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_config_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode != 1) result = 5U;
    else if (r[4] > 1U) result = 1U;
    else if (providers->buzzer_test == NULL) return OPEN_CFW_PT_HANDLER_FAILED;
    else result = providers->buzzer_test(
        r[4] != 0U, 4000U, 30U, providers->context) == 0 ? 0U : 1U;
    return open_cfw_pt_make_status_payload(0x44U, result, 3U, p, l);
}

static int open_cfw_pt_config_62(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_config_valid(r, n, 9U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_config_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->buzzer_test != NULL) {
        result = providers->buzzer_test(1, open_cfw_pt_config_u32_le(r + 4U),
            r[8], providers->context) == 0 ? 0U : 1U;
    }
    return open_cfw_pt_make_status_payload(0x61U, result, 3U, p, l);
}

static int open_cfw_pt_config_63(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    uint32_t frequency;
    uint8_t duty;
    if (!open_cfw_pt_config_valid(r, n, 4U) || providers == NULL ||
        providers->buzzer_read == NULL ||
        providers->buzzer_read(&frequency, &duty, providers->context) != 0 ||
        p == NULL || l == NULL) return OPEN_CFW_PT_HANDLER_FAILED;
    p[0] = 0x62U; p[1] = 1U; p[2] = 3U; p[3] = 5U;
    open_cfw_pt_config_put_u32_le(p + 4U, frequency); p[8] = duty; *l = 9U;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_config_64(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    if (!open_cfw_pt_config_valid(r, n, 9U) || providers == NULL ||
        providers->buzzer_write == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    return open_cfw_pt_make_status_payload(0x63U,
        providers->buzzer_write(open_cfw_pt_config_u32_le(r + 4U), r[8],
            providers->context) == 0 ? 0U : 1U, 3U, p, l);
}

static int open_cfw_pt_config_66(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    uint8_t result;
    if (!open_cfw_pt_config_valid(r, n, 5U) || providers == NULL ||
        providers->update_onboarding == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    if (r[4] > 1U) result = 3U;
    else result = providers->update_onboarding(
        r[4] != 0U, providers->context) == 0 ? 0U : 1U;
    return open_cfw_pt_make_status_payload(0x65U, result, 3U, p, l);
}

static int open_cfw_pt_config_6a(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_config_providers *providers = c;
    if (!open_cfw_pt_config_valid(r, n, 5U) || providers == NULL ||
        providers->set_charger_test == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    if (providers->set_charger_test(r[4] != 0U, providers->context) != 0)
        return OPEN_CFW_PT_HANDLER_FAILED;
    return open_cfw_pt_make_status_payload(0x69U, 0U, 3U, p, l);
}

int open_cfw_pt_bind_config_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_config_providers *providers)
{
    static const struct { uint8_t command; open_cfw_pt_handler_fn handler; }
        bindings[] = {
            {0x01U, open_cfw_pt_config_01}, {0x26U, open_cfw_pt_config_26},
            {0x29U, open_cfw_pt_config_29}, {0x30U, open_cfw_pt_config_30},
            {0x38U, open_cfw_pt_config_38}, {0x3AU, open_cfw_pt_config_3a},
            {0x42U, open_cfw_pt_config_42}, {0x62U, open_cfw_pt_config_62},
            {0x63U, open_cfw_pt_config_63}, {0x64U, open_cfw_pt_config_64},
            {0x66U, open_cfw_pt_config_66}, {0x6AU, open_cfw_pt_config_6a},
        };
    size_t index;
    if (protocol == NULL || providers == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    for (index = 0U; index < sizeof(bindings) / sizeof(bindings[0]); ++index) {
        if (open_cfw_pt_protocol_bind(protocol, bindings[index].command,
                bindings[index].handler, (void *)providers) != 0)
            return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return OPEN_CFW_PT_OK;
}
