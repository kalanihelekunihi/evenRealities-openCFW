/* Owner-authorized R1 YHM2710 reconstruction. Not vendor source. */

#include "yhm2710/yhm2710.h"

enum {
    YHM2710_RECOVERY_DELAY = 209,
    YHM2710_ONE_PULSE_DELAY = 52,
    YHM2710_ZERO_PULSE_DELAY = 13,
    YHM2710_SAMPLE_DELAY = 26
};

static void spin_delay(yhm2710_stacmd_device *device, uint32_t cycles) {
    if (device != NULL && device->line.delay_cycles != NULL) {
        device->line.delay_cycles(cycles);
        return;
    }
    /* Preserve an observable bounded delay in freestanding builds even when
     * the board port does not supply a calibrated cycle callback. */
    volatile uint32_t count = 0u;
    while (count < cycles) {
        ++count;
    }
}

bool yhm2710_stacmd_operational(const yhm2710_stacmd_device *device) {
    return device != NULL && device->line.drive_low != NULL &&
           device->line.release_high != NULL &&
           device->line.set_output != NULL &&
           device->line.set_input != NULL && device->line.read_pin != NULL;
}

void yhm2710_stacmd_initialize(yhm2710_stacmd_device *device,
                               const yhm2710_stacmd_line *line) {
    if (device == NULL) {
        return;
    }
    device->opened = false;
    device->failed_transactions = 0u;
    device->line.pin = YHM2710_STACMD_GPIO;
    device->line.drive_low = NULL;
    device->line.release_high = NULL;
    device->line.set_output = NULL;
    device->line.set_input = NULL;
    device->line.input_pull = 0u;
    device->line.read_pin = NULL;
    device->line.delay_cycles = NULL;
    if (line != NULL) {
        device->line = *line;
    }
}

uint8_t yhm2710_stacmd_parity(uint8_t value) {
    uint8_t parity = 0u;
    for (uint32_t bit = 0u; bit < 8u; ++bit) {
        parity = (uint8_t)(parity ^ ((value >> bit) & UINT8_C(1)));
    }
    return parity;
}

void yhm2710_stacmd_drive_bit(yhm2710_stacmd_device *device, uint8_t bit) {
    if (!yhm2710_stacmd_operational(device)) {
        return;
    }
    const uint32_t pin = device->line.pin;
    /* Both symbols use the same pulse edges; the encoded value is the low
     * pulse width (52 loop iterations for one, 13 for zero). */
    device->line.release_high(pin);
    device->line.set_output(pin);
    device->line.release_high(pin);
    device->line.drive_low(pin);
    spin_delay(device, bit != 0u ? YHM2710_ONE_PULSE_DELAY
                                 : YHM2710_ZERO_PULSE_DELAY);
    device->line.release_high(pin);
}

void yhm2710_stacmd_write_bits(yhm2710_stacmd_device *device,
                               uint8_t value, bool seven_bits) {
    int32_t bit = seven_bits ? 6 : 7;
    while (bit >= 0) {
        yhm2710_stacmd_drive_bit(device,
            (uint8_t)((value >> (uint32_t)bit) & UINT8_C(1)));
        --bit;
    }
}

void yhm2710_stacmd_bus_recovery(yhm2710_stacmd_device *device) {
    if (!yhm2710_stacmd_operational(device)) {
        return;
    }
    const uint32_t pin = device->line.pin;
    device->line.release_high(pin);
    device->line.set_output(pin);
    device->line.release_high(pin);
    spin_delay(device, YHM2710_RECOVERY_DELAY);
    device->line.drive_low(pin);
    for (uint32_t index = 0u; index < 4u; ++index) {
        spin_delay(device, YHM2710_RECOVERY_DELAY);
    }
    device->line.release_high(pin);
}

void yhm2710_stacmd_idle(yhm2710_stacmd_device *device) {
    if (!yhm2710_stacmd_operational(device)) {
        return;
    }
    const uint32_t pin = device->line.pin;
    device->line.release_high(pin);
    device->line.set_output(pin);
    device->line.release_high(pin);
    device->line.drive_low(pin);
    spin_delay(device, YHM2710_RECOVERY_DELAY);
    device->line.release_high(pin);
}

