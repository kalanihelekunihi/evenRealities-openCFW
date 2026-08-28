/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_PLATFORM_WRAPPERS_H
#define OPEN_CFW_RUNTIME_TOUCH_PLATFORM_WRAPPERS_H

#include <stddef.h>
#include <stdint.h>

typedef struct open_cfw_touch_platform_provider {
    void (*configure_pair)(void *context, uint32_t base, uint32_t descriptor);
    void (*delay)(void *context, uint32_t channel, uint32_t count);
    void (*install)(void *context, uint32_t channel, uint32_t entry);
    void (*sample)(void *context, uint32_t destination, uint16_t value);
    void (*start)(void *context, uint32_t token);
    void (*stage)(void *context, uint32_t ordinal);
    void (*route)(void *context, uint32_t base, uint32_t mode,
                  uint32_t descriptor);
    uint32_t (*probe)(void *context, uint32_t state_token);
    uint32_t (*measure)(void *context);
    void *context;
} open_cfw_touch_platform_provider;

void open_cfw_touch_platform_0324_configure(
    const open_cfw_touch_platform_provider *provider);
void open_cfw_touch_platform_0338_install(
    const open_cfw_touch_platform_provider *provider,
    uint32_t *stored_argument, uint32_t argument);
void open_cfw_touch_platform_0358_sample(
    const open_cfw_touch_platform_provider *provider, uint16_t value);
void open_cfw_touch_platform_0648_configure(
    const open_cfw_touch_platform_provider *provider);
void open_cfw_touch_platform_09a4_start(
    const open_cfw_touch_platform_provider *provider);
void open_cfw_touch_platform_11a0_sequence(
    const open_cfw_touch_platform_provider *provider);
void open_cfw_touch_platform_11c4_sequence(
    const open_cfw_touch_platform_provider *provider);
void open_cfw_touch_platform_1238_routes(
    const open_cfw_touch_platform_provider *provider);
uint32_t open_cfw_touch_platform_1334_probe(
    const open_cfw_touch_platform_provider *provider);
uint32_t open_cfw_touch_platform_1350_initialize(
    const open_cfw_touch_platform_provider *provider);
uint32_t open_cfw_touch_platform_13f8_rounded_measurement(
    const open_cfw_touch_platform_provider *provider, uint32_t control_word);
uint32_t open_cfw_touch_platform_156c_record_init(
    uint32_t *record, size_t words);

#endif
