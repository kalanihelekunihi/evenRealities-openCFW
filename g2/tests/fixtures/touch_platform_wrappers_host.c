/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_platform_wrappers.c"

typedef struct test_log {
    uint32_t values[64];
    uint32_t count;
    uint32_t probe_result;
    uint32_t measurement;
} test_log;

static void push(test_log *log, uint32_t value)
{
    if (log->count < 64U) {
        log->values[log->count++] = value;
    }
}

static void configure_pair(void *context, uint32_t base, uint32_t descriptor)
{
    test_log *log = (test_log *)context;
    push(log, base);
    push(log, descriptor);
}

static void delay_call(void *context, uint32_t channel, uint32_t count)
{
    test_log *log = (test_log *)context;
    push(log, UINT32_C(0xD0000000) | channel);
    push(log, count);
}

static void install_call(void *context, uint32_t channel, uint32_t entry)
{
    test_log *log = (test_log *)context;
    push(log, UINT32_C(0xE0000000) | channel);
    push(log, entry);
}

static void sample_call(void *context, uint32_t destination, uint16_t value)
{
    test_log *log = (test_log *)context;
    push(log, destination);
    push(log, value);
}

static void start_call(void *context, uint32_t token)
{
    push((test_log *)context, token);
}

static void stage_call(void *context, uint32_t ordinal)
{
    push((test_log *)context, ordinal);
}

static void route_call(void *context, uint32_t base, uint32_t mode,
                       uint32_t descriptor)
{
    test_log *log = (test_log *)context;
    push(log, base);
    push(log, mode);
    push(log, descriptor);
}

static uint32_t probe_call(void *context, uint32_t state_token)
{
    test_log *log = (test_log *)context;
    push(log, state_token);
    return log->probe_result;
}

static uint32_t measure_call(void *context)
{
    return ((test_log *)context)->measurement;
}

static open_cfw_touch_platform_provider provider_for(test_log *log)
{
    open_cfw_touch_platform_provider provider = {
        configure_pair, delay_call, install_call, sample_call, start_call,
        stage_call, route_call, probe_call, measure_call, log,
    };
    return provider;
}

uint32_t open_cfw_test_touch_platform_wrappers(void)
{
    test_log log = {{0U}, 0U, 0U, 11U};
    open_cfw_touch_platform_provider provider = provider_for(&log);
    uint32_t stored = 0U;
    uint32_t record[12] = {0U};
    uint32_t result = 0U;

    open_cfw_touch_platform_0324_configure(&provider);
    result |= log.count == 2U && log.values[0] == UINT32_C(0x40250000) &&
                      log.values[1] == UINT32_C(0x200008EC) ? 1U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_0338_install(&provider, &stored, UINT32_C(0xAA55));
    result |= stored == UINT32_C(0xAA55) && log.count == 4U &&
                      log.values[0] == UINT32_C(0xD0000000) &&
                      log.values[1] == 40U &&
                      log.values[2] == UINT32_C(0xE0000000) &&
                      log.values[3] == UINT32_C(0x35E5) ? 2U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_0358_sample(&provider, UINT16_C(0xBEEF));
    result |= log.count == 2U && log.values[0] == UINT32_C(0x20000940) &&
                      log.values[1] == UINT32_C(0xBEEF) ? 4U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_0648_configure(&provider);
    result |= log.count == 2U && log.values[0] == UINT32_C(0x40290000) &&
                      log.values[1] == UINT32_C(0x200004EC) ? 8U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_09a4_start(&provider);
    result |= log.count == 1U && log.values[0] == UINT32_C(0x200004CC)
                  ? 16U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_11a0_sequence(&provider);
    result |= log.count == 4U && log.values[0] == 0U && log.values[3] == 3U
                  ? 32U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_11c4_sequence(&provider);
    result |= log.count == 5U && log.values[0] == 0U && log.values[4] == 4U
                  ? 64U : 0U;

    log.count = 0U;
    open_cfw_touch_platform_1238_routes(&provider);
    result |= log.count == 18U &&
                      log.values[0] == UINT32_C(0x40040200) &&
                      log.values[1] == 2U &&
                      log.values[2] == UINT32_C(0xB404) &&
                      log.values[15] == UINT32_C(0x40040400) &&
                      log.values[16] == 1U &&
                      log.values[17] == UINT32_C(0xB38C) ? 128U : 0U;

    log.count = 0U;
    log.probe_result = 0U;
    result |= open_cfw_touch_platform_1334_probe(&provider) ==
                      UINT32_C(0x06020000) &&
                      log.values[0] == UINT32_C(0x20000850) ? 256U : 0U;

    log.count = 0U;
    log.probe_result = 1U;
    result |= open_cfw_touch_platform_1350_initialize(&provider) == 0U &&
                      log.count == 6U && log.values[4] == 4U &&
                      log.values[5] == UINT32_C(0x20000850) ? 512U : 0U;

    result |= open_cfw_touch_platform_13f8_rounded_measurement(
                  &provider, 0U << 6) == 11U &&
                      open_cfw_touch_platform_13f8_rounded_measurement(
                          &provider, 1U << 6) == 6U &&
                      open_cfw_touch_platform_13f8_rounded_measurement(
                          &provider, 2U << 6) == 3U &&
                      open_cfw_touch_platform_13f8_rounded_measurement(
                          &provider, 3U << 6) == 1U ? 1024U : 0U;

    result |= open_cfw_touch_platform_156c_record_init(record, 12U) == 0U &&
                      record[0] == 0U && record[1] == UINT32_C(0x4781) &&
                      record[5] == UINT32_C(0x4861) &&
                      record[8] == 0U && record[9] == 0U &&
                      record[11] == UINT32_C(0x47AB) ? 2048U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_platform_null_guards(void)
{
    open_cfw_touch_platform_0324_configure((const open_cfw_touch_platform_provider *)0);
    open_cfw_touch_platform_0338_install((const open_cfw_touch_platform_provider *)0,
                                         (uint32_t *)0, 1U);
    open_cfw_touch_platform_0358_sample((const open_cfw_touch_platform_provider *)0, 1U);
    open_cfw_touch_platform_0648_configure((const open_cfw_touch_platform_provider *)0);
    open_cfw_touch_platform_09a4_start((const open_cfw_touch_platform_provider *)0);
    open_cfw_touch_platform_11a0_sequence((const open_cfw_touch_platform_provider *)0);
    open_cfw_touch_platform_11c4_sequence((const open_cfw_touch_platform_provider *)0);
    open_cfw_touch_platform_1238_routes((const open_cfw_touch_platform_provider *)0);
    return open_cfw_touch_platform_1334_probe(
               (const open_cfw_touch_platform_provider *)0) |
           open_cfw_touch_platform_1350_initialize(
               (const open_cfw_touch_platform_provider *)0) |
           open_cfw_touch_platform_13f8_rounded_measurement(
               (const open_cfw_touch_platform_provider *)0, 0U) |
           (open_cfw_touch_platform_156c_record_init((uint32_t *)0, 0U) ==
                    UINT32_C(0x06160003) ? 0U : 1U);
}
