#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "gxt310/gxt310.h"

typedef struct {
    size_t writes;
    uint8_t addresses[8];
    uint16_t operations[8];
    uint8_t commands[8][GXT310_COMMAND_BYTES];
    size_t lengths[8];
    size_t fail_at;
    size_t failures;
    gxt310_failure_operation last_failure;
    uint8_t last_failure_address;
} gxt310_trace;

static bool trace_write(void *context, uint8_t address, uint16_t operation,
                        const uint8_t *bytes, size_t length) {
    gxt310_trace *trace = context;
    const size_t index = trace->writes;
    assert(index < 8u);
    trace->addresses[index] = address;
    trace->operations[index] = operation;
    trace->lengths[index] = length;
    assert(length == GXT310_COMMAND_BYTES);
    memcpy(trace->commands[index], bytes, length);
    ++trace->writes;
    return trace->fail_at == 0u || trace->fail_at != trace->writes;
}

static void trace_failure(void *context, gxt310_failure_operation operation,
                          uint8_t address) {
    gxt310_trace *trace = context;
    ++trace->failures;
    trace->last_failure = operation;
    trace->last_failure_address = address;
}

void test_reconstructed_gxt310(void) {
    gxt310_trace trace = {0};
    gxt310_provider provider;
    gxt310_provider_initialize(&provider, trace_write, &trace,
                               trace_failure, &trace);

    assert(gxt310_channel_0_switch_mode(&provider, true) ==
           GXT310_STATUS_SUCCESS);
    assert(trace.writes == 1u);
    assert(trace.addresses[0] == GXT310_CHANNEL_0_ADDRESS);
    assert(trace.operations[0] == GXT310_WRITE_OPERATION);
    assert(trace.commands[0][0] == UINT8_C(0x00));
    assert(trace.commands[0][1] == UINT8_C(0xC2));

    assert(gxt310_channel_2_switch_mode(&provider, false) ==
           GXT310_STATUS_SUCCESS);
    assert(trace.addresses[1] == GXT310_CHANNEL_2_ADDRESS);
    assert(trace.commands[1][0] == UINT8_C(0x01));
    assert(trace.commands[1][1] == UINT8_C(0xC2));

    assert(gxt310_channel_0_trigger_one_shot(&provider) ==
           GXT310_STATUS_SUCCESS);
    assert(gxt310_channel_2_trigger_one_shot(&provider) ==
           GXT310_STATUS_SUCCESS);
    assert(trace.commands[2][0] == UINT8_C(0x01));
    assert(trace.commands[2][1] == UINT8_C(0xC1));
    assert(trace.commands[3][0] == UINT8_C(0x01));
    assert(trace.commands[3][1] == UINT8_C(0xC1));

    memset(&trace, 0, sizeof(trace));
    trace.fail_at = 1u;
    assert(gxt310_enable_pair(&provider) == GXT310_STATUS_FAILURE);
    assert(trace.writes == 2u); /* Stock does not short-circuit. */
    assert(trace.addresses[0] == GXT310_CHANNEL_0_ADDRESS);
    assert(trace.addresses[1] == GXT310_CHANNEL_2_ADDRESS);
    assert(trace.failures == 1u);
    assert(trace.last_failure == GXT310_FAILURE_SWITCH_MODE);
    assert(trace.last_failure_address == GXT310_CHANNEL_0_ADDRESS);

    assert(gxt310_switch_mode(&provider, UINT8_C(0x92), true) ==
           GXT310_STATUS_FAILURE);
    assert(trace.writes == 2u);
    assert(trace.failures == 2u);

    gxt310_provider_initialize(&provider, NULL, NULL, trace_failure, &trace);
    assert(gxt310_channel_0_trigger_one_shot(&provider) ==
           GXT310_STATUS_FAILURE);
    assert(trace.last_failure == GXT310_FAILURE_TRIGGER_ONE_SHOT);
}
