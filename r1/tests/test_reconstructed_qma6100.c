#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "qma6100/qma6100.h"

typedef struct {
    uint8_t registers[256];
    uint8_t fifo[QMA6100_FIFO_MAX_SAMPLES * QMA6100_FIFO_SAMPLE_BYTES];
    uint8_t address_1_id;
    uint8_t address_2_id;
    size_t read_calls;
    size_t write_calls;
    size_t delay_calls;
    uint64_t delayed_cycles;
    size_t read_failures_remaining;
    size_t write_failures_remaining;
    size_t acquire_calls;
    size_t release_calls;
    size_t any_motion_events;
    size_t double_tap_events;
} qma_trace;

static bool qma_read(void *context, uint8_t address, uint8_t reg,
                     uint8_t *bytes, size_t length) {
    qma_trace *trace = context;
    ++trace->read_calls;
    if (trace->read_failures_remaining != 0u) {
        --trace->read_failures_remaining;
        return false;
    }
    if (reg == UINT8_C(0x00) && length == 1u) {
        bytes[0] = address == QMA6100_ADDRESS_1
            ? trace->address_1_id : trace->address_2_id;
        return true;
    }
    if (reg == UINT8_C(0x11) && length == 1u) {
        bytes[0] = UINT8_C(0x80);
        return true;
    }
    if (reg == UINT8_C(0x33) && length == 1u) {
        bytes[0] = UINT8_C(0x05);
        return true;
    }
    if (reg == UINT8_C(0x3F)) {
        memcpy(bytes, trace->fifo, length);
        return true;
    }
    assert((size_t)reg + length <= sizeof(trace->registers));
    memcpy(bytes, &trace->registers[reg], length);
    return true;
}

static bool qma_write(void *context, uint8_t address, uint8_t reg,
                      const uint8_t *bytes, size_t length) {
    qma_trace *trace = context;
    (void)address;
    ++trace->write_calls;
    if (trace->write_failures_remaining != 0u) {
        --trace->write_failures_remaining;
        return false;
    }
    assert((size_t)reg + length <= sizeof(trace->registers));
    memcpy(&trace->registers[reg], bytes, length);
    return true;
}

static void qma_delay_cycles(void *context, uint32_t cycles) {
    qma_trace *trace = context;
    ++trace->delay_calls;
    trace->delayed_cycles += cycles;
}

static void qma_acquire(void *context) {
    ++((qma_trace *)context)->acquire_calls;
}

static void qma_release(void *context) {
    ++((qma_trace *)context)->release_calls;
}

static void qma_any_motion(void *context) {
    ++((qma_trace *)context)->any_motion_events;
}

static void qma_double_tap(void *context) {
    ++((qma_trace *)context)->double_tap_events;
}

static qma6100_device make_device(qma_trace *trace) {
    const qma6100_bindings bindings = {
        qma_read, qma_write, qma_delay_cycles, trace,
        qma_acquire, qma_release, trace,
    };
    qma6100_device device;
    qma6100_initialize(&device, &bindings);
    qma6100_bind_events(&device, qma_double_tap, trace,
                        qma_any_motion, trace);
    return device;
}

