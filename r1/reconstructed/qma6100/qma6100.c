/* Owner-authorized R1 QMA6100 reconstruction. Not vendor source. */

#include "qma6100/qma6100.h"

static void zero_bytes(void *pointer, size_t length) {
    uint8_t *bytes = pointer;
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

static void lock(qma6100_device *device) {
    if (device != NULL && device->bindings.acquire != NULL) {
        device->bindings.acquire(device->bindings.lock_context);
    }
}

static void unlock(qma6100_device *device) {
    if (device != NULL && device->bindings.release != NULL) {
        device->bindings.release(device->bindings.lock_context);
    }
}

void qma6100_initialize(qma6100_device *device,
                        const qma6100_bindings *bindings) {
    if (device == NULL) {
        return;
    }
    zero_bytes(device, sizeof(*device));
    if (bindings != NULL) {
        device->bindings = *bindings;
    }
    device->address = QMA6100_ADDRESS_1;
    device->scale_lsb_per_g = UINT16_C(4096);
    /* Recovered six-halfword orientation table at stock 0x0009A6A6. */
    device->axis_sign[0] = UINT16_C(1);
    device->axis_sign[1] = UINT16_C(1);
    device->axis_sign[2] = UINT16_C(1);
    device->axis_map[0] = UINT16_C(0);
    device->axis_map[1] = UINT16_C(1);
    device->axis_map[2] = UINT16_C(2);
}

void qma6100_bind_events(qma6100_device *device,
                         qma6100_event_fn double_tap,
                         void *double_tap_context,
                         qma6100_event_fn any_motion,
                         void *any_motion_context) {
    if (device == NULL) {
        return;
    }
    device->double_tap = double_tap;
    device->double_tap_context = double_tap_context;
    device->any_motion = any_motion;
    device->any_motion_context = any_motion_context;
}

bool qma6100_identity_accepted(uint8_t chip_id) {
    return chip_id == QMA6100_DEVICE_ID ||
           (chip_id & QMA6100P_ID_MASK) == QMA6100P_ID_VALUE;
}

void qma6100_delay(qma6100_device *device, uint32_t units) {
    if (device == NULL || device->bindings.delay_cycles == NULL) {
        return;
    }
    while (units != 0u) {
        device->bindings.delay_cycles(device->bindings.transport_context,
                                      UINT32_C(64000));
        --units;
    }
}

uint32_t qma6100_read_retry(qma6100_device *device, uint8_t reg,
                            uint8_t *bytes, size_t length) {
    if (device == NULL || bytes == NULL || length == 0u ||
            device->bindings.read == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    for (size_t attempt = 0u; attempt < QMA6100_TRANSPORT_ATTEMPTS; ++attempt) {
        if (device->bindings.read(device->bindings.transport_context,
                                  device->address, reg, bytes, length)) {
            return QMA6100_STATUS_SUCCESS;
        }
        qma6100_delay(device, UINT32_C(5));
    }
    return QMA6100_STATUS_FAILURE;
}

uint32_t qma6100_write_retry(qma6100_device *device, uint8_t reg,
                             uint8_t value) {
    if (device == NULL || device->bindings.write == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    for (size_t attempt = 0u; attempt < QMA6100_TRANSPORT_ATTEMPTS; ++attempt) {
        if (device->bindings.write(device->bindings.transport_context,
                                   device->address, reg, &value, 1u)) {
            return QMA6100_STATUS_SUCCESS;
        }
    }
    return QMA6100_STATUS_FAILURE;
}

uint8_t qma6100_chip_id(qma6100_device *device) {
    uint8_t identifier = 0u;
    (void)qma6100_read_retry(device, UINT8_C(0x00), &identifier, 1u);
    return identifier;
}

uint32_t qma6100_set_range(qma6100_device *device, uint8_t range) {
    if (device == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    switch (range) {
    case 2u:
        device->scale_lsb_per_g = UINT16_C(2048);
        break;
    case 4u:
        device->scale_lsb_per_g = UINT16_C(1024);
        break;
    case 8u:
        device->scale_lsb_per_g = UINT16_C(512);
        break;
    case 15u:
        device->scale_lsb_per_g = UINT16_C(256);
        break;
    default:
        device->scale_lsb_per_g = UINT16_C(4096);
        break;
    }
    return qma6100_write_retry(device, UINT8_C(0x0F), range);
}

uint32_t qma6100_soft_reset(qma6100_device *device) {
    if (device == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    bool ok = qma6100_write_retry(device, UINT8_C(0x36), UINT8_C(0xB6)) != 0u;
    qma6100_delay(device, UINT32_C(5));
    ok = qma6100_write_retry(device, UINT8_C(0x36), UINT8_C(0x00)) != 0u && ok;
    qma6100_delay(device, UINT32_C(100));

    bool mode_ready = false;
    for (size_t attempt = 0u; attempt < QMA6100_RESET_POLL_ATTEMPTS; ++attempt) {
        ok = qma6100_write_retry(device, UINT8_C(0x11), UINT8_C(0x80)) != 0u && ok;
        qma6100_delay(device, UINT32_C(2));
        uint8_t value = 0u;
        ok = qma6100_read_retry(device, UINT8_C(0x11), &value, 1u) != 0u && ok;
        if (value == UINT8_C(0x80)) {
            mode_ready = true;
            break;
        }
    }

    ok = qma6100_write_retry(device, UINT8_C(0x33), UINT8_C(0x08)) != 0u && ok;
    qma6100_delay(device, UINT32_C(5));
    bool nvm_ready = false;
    for (size_t attempt = 0u; attempt < QMA6100_RESET_POLL_ATTEMPTS; ++attempt) {
        uint8_t value = 0u;
        ok = qma6100_read_retry(device, UINT8_C(0x33), &value, 1u) != 0u && ok;
        qma6100_delay(device, UINT32_C(10));
        if (value == UINT8_C(0x05)) {
            nvm_ready = true;
            break;
        }
    }
    return ok && mode_ready && nvm_ready ? QMA6100_STATUS_SUCCESS
                                         : QMA6100_STATUS_FAILURE;
}

static bool read_register(qma6100_device *device, uint8_t reg, uint8_t *value) {
    return qma6100_read_retry(device, reg, value, 1u) != 0u;
}

static bool write_register(qma6100_device *device, uint8_t reg, uint8_t value) {
    return qma6100_write_retry(device, reg, value) != 0u;
}

uint32_t qma6100_any_motion_configure(qma6100_device *device,
                                      uint8_t route, bool enabled) {
    if (device == NULL || route > 1u) {
        return QMA6100_STATUS_FAILURE;
    }
    uint8_t reg18 = 0u;
    uint8_t reg1a = 0u;
    uint8_t reg1c = 0u;
    uint8_t reg2c = 0u;
    bool ok = read_register(device, UINT8_C(0x18), &reg18);
    ok = read_register(device, UINT8_C(0x1A), &reg1a) && ok;
    ok = read_register(device, UINT8_C(0x1C), &reg1c) && ok;
    ok = read_register(device, UINT8_C(0x2C), &reg2c) && ok;
    reg2c = (uint8_t)(reg2c | UINT8_C(1));
    ok = write_register(device, UINT8_C(0x2C), reg2c) && ok;
    if (device->chip_id == UINT8_C(0x90) ||
            device->chip_id == QMA6100_DEVICE_ID) {
        ok = write_register(device, UINT8_C(0x2E), UINT8_C(0x10)) && ok;
    }
    ok = write_register(device, UINT8_C(0x2F), UINT8_C(0x00)) && ok;
    ok = write_register(device, UINT8_C(0x30), UINT8_C(0xFF)) && ok;

    if (enabled) {
        reg18 = (uint8_t)(reg18 | UINT8_C(7));
        reg1a = (uint8_t)(reg1a | UINT8_C(1));
        reg1c = (uint8_t)(reg1c | UINT8_C(1));
    } else {
        reg18 = (uint8_t)(reg18 & UINT8_C(0xF8));
        reg1a = (uint8_t)(reg1a & UINT8_C(0xFE));
        reg1c = (uint8_t)(reg1c & UINT8_C(0xFE));
    }
    ok = write_register(device, UINT8_C(0x18), reg18) && ok;
    ok = write_register(device, route == 0u ? UINT8_C(0x1A) : UINT8_C(0x1C),
                        route == 0u ? reg1a : reg1c) && ok;
    return ok ? QMA6100_STATUS_SUCCESS : QMA6100_STATUS_FAILURE;
}

uint32_t qma6100_step_configure(qma6100_device *device, bool enabled) {
    if (device == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    bool ok = write_register(device, UINT8_C(0x13), UINT8_C(0x80));
    qma6100_delay(device, UINT32_C(1));
    ok = write_register(device, UINT8_C(0x13), UINT8_C(0x7F)) && ok;
    if (!enabled) {
        return ok ? QMA6100_STATUS_SUCCESS : QMA6100_STATUS_FAILURE;
    }
    uint8_t reg12 = 0u;
    uint8_t reg14 = 0u;
    uint8_t reg15 = 0u;
    if (device->chip_id == UINT8_C(0x90)) {
        reg12 = UINT8_C(0x89);
        reg14 = UINT8_C(0x0B);
        reg15 = UINT8_C(0x0C);
    } else if (device->chip_id == QMA6100_DEVICE_ID) {
        reg12 = UINT8_C(0x89);
        reg14 = UINT8_C(0x0B);
        reg15 = UINT8_C(0x0E);
    }
    ok = write_register(device, UINT8_C(0x12), reg12) && ok;
    ok = write_register(device, UINT8_C(0x14), reg14) && ok;
    ok = write_register(device, UINT8_C(0x15), reg15) && ok;
    uint8_t reg1e = 0u;
    ok = read_register(device, UINT8_C(0x1E), &reg1e) && ok;
    reg1e = (uint8_t)(reg1e & UINT8_C(0x3F));
    ok = write_register(device, UINT8_C(0x1E), reg1e) && ok;
    if (device->chip_id == UINT8_C(0x90)) {
        ok = write_register(device, UINT8_C(0x1F), UINT8_C(0xA9)) && ok;
    } else if (device->chip_id == QMA6100_DEVICE_ID) {
        ok = write_register(device, UINT8_C(0x1F), UINT8_C(0xAA)) && ok;
    }
    return ok ? QMA6100_STATUS_SUCCESS : QMA6100_STATUS_FAILURE;
}

uint32_t qma6100_tap_configure(qma6100_device *device, uint8_t mask,
                               uint8_t route, bool enabled) {
    if (device == NULL || route > 1u) {
        return QMA6100_STATUS_FAILURE;
    }
    uint8_t reg16 = 0u;
    uint8_t reg19 = 0u;
    uint8_t reg1a = 0u;
    uint8_t reg1b = 0u;
    uint8_t reg1c = 0u;
    bool ok = read_register(device, UINT8_C(0x16), &reg16);
    ok = read_register(device, UINT8_C(0x19), &reg19) && ok;
    ok = read_register(device, UINT8_C(0x1A), &reg1a) && ok;
    ok = read_register(device, UINT8_C(0x1B), &reg1b) && ok;
    ok = read_register(device, UINT8_C(0x1C), &reg1c) && ok;
    ok = write_register(device, UINT8_C(0x1E), UINT8_C(3)) && ok;
    ok = write_register(device, UINT8_C(0x2A), UINT8_C(0x86)) && ok;
    ok = write_register(device, UINT8_C(0x2B), UINT8_C(0x85)) && ok;

    reg16 = enabled ? (uint8_t)(reg16 | mask)
                    : (uint8_t)(reg16 & (uint8_t)~mask);
    ok = write_register(device, UINT8_C(0x16), reg16) && ok;
    if (route == 0u) {
        if ((mask & UINT8_C(1)) != 0u) {
            reg1a = enabled ? (uint8_t)(reg1a | UINT8_C(2))
                            : (uint8_t)(reg1a & UINT8_C(0xFD));
            ok = write_register(device, UINT8_C(0x1A), reg1a) && ok;
        }
        reg19 = enabled ? (uint8_t)(reg19 | mask)
                        : (uint8_t)(reg19 & (uint8_t)~mask);
        ok = write_register(device, UINT8_C(0x19), reg19) && ok;
    } else {
        if ((mask & UINT8_C(1)) != 0u) {
            reg1c = enabled ? (uint8_t)(reg1c | UINT8_C(2))
                            : (uint8_t)(reg1c & UINT8_C(0xFD));
            ok = write_register(device, UINT8_C(0x1C), reg1c) && ok;
        }
        reg1b = enabled ? (uint8_t)(reg1b | mask)
                        : (uint8_t)(reg1b & (uint8_t)~mask);
        ok = write_register(device, UINT8_C(0x1B), reg1b) && ok;
    }
    return ok ? QMA6100_STATUS_SUCCESS : QMA6100_STATUS_FAILURE;
}

uint32_t qma6100_configure(qma6100_device *device, uint16_t rate_hz) {
    if (device == NULL || qma6100_soft_reset(device) == 0u) {
        return QMA6100_STATUS_FAILURE;
    }
    bool ok = write_register(device, UINT8_C(0x4A), UINT8_C(0x20));
    ok = write_register(device, UINT8_C(0x50), UINT8_C(0x51)) && ok;
    ok = write_register(device, UINT8_C(0x56), UINT8_C(1)) && ok;
    ok = qma6100_set_range(device, UINT8_C(4)) != 0u && ok;
    uint8_t odr = 0u;
    uint8_t bandwidth = 0u;
    bool rate_supported = true;
    switch (rate_hz) {
    case 25u:
        odr = UINT8_C(0);
        bandwidth = UINT8_C(0x86);
        break;
    case 50u:
        odr = UINT8_C(6);
        bandwidth = UINT8_C(0x84);
        break;
    case 100u:
        odr = UINT8_C(1);
        bandwidth = UINT8_C(0x85);
        break;
    case 150u:
    case 200u:
        odr = UINT8_C(2);
        bandwidth = UINT8_C(0x85);
        break;
    default:
        rate_supported = false;
        break;
    }
    if (rate_supported) {
        ok = write_register(device, UINT8_C(0x10), odr) && ok;
        ok = write_register(device, UINT8_C(0x11), bandwidth) && ok;
    }
    ok = write_register(device, UINT8_C(0x3E), UINT8_C(0x87)) && ok;
    ok = write_register(device, UINT8_C(0x4A), UINT8_C(0x28)) && ok;
    ok = write_register(device, UINT8_C(0x20), UINT8_C(5)) && ok;
    qma6100_delay(device, UINT32_C(5));
    ok = write_register(device, UINT8_C(0x5F), UINT8_C(0x80)) && ok;
    qma6100_delay(device, UINT32_C(5));
    ok = write_register(device, UINT8_C(0x5F), UINT8_C(0)) && ok;
    qma6100_delay(device, UINT32_C(5));
    ok = qma6100_step_configure(device, true) != 0u && ok;
    ok = qma6100_any_motion_configure(device, UINT8_C(0), true) != 0u && ok;
    ok = qma6100_tap_configure(device, UINT8_C(0x31), UINT8_C(0), true) != 0u && ok;
    return ok ? QMA6100_STATUS_SUCCESS : QMA6100_STATUS_FAILURE;
}

uint32_t qma6100_identity_and_configure(qma6100_device *device,
                                        uint16_t rate_hz) {
    if (device == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    static const uint8_t addresses[2] = {
        QMA6100_ADDRESS_1, QMA6100_ADDRESS_2,
    };
    for (size_t index = 0u; index < 2u; ++index) {
        device->address = addresses[index];
        device->chip_id = qma6100_chip_id(device);
        if (qma6100_identity_accepted(device->chip_id)) {
            return qma6100_configure(device, rate_hz);
        }
    }
    return QMA6100_STATUS_FAILURE;
}

void qma6100_interrupt(qma6100_device *device) {
    if (device == NULL) {
        return;
    }
    uint8_t status[4] = {0u, 0u, 0u, 0u};
    for (size_t attempt = 0u; attempt < 10u; ++attempt) {
        if (qma6100_read_retry(device, UINT8_C(0x09), status,
                               sizeof(status)) != 0u) {
            const uint32_t value = (uint32_t)status[0] |
                ((uint32_t)status[1] << 8u) |
                ((uint32_t)status[2] << 16u) |
                ((uint32_t)status[3] << 24u);
            if ((value & UINT32_C(7)) != 0u && device->any_motion != NULL) {
                device->any_motion(device->any_motion_context);
            }
            if ((value & UINT32_C(0x2000)) != 0u &&
                    device->double_tap != NULL) {
                device->double_tap(device->double_tap_context);
            }
            return;
        }
    }
}

uint32_t qma6100_read_fifo(qma6100_device *device, uint8_t *bytes,
                           size_t maximum_samples) {
    if (device == NULL || bytes == NULL) {
        return QMA6100_FIFO_ERROR;
    }
    uint8_t fifo_state = 0u;
    if (qma6100_read_retry(device, UINT8_C(0x0E), &fifo_state, 1u) == 0u) {
        return QMA6100_FIFO_ERROR;
    }
    size_t depth = (size_t)(fifo_state & UINT8_C(0x7F));
    if (depth > QMA6100_FIFO_MAX_SAMPLES) {
        return 0u;
    }
    if (depth > maximum_samples) {
        depth = maximum_samples;
    }
    if (depth != 0u && qma6100_read_retry(
            device, UINT8_C(0x3F), bytes,
            depth * QMA6100_FIFO_SAMPLE_BYTES) == 0u) {
        return QMA6100_FIFO_ERROR;
    }
    if (qma6100_write_retry(device, UINT8_C(0x3E), UINT8_C(0x87)) == 0u) {
        return QMA6100_FIFO_ERROR;
    }
    return (uint32_t)depth;
}

uint32_t qma6100_probe_wrapper(qma6100_device *device, uint8_t *chip_id) {
    if (device == NULL || chip_id == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    lock(device);
    *chip_id = qma6100_chip_id(device);
    unlock(device);
    return QMA6100_STATUS_SUCCESS;
}

uint32_t qma6100_configure_wrapper(qma6100_device *device,
                                   uint16_t requested_rate_hz) {
    if (device == NULL) {
        return QMA6100_STATUS_FAILURE;
    }
    lock(device);
    /* Stock wrapper hard-codes 25 Hz regardless of its table-call argument. */
    (void)requested_rate_hz;
    const uint32_t status = qma6100_identity_and_configure(device, UINT16_C(25));
    unlock(device);
    return status;
}

void qma6100_interrupt_wrapper(qma6100_device *device) {
    lock(device);
    qma6100_interrupt(device);
    unlock(device);
}

static int16_t arithmetic_shift_two(int16_t value) {
    const int32_t promoted = value;
    return promoted >= 0 ? (int16_t)(promoted / 4)
                         : (int16_t)(-(((-promoted) + 3) / 4));
}

uint32_t qma6100_fifo_wrapper(qma6100_device *device, uint8_t *bytes,
                              size_t maximum_samples) {
    lock(device);
    const uint32_t count = qma6100_read_fifo(device, bytes, maximum_samples);
    unlock(device);
    if (count == QMA6100_FIFO_ERROR) {
        return count;
    }
    for (size_t index = 0u; index < (size_t)count; ++index) {
        const size_t offset = index * QMA6100_FIFO_SAMPLE_BYTES;
        for (size_t axis = 0u; axis < 3u; ++axis) {
            const size_t position = offset + axis * 2u;
            const uint16_t raw = (uint16_t)bytes[position] |
                (uint16_t)((uint16_t)bytes[position + 1u] << 8u);
            const uint16_t normalized =
                (uint16_t)arithmetic_shift_two((int16_t)raw);
            bytes[position] = (uint8_t)normalized;
            bytes[position + 1u] = (uint8_t)(normalized >> 8u);
        }
    }
    return count;
}