bool yhm2710_stacmd_read_bit(yhm2710_stacmd_device *device, uint8_t *bit) {
    if (!yhm2710_stacmd_operational(device) || bit == NULL) {
        return false;
    }
    const uint32_t pin = device->line.pin;
    device->line.set_input(pin, device->line.input_pull);
    bool edges_valid = false;
    for (uint32_t count = 0u; count < YHM2710_STACMD_EDGE_POLLS; ++count) {
        if (device->line.read_pin(pin) != 1u) {
            edges_valid = true;
            break;
        }
    }
    spin_delay(device, YHM2710_SAMPLE_DELAY);
    const uint32_t sample = device->line.read_pin(pin);
    bool rising_edge = false;
    for (uint32_t count = 0u; count < YHM2710_STACMD_EDGE_POLLS; ++count) {
        if (device->line.read_pin(pin) != 0u) {
            rising_edge = true;
            break;
        }
    }
    *bit = (uint8_t)((~sample) & UINT32_C(1));
    return edges_valid && rising_edge;
}

bool yhm2710_stacmd_read_bit_adapter(yhm2710_stacmd_device *device,
                                     uint8_t *bit) {
    return yhm2710_stacmd_read_bit(device, bit);
}

static uint8_t command_header(uint8_t command, uint8_t reg) {
    return (uint8_t)((command & UINT8_C(0xF0)) + reg);
}

bool yhm2710_stacmd_read_frame(yhm2710_stacmd_device *device,
                               uint8_t command, uint8_t reg,
                               uint8_t *bytes, size_t length) {
    if (!yhm2710_stacmd_operational(device) ||
            (length != 0u && bytes == NULL) ||
            (command & UINT8_C(0x40)) == 0u) {
        yhm2710_stacmd_idle(device);
        return false;
    }
    yhm2710_stacmd_idle(device);
    const uint8_t header = command_header(command, reg);
    yhm2710_stacmd_write_bits(device, header, true);
    yhm2710_stacmd_drive_bit(device, UINT8_C(1));
    uint8_t received_parity = 0u;
    if (!yhm2710_stacmd_read_bit_adapter(device, &received_parity) ||
            received_parity != yhm2710_stacmd_parity(
                (uint8_t)((header << 1) + UINT8_C(1)))) {
        yhm2710_stacmd_idle(device);
        return false;
    }
    for (size_t index = 0u; index < length; ++index) {
        uint8_t value = 0u;
        for (int32_t bit = 7; bit >= 0; --bit) {
            uint8_t received = 0u;
            if (!yhm2710_stacmd_read_bit(device, &received)) {
                bytes[index] = value;
                yhm2710_stacmd_idle(device);
                return false;
            }
            value = (uint8_t)(value + (uint8_t)(received << (uint32_t)bit));
        }
        bytes[index] = value;
        if (index + 1u != length) {
            yhm2710_stacmd_drive_bit(device, yhm2710_stacmd_parity(value));
        }
    }
    yhm2710_stacmd_idle(device);
    device->line.release_high(device->line.pin);
    return true;
}

bool yhm2710_stacmd_write_frame(yhm2710_stacmd_device *device,
                                uint8_t command, uint8_t reg,
                                const uint8_t *bytes, size_t length) {
    if (!yhm2710_stacmd_operational(device) ||
            (length != 0u && bytes == NULL) ||
            (command & UINT8_C(0x40)) == 0u) {
        yhm2710_stacmd_idle(device);
        return false;
    }
    const uint8_t header = command_header(command, reg);
    yhm2710_stacmd_idle(device);
    yhm2710_stacmd_write_bits(device, header, true);
    yhm2710_stacmd_drive_bit(device, UINT8_C(0));
    uint8_t received_parity = 0u;
    if (!yhm2710_stacmd_read_bit_adapter(device, &received_parity) ||
            received_parity != yhm2710_stacmd_parity(
                (uint8_t)(header << 1))) {
        yhm2710_stacmd_idle(device);
        return false;
    }
    for (size_t index = 0u; index < length; ++index) {
        yhm2710_stacmd_write_bits(device, bytes[index], false);
        if (!yhm2710_stacmd_read_bit_adapter(device, &received_parity) ||
                received_parity != yhm2710_stacmd_parity(bytes[index])) {
            yhm2710_stacmd_idle(device);
            return false;
        }
    }
    yhm2710_stacmd_idle(device);
    device->line.release_high(device->line.pin);
    return true;
}