void test_reconstructed_qma6100(void) {
    assert(qma6100_identity_accepted(UINT8_C(0xFA)));
    assert(qma6100_identity_accepted(UINT8_C(0x90)));
    assert(qma6100_identity_accepted(UINT8_C(0x9F)));
    assert(!qma6100_identity_accepted(UINT8_C(0x8F)));

    qma_trace trace = {
        .address_1_id = UINT8_C(0x00),
        .address_2_id = UINT8_C(0xFA),
    };
    qma6100_device device = make_device(&trace);
    assert(device.address == QMA6100_ADDRESS_1);
    assert(device.scale_lsb_per_g == UINT16_C(4096));
    assert(device.axis_sign[0] == 1u && device.axis_sign[2] == 1u);
    assert(device.axis_map[0] == 0u && device.axis_map[2] == 2u);

    trace.read_failures_remaining = 4u;
    uint8_t value = 0u;
    assert(qma6100_read_retry(&device, UINT8_C(0), &value, 1u) ==
           QMA6100_STATUS_SUCCESS);
    assert(trace.read_calls == 5u && trace.delay_calls == 20u);
    trace.write_failures_remaining = 4u;
    assert(qma6100_write_retry(&device, UINT8_C(0x20), UINT8_C(7)) ==
           QMA6100_STATUS_SUCCESS);
    assert(trace.registers[0x20] == 7u);

    assert(qma6100_set_range(&device, UINT8_C(2)) == QMA6100_STATUS_SUCCESS);
    assert(device.scale_lsb_per_g == UINT16_C(2048));
    assert(trace.registers[0x0F] == 2u);
    assert(qma6100_set_range(&device, UINT8_C(4)) == QMA6100_STATUS_SUCCESS);
    assert(device.scale_lsb_per_g == UINT16_C(1024));
    assert(qma6100_set_range(&device, UINT8_C(8)) == QMA6100_STATUS_SUCCESS);
    assert(device.scale_lsb_per_g == UINT16_C(512));
    assert(qma6100_set_range(&device, UINT8_C(15)) == QMA6100_STATUS_SUCCESS);
    assert(device.scale_lsb_per_g == UINT16_C(256));
    assert(qma6100_set_range(&device, UINT8_C(1)) == QMA6100_STATUS_SUCCESS);
    assert(device.scale_lsb_per_g == UINT16_C(4096));

    assert(qma6100_soft_reset(&device) == QMA6100_STATUS_SUCCESS);
    assert(trace.registers[0x36] == 0u);
    assert(trace.registers[0x11] == UINT8_C(0x80));
    assert(trace.registers[0x33] == UINT8_C(0x08));

    device.chip_id = UINT8_C(0xFA);
    trace.registers[0x1E] = UINT8_C(0xFF);
    assert(qma6100_step_configure(&device, true) == QMA6100_STATUS_SUCCESS);
    assert(trace.registers[0x12] == UINT8_C(0x89));
    assert(trace.registers[0x14] == UINT8_C(0x0B));
    assert(trace.registers[0x15] == UINT8_C(0x0E));
    assert(trace.registers[0x1E] == UINT8_C(0x3F));
    assert(trace.registers[0x1F] == UINT8_C(0xAA));

    memset(&trace.registers[0x16], 0, 7u);
    assert(qma6100_tap_configure(
               &device, UINT8_C(0x31), UINT8_C(0), true) ==
           QMA6100_STATUS_SUCCESS);
    assert(trace.registers[0x16] == UINT8_C(0x31));
    assert(trace.registers[0x19] == UINT8_C(0x31));
    assert((trace.registers[0x1A] & UINT8_C(2)) != 0u);

    memset(&trace.registers[0x18], 0, 0x19u);
    assert(qma6100_any_motion_configure(&device, UINT8_C(0), true) ==
           QMA6100_STATUS_SUCCESS);
    assert((trace.registers[0x18] & UINT8_C(7)) == UINT8_C(7));
    assert((trace.registers[0x1A] & UINT8_C(1)) != 0u);
    assert(trace.registers[0x2E] == UINT8_C(0x10));
    assert(trace.registers[0x2F] == 0u);
    assert(trace.registers[0x30] == UINT8_C(0xFF));

    assert(qma6100_identity_and_configure(&device, UINT16_C(25)) ==
           QMA6100_STATUS_SUCCESS);
    assert(device.address == QMA6100_ADDRESS_2);
    assert(device.chip_id == QMA6100_DEVICE_ID);
    assert(trace.registers[0x10] == 0u);
    assert(trace.registers[0x11] == UINT8_C(0x86));
    assert(trace.registers[0x4A] == UINT8_C(0x28));
    assert(trace.registers[0x20] == UINT8_C(5));

    trace.registers[0x09] = UINT8_C(1);
    trace.registers[0x0A] = UINT8_C(0x20);
    qma6100_interrupt_wrapper(&device);
    assert(trace.any_motion_events == 1u);
    assert(trace.double_tap_events == 1u);
    assert(trace.acquire_calls == 1u && trace.release_calls == 1u);

    trace.registers[0x0E] = UINT8_C(2);
    static const uint8_t fifo[] = {
        0x07u, 0x00u, 0xF9u, 0xFFu, 0x00u, 0x10u,
        0xFFu, 0xFFu, 0x01u, 0x00u, 0x00u, 0xF0u,
    };
    memcpy(trace.fifo, fifo, sizeof(fifo));
    uint8_t output[sizeof(fifo)] = {0};
    assert(qma6100_fifo_wrapper(&device, output, 2u) == 2u);
    static const uint8_t normalized[] = {
        0x01u, 0x00u, 0xFEu, 0xFFu, 0x00u, 0x04u,
        0xFFu, 0xFFu, 0x00u, 0x00u, 0x00u, 0xFCu,
    };
    assert(memcmp(output, normalized, sizeof(output)) == 0);
    assert(trace.registers[0x3E] == UINT8_C(0x87));
    assert(trace.acquire_calls == 2u && trace.release_calls == 2u);

    trace.registers[0x0E] = UINT8_C(65);
    assert(qma6100_read_fifo(&device, output, 2u) == 0u);
    trace.read_failures_remaining = QMA6100_TRANSPORT_ATTEMPTS;
    assert(qma6100_read_fifo(&device, output, 2u) == QMA6100_FIFO_ERROR);
}
