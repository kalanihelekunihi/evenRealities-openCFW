#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "yhm2710/yhm2710.h"

typedef struct {
    uint32_t releases;
    uint32_t lows;
    uint32_t outputs;
    uint32_t inputs;
    uint32_t delays[256];
    size_t delay_count;
    uint8_t samples[4096];
    size_t sample_count;
    size_t sample_index;
    uint8_t registers[16];
    uint32_t reads;
    uint32_t writes;
    uint32_t acquires;
    uint32_t releases_lock;
    uint32_t completions;
    uint32_t completion_value;
} yhm_trace;

static yhm_trace *active_trace;

static void trace_low(uint32_t pin) {
    assert(pin == YHM2710_STACMD_GPIO);
    ++active_trace->lows;
}

static void trace_release(uint32_t pin) {
    assert(pin == YHM2710_STACMD_GPIO);
    ++active_trace->releases;
}

static void trace_output(uint32_t pin) {
    assert(pin == YHM2710_STACMD_GPIO);
    ++active_trace->outputs;
}

static void trace_input(uint32_t pin, uint32_t pull) {
    assert(pin == YHM2710_STACMD_GPIO);
    assert(pull == 3u);
    ++active_trace->inputs;
}

static uint32_t trace_read(uint32_t pin) {
    assert(pin == YHM2710_STACMD_GPIO);
    assert(active_trace->sample_index < active_trace->sample_count);
    return active_trace->samples[active_trace->sample_index++];
}

static void trace_delay(uint32_t cycles) {
    assert(active_trace->delay_count < 256u);
    active_trace->delays[active_trace->delay_count++] = cycles;
}

static bool register_read(void *context, uint8_t reg, uint8_t *bytes,
                          size_t length) {
    yhm_trace *trace = context;
    assert((size_t)reg + length <= sizeof(trace->registers));
    ++trace->reads;
    memcpy(bytes, &trace->registers[reg], length);
    return true;
}

static bool register_write(void *context, uint8_t reg, const uint8_t *bytes,
                           size_t length) {
    yhm_trace *trace = context;
    assert((size_t)reg + length <= sizeof(trace->registers));
    ++trace->writes;
    memcpy(&trace->registers[reg], bytes, length);
    return true;
}

static void lock_acquire(void *context) {
    ++((yhm_trace *)context)->acquires;
}

static void lock_release(void *context) {
    ++((yhm_trace *)context)->releases_lock;
}

static void completion(void *context, uint32_t value) {
    yhm_trace *trace = context;
    ++trace->completions;
    trace->completion_value = value;
}

static yhm2710_stacmd_device make_device(yhm_trace *trace) {
    active_trace = trace;
    const yhm2710_stacmd_line line = {
        YHM2710_STACMD_GPIO, trace_low, trace_release, trace_output,
        trace_input, 3u, trace_read, trace_delay,
    };
    yhm2710_stacmd_device device;
    yhm2710_stacmd_initialize(&device, &line);
    return device;
}

static void append_received_bit(yhm_trace *trace, uint8_t bit) {
    assert(trace->sample_count + 3u <= sizeof(trace->samples));
    trace->samples[trace->sample_count++] = 0u; /* falling edge */
    trace->samples[trace->sample_count++] = bit != 0u ? 0u : 1u;
    trace->samples[trace->sample_count++] = 1u; /* rising edge */
}

static void append_received_byte(yhm_trace *trace, uint8_t value) {
    for (int32_t bit = 7; bit >= 0; --bit) {
        append_received_bit(trace,
            (uint8_t)((value >> (uint32_t)bit) & UINT8_C(1)));
    }
}