bool yhm2710_stacmd_write_retry(yhm2710_stacmd_device *device,
                                uint8_t reg, const uint8_t *bytes,
                                size_t length) {
    if (!yhm2710_stacmd_operational(device)) {
        return false;
    }
    for (size_t attempt = 0u; attempt < YHM2710_STACMD_RETRY_ATTEMPTS;
            ++attempt) {
        yhm2710_stacmd_bus_recovery(device);
        if (yhm2710_stacmd_write_frame(device, UINT8_C(0x44), reg,
                                       bytes, length)) {
            return true;
        }
        ++device->failed_transactions;
    }
    return false;
}

uint32_t yhm2710_stacmd_open(yhm2710_stacmd_device *device) {
    if (device != NULL) {
        device->opened = true;
    }
    return YHM2710_STATUS_OK;
}

uint32_t yhm2710_stacmd_close(yhm2710_stacmd_device *device) {
    if (device != NULL) {
        device->opened = false;
    }
    return YHM2710_STATUS_OK;
}

uint32_t yhm2710_stacmd_read(yhm2710_stacmd_device *device,
                             const yhm2710_stacmd_read_request *request) {
    if (request == NULL) {
        return YHM2710_STATUS_NULL_REQUEST;
    }
    if (device == NULL || !device->opened) {
        return YHM2710_STATUS_READ_NOT_OPEN;
    }
    for (size_t attempt = 0u; attempt < YHM2710_STACMD_RETRY_ATTEMPTS;
            ++attempt) {
        yhm2710_stacmd_bus_recovery(device);
        if (yhm2710_stacmd_read_frame(device, UINT8_C(0x44),
                                      request->command, request->buffer,
                                      request->length)) {
            return YHM2710_STATUS_OK;
        }
        ++device->failed_transactions;
    }
    if (request->buffer != NULL) {
        for (size_t index = 0u; index < request->length; ++index) {
            request->buffer[index] = UINT8_C(0xFF);
        }
    }
    return YHM2710_STATUS_READ_FAILED;
}

uint32_t yhm2710_stacmd_write(yhm2710_stacmd_device *device,
                              const yhm2710_stacmd_write_request *request) {
    if (request == NULL) {
        return YHM2710_STATUS_NULL_REQUEST;
    }
    if (device == NULL || !device->opened) {
        return YHM2710_STATUS_WRITE_NOT_OPEN;
    }
    return yhm2710_stacmd_write_retry(device, request->command,
                                      request->buffer, request->length)
        ? YHM2710_STATUS_OK : YHM2710_STATUS_WRITE_FAILED;
}

