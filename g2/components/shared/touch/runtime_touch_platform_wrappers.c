/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Touch platform wrappers. Hardware and resident-library calls are
 * injected, so this unit contains no fixed-address access or MMIO execution.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_platform_wrappers.h"

void open_cfw_touch_platform_0324_configure(
    const open_cfw_touch_platform_provider *provider)
{
    if (provider != NULL && provider->configure_pair != NULL) {
        provider->configure_pair(provider->context, UINT32_C(0x40250000),
                                 UINT32_C(0x200008EC));
    }
}

void open_cfw_touch_platform_0338_install(
    const open_cfw_touch_platform_provider *provider,
    uint32_t *stored_argument, uint32_t argument)
{
    if (stored_argument != NULL) {
        *stored_argument = argument;
    }
    if (provider == NULL) {
        return;
    }
    if (provider->delay != NULL) {
        provider->delay(provider->context, 0U, 40U);
    }
    if (provider->install != NULL) {
        provider->install(provider->context, 0U, UINT32_C(0x35E5));
    }
}

void open_cfw_touch_platform_0358_sample(
    const open_cfw_touch_platform_provider *provider, uint16_t value)
{
    if (provider != NULL && provider->sample != NULL) {
        provider->sample(provider->context, UINT32_C(0x20000940), value);
    }
}

void open_cfw_touch_platform_0648_configure(
    const open_cfw_touch_platform_provider *provider)
{
    if (provider != NULL && provider->configure_pair != NULL) {
        provider->configure_pair(provider->context, UINT32_C(0x40290000),
                                 UINT32_C(0x200004EC));
    }
}

void open_cfw_touch_platform_09a4_start(
    const open_cfw_touch_platform_provider *provider)
{
    if (provider != NULL && provider->start != NULL) {
        provider->start(provider->context, UINT32_C(0x200004CC));
    }
}

void open_cfw_touch_platform_11a0_sequence(
    const open_cfw_touch_platform_provider *provider)
{
    uint32_t ordinal;

    if (provider == NULL || provider->stage == NULL) {
        return;
    }
    for (ordinal = 0U; ordinal < 4U; ++ordinal) {
        provider->stage(provider->context, ordinal);
    }
}

void open_cfw_touch_platform_11c4_sequence(
    const open_cfw_touch_platform_provider *provider)
{
    open_cfw_touch_platform_11a0_sequence(provider);
    if (provider != NULL && provider->stage != NULL) {
        provider->stage(provider->context, 4U);
    }
}

void open_cfw_touch_platform_1238_routes(
    const open_cfw_touch_platform_provider *provider)
{
    static const uint32_t routes[6][3] = {
        {UINT32_C(0x40040200), 2U, UINT32_C(0x0000B404)},
        {UINT32_C(0x40040200), 3U, UINT32_C(0x0000B3EC)},
        {UINT32_C(0x40040300), 2U, UINT32_C(0x0000B3D4)},
        {UINT32_C(0x40040300), 3U, UINT32_C(0x0000B3BC)},
        {UINT32_C(0x40040400), 0U, UINT32_C(0x0000B3A4)},
        {UINT32_C(0x40040400), 1U, UINT32_C(0x0000B38C)},
    };
    uint32_t index;

    if (provider == NULL || provider->route == NULL) {
        return;
    }
    for (index = 0U; index < 6U; ++index) {
        provider->route(provider->context, routes[index][0],
                        routes[index][1], routes[index][2]);
    }
}

uint32_t open_cfw_touch_platform_1334_probe(
    const open_cfw_touch_platform_provider *provider)
{
    if (provider == NULL || provider->probe == NULL) {
        return 0U;
    }
    return provider->probe(provider->context, UINT32_C(0x20000850)) != 0U
               ? 0U : UINT32_C(0x06020000);
}

uint32_t open_cfw_touch_platform_1350_initialize(
    const open_cfw_touch_platform_provider *provider)
{
    open_cfw_touch_platform_11c4_sequence(provider);
    return open_cfw_touch_platform_1334_probe(provider);
}

uint32_t open_cfw_touch_platform_13f8_rounded_measurement(
    const open_cfw_touch_platform_provider *provider, uint32_t control_word)
{
    uint32_t shift = (control_word >> 6) & 3U;
    uint32_t value;

    if (provider == NULL || provider->measure == NULL) {
        return 0U;
    }
    value = provider->measure(provider->context);
    return (value + ((UINT32_C(1) << shift) >> 1)) >> shift;
}

uint32_t open_cfw_touch_platform_156c_record_init(
    uint32_t *record, size_t words)
{
    if (record == NULL || words < 12U) {
        return UINT32_C(0x06160003);
    }
    record[0] = 0U;
    record[1] = UINT32_C(0x00004781);
    record[2] = UINT32_C(0x00004785);
    record[3] = UINT32_C(0x00004789);
    record[4] = UINT32_C(0x0000478D);
    record[5] = UINT32_C(0x00004861);
    record[6] = UINT32_C(0x00004811);
    record[7] = UINT32_C(0x000047B1);
    record[8] = 0U;
    record[9] = 0U;
    record[10] = UINT32_C(0x00004791);
    record[11] = UINT32_C(0x000047AB);
    return 0U;
}