void test_reconstructed_yhm2710(void) {
    assert(yhm2710_stacmd_parity(UINT8_C(0x00)) == 0u);
    assert(yhm2710_stacmd_parity(UINT8_C(0x01)) == 1u);
    assert(yhm2710_stacmd_parity(UINT8_C(0xA5)) == 0u);
    assert(yhm2710_stacmd_parity(UINT8_C(0xA7)) == 1u);

    yhm_trace trace = {0};
    yhm2710_stacmd_device device = make_device(&trace);
    assert(yhm2710_stacmd_operational(&device));
    assert(yhm2710_stacmd_open(&device) == YHM2710_STATUS_OK);
    assert(device.opened);

    yhm2710_stacmd_drive_bit(&device, 1u);
    assert(trace.outputs == 1u && trace.lows == 1u && trace.releases == 3u);
    assert(trace.delays[0] == 52u);
    yhm2710_stacmd_drive_bit(&device, 0u);
    assert(trace.delays[1] == 13u);

    const uint32_t releases_before = trace.releases;
    yhm2710_stacmd_bus_recovery(&device);
    assert(trace.releases == releases_before + 3u);
    assert(trace.delays[2] == 209u);
    assert(trace.delays[6] == 209u);

    memset(&trace, 0, sizeof(trace));
    active_trace = &trace;
    append_received_bit(&trace, 1u); /* parity of (0x42 << 1) | 1 */
    append_received_byte(&trace, UINT8_C(0xA0));
    uint8_t chip_id = 0u;
    assert(yhm2710_stacmd_read_frame(&device, UINT8_C(0x44), UINT8_C(2),
                                     &chip_id, 1u));
    assert(chip_id == UINT8_C(0xA0));
    assert(trace.sample_index == trace.sample_count);

    memset(&trace, 0, sizeof(trace));
    active_trace = &trace;
    append_received_bit(&trace, yhm2710_stacmd_parity(UINT8_C(0x82)));
    append_received_bit(&trace, yhm2710_stacmd_parity(UINT8_C(0xA8)));
    const uint8_t write_value = UINT8_C(0xA8);
    assert(yhm2710_stacmd_write_frame(&device, UINT8_C(0x44), UINT8_C(1),
                                      &write_value, 1u));

    yhm2710_stacmd_read_request read_request = {0};
    read_request.command = UINT8_C(8);
    read_request.buffer = &chip_id;
    read_request.length = 1u;
    assert(yhm2710_stacmd_close(&device) == YHM2710_STATUS_OK);
    assert(yhm2710_stacmd_read(&device, &read_request) ==
           YHM2710_STATUS_READ_NOT_OPEN);
    assert(yhm2710_stacmd_read(&device, NULL) ==
           YHM2710_STATUS_NULL_REQUEST);
    yhm2710_stacmd_write_request write_request = {0};
    write_request.command = UINT8_C(2);
    write_request.buffer = &write_value;
    write_request.length = 1u;
    assert(yhm2710_stacmd_write(&device, &write_request) ==
           YHM2710_STATUS_WRITE_NOT_OPEN);

    memset(&trace, 0, sizeof(trace));
    active_trace = &trace;
    const yhm2710_bindings bindings = {
        register_read, register_write, &trace,
        lock_acquire, lock_release, &trace,
        trace_delay, completion, &trace,
    };
    yhm2710_device chip;
    yhm2710_initialize(&chip, &bindings);
    trace.registers[8] = YHM2710_DEVICE_ID;
    assert(yhm2710_chip_id(&chip) == YHM2710_DEVICE_ID);
    assert(yhm2710_configure(&chip) == 0u);
    assert(trace.registers[0] == UINT8_C(0x6A));
    assert(trace.registers[1] == UINT8_C(0x4C));
    assert(trace.registers[2] == UINT8_C(0xA0));
    assert(trace.registers[3] == UINT8_C(0x02));
    assert(trace.delay_count == 50u);
    assert(trace.acquires == trace.releases_lock);
    assert(trace.completions == 5u && trace.completion_value == 0u);

    /* Readiness is the only device-policy primitive that samples the bound
     * physical line. */
    yhm2710_stacmd_device policy_transport = make_device(&trace);
    chip.transport = &policy_transport;
    trace.samples[0] = 1u;
    trace.sample_count = 1u;
    trace.sample_index = 0u;
    trace.registers[6] = UINT8_C(0xB0);
    assert(yhm2710_status(&chip) == UINT8_C(0x0B));
    trace.sample_index = 0u;
    assert(yhm2710_charge_state(&chip) == 1u);

    trace.registers[1] = UINT8_C(0x1F);
    trace.registers[9] = UINT8_C(0x5A);
    uint8_t register_9 = 0u;
    assert(yhm2710_read_register_9(&chip, &register_9));
    assert(register_9 == UINT8_C(0x5A));
    assert(yhm2710_set_ladder(&chip, 4.016f) == 1u);
    assert(trace.registers[1] == UINT8_C(0x3F));
    assert(yhm2710_set_ladder(&chip, 14.06f) == 2u);
    assert(trace.registers[1] == UINT8_C(0x5F));
    assert(yhm2710_set_system_track(&chip));
    assert((trace.registers[1] & UINT8_C(2)) != 0u);
    assert(yhm2710_clear_system_track(&chip));
    assert((trace.registers[1] & UINT8_C(2)) == 0u);
    trace.registers[3] = UINT8_C(0x42);
    assert(yhm2710_set_charging_event(&chip));
    assert(trace.registers[3] == UINT8_C(0x4a));
    assert(yhm2710_set_shared_power_active(&chip));
    assert(trace.registers[2] == UINT8_C(0xA8));
    assert(yhm2710_set_shared_power_inactive(&chip));
    assert(trace.registers[2] == UINT8_C(0x28));
    assert(yhm2710_set_shared_power_enabled(&chip, true));
    assert(trace.registers[2] == UINT8_C(0xA8));
    assert(yhm2710_set_shared_power_enabled(&chip, false));
    assert(trace.registers[2] == UINT8_C(0x28));
    assert(yhm2710_set_high_temperature(&chip));
    assert(trace.registers[2] == UINT8_C(0xF8));
}