static void zero_bytes(void *pointer, size_t length) {
    uint8_t *bytes = pointer;
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

static void acquire(yhm2710_device *device) {
    if (device != NULL && device->bindings.acquire != NULL) {
        device->bindings.acquire(device->bindings.lock_context);
    }
}

static void release(yhm2710_device *device) {
    if (device != NULL && device->bindings.release != NULL) {
        device->bindings.release(device->bindings.lock_context);
    }
}

static bool stacmd_register_read(void *context, uint8_t reg,
                                 uint8_t *bytes, size_t length) {
    yhm2710_stacmd_device *transport = context;
    if (length > UINT8_MAX) {
        return false;
    }
    yhm2710_stacmd_read_request request = {0};
    request.command = reg;
    request.buffer = bytes;
    request.length = (uint8_t)length;
    return yhm2710_stacmd_read(transport, &request) == YHM2710_STATUS_OK;
}

static bool stacmd_register_write(void *context, uint8_t reg,
                                  const uint8_t *bytes, size_t length) {
    yhm2710_stacmd_device *transport = context;
    if (length > UINT8_MAX) {
        return false;
    }
    yhm2710_stacmd_write_request request = {0};
    request.command = reg;
    request.buffer = bytes;
    request.length = (uint8_t)length;
    return yhm2710_stacmd_write(transport, &request) == YHM2710_STATUS_OK;
}

void yhm2710_initialize(yhm2710_device *device,
                        const yhm2710_bindings *bindings) {
    if (device == NULL) {
        return;
    }
    zero_bytes(device, sizeof(*device));
    if (bindings != NULL) {
        device->bindings = *bindings;
    }
}

void yhm2710_initialize_with_stacmd(yhm2710_device *device,
                                    yhm2710_stacmd_device *transport,
                                    const yhm2710_bindings *extra_bindings) {
    yhm2710_initialize(device, extra_bindings);
    if (device == NULL) {
        return;
    }
    device->transport = transport;
    device->bindings.read = stacmd_register_read;
    device->bindings.write = stacmd_register_write;
    device->bindings.io_context = transport;
}

bool yhm2710_register_read(yhm2710_device *device, uint8_t reg,
                           uint8_t *bytes, size_t length) {
    if (device == NULL || bytes == NULL || length == 0u ||
            device->bindings.read == NULL) {
        return false;
    }
    acquire(device);
    const bool ok = device->bindings.read(device->bindings.io_context, reg,
                                           bytes, length);
    release(device);
    return ok;
}

bool yhm2710_register_write(yhm2710_device *device, uint8_t reg,
                            const uint8_t *bytes, size_t length) {
    if (device == NULL || bytes == NULL || length == 0u ||
            device->bindings.write == NULL) {
        return false;
    }
    acquire(device);
    const bool ok = device->bindings.write(device->bindings.io_context, reg,
                                            bytes, length);
    release(device);
    if (device->bindings.completion != NULL) {
        device->bindings.completion(device->bindings.completion_context,
                                    ok ? 0u : 1u);
    }
    return ok;
}

bool yhm2710_register_read_byte(yhm2710_device *device, uint8_t reg,
                                uint8_t *value) {
    return yhm2710_register_read(device, reg, value, 1u);
}

bool yhm2710_register_write_byte(yhm2710_device *device, uint8_t reg,
                                 uint8_t value) {
    return yhm2710_register_write(device, reg, &value, 1u);
}

bool yhm2710_read_register_9(yhm2710_device *device, uint8_t *value) {
    return yhm2710_register_read_byte(device, UINT8_C(9), value);
}

bool yhm2710_ready(yhm2710_device *device) {
    if (device == NULL || device->transport == NULL ||
            !yhm2710_stacmd_operational(device->transport)) {
        return false;
    }
    yhm2710_stacmd_device *transport = device->transport;
    transport->line.set_input(transport->line.pin,
                              transport->line.input_pull);
    return transport->line.read_pin(transport->line.pin) != 0u;
}

uint8_t yhm2710_chip_id(yhm2710_device *device) {
    uint8_t identifier = 0u;
    (void)yhm2710_register_read_byte(device, UINT8_C(8), &identifier);
    return identifier;
}

uint32_t yhm2710_configure(yhm2710_device *device) {
    if (yhm2710_chip_id(device) != YHM2710_DEVICE_ID) {
        return 5u;
    }
    static const uint8_t registers[] = {2u, 0u, 1u, 2u, 3u};
    static const uint8_t values[] = {0x01u, 0x6Au, 0x4Cu, 0xA0u, 0x02u};
    bool ok = true;
    for (size_t index = 0u; index < sizeof(registers); ++index) {
        ok = yhm2710_register_write_byte(device, registers[index],
                                          values[index]) && ok;
    }
    if (device != NULL && device->bindings.delay_cycles != NULL) {
        for (uint32_t count = 0u; count < 50u; ++count) {
            device->bindings.delay_cycles(UINT32_C(64000));
        }
    }
    return ok ? 0u : 5u;
}

uint8_t yhm2710_status(yhm2710_device *device) {
    uint8_t value = UINT8_C(0xC0);
    if (yhm2710_ready(device) &&
            yhm2710_register_read_byte(device, UINT8_C(6), &value)) {
        const uint8_t status = (uint8_t)((value >> 4) & UINT8_C(0x0F));
        if (status <= UINT8_C(0x0D) || status == UINT8_C(0x0F)) {
            return status;
        }
        return UINT8_C(0x11);
    }
    return UINT8_C(0x0C);
}

uint8_t yhm2710_charge_state(yhm2710_device *device) {
    const uint8_t status = yhm2710_status(device);
    if (status >= UINT8_C(0x0A) && status <= UINT8_C(0x0C)) {
        return 1u;
    }
    return status == UINT8_C(0x0D) ? 2u : 0u;
}

static float absolute_float(float value) {
    return value < 0.0f ? -value : value;
}

uint8_t yhm2710_set_ladder(yhm2710_device *device, float target) {
    static const float scale = 20.080322265625f;
    static const float multipliers[8] = {
        0.5f, 0.2f, 0.7f, 0.9f, 1.0f, 1.5f, 2.0f, 3.0f,
    };
    uint8_t selected = 0u;
    float distance = absolute_float(target - scale * multipliers[0]);
    for (uint8_t index = 1u; index < 8u; ++index) {
        const float candidate = absolute_float(
            target - scale * multipliers[index]);
        if (candidate < distance) {
            selected = index;
            distance = candidate;
        }
    }
    uint8_t value = 0u;
    if (yhm2710_register_read_byte(device, UINT8_C(1), &value)) {
        value = (uint8_t)((value & UINT8_C(0x1F)) |
                          (uint8_t)(selected << 5));
        (void)yhm2710_register_write_byte(device, UINT8_C(1), value);
    }
    return selected;
}

bool yhm2710_set_shared_power_active(yhm2710_device *device) {
    return yhm2710_register_write_byte(device, UINT8_C(2), UINT8_C(0xA8));
}

bool yhm2710_set_shared_power_inactive(yhm2710_device *device) {
    return yhm2710_register_write_byte(device, UINT8_C(2), UINT8_C(0x28));
}

bool yhm2710_set_shared_power_enabled(yhm2710_device *device,
                                      bool enabled) {
    return enabled ? yhm2710_set_shared_power_active(device)
                   : yhm2710_set_shared_power_inactive(device);
}

bool yhm2710_set_high_temperature(yhm2710_device *device) {
    return yhm2710_register_write_byte(device, UINT8_C(2), UINT8_C(0xF8));
}

bool yhm2710_set_system_track(yhm2710_device *device) {
    uint8_t value = 0u;
    if (!yhm2710_register_read_byte(device, UINT8_C(1), &value)) {
        return false;
    }
    value = (uint8_t)(value | UINT8_C(2));
    return yhm2710_register_write_byte(device, UINT8_C(1), value);
}

bool yhm2710_clear_system_track(yhm2710_device *device) {
    uint8_t value = 0u;
    if (!yhm2710_register_read_byte(device, UINT8_C(1), &value)) {
        return false;
    }
    value = (uint8_t)(value & (uint8_t)~UINT8_C(2));
    return yhm2710_register_write_byte(device, UINT8_C(1), value);
}

bool yhm2710_set_charging_event(yhm2710_device *device) {
    uint8_t value = 0u;
    if (!yhm2710_register_read_byte(device, UINT8_C(3), &value)) {
        return false;
    }
    value = (uint8_t)(value | UINT8_C(0x08));
    return yhm2710_register_write_byte(device, UINT8_C(3), value);
}

void yhm2710_delay_209(void) {
    volatile uint32_t count = 0u;
    while (count < UINT32_C(209)) {
        ++count;
    }
}

void yhm2710_dispatch_completion(yhm2710_device *device, uint32_t value) {
    if (device != NULL && device->bindings.completion != NULL) {
        device->bindings.completion(device->bindings.completion_context, value);
    }
}
