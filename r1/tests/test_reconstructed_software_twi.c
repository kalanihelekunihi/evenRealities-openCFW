/*
 * Host tests for the reconstructed software-TWI engine (family
 * unknown_software_twi_provider_candidate).  Exposes
 * test_reconstructed_software_twi(); the integrator wave wires it into the
 * shared runner.  Expected values are derived from the recovered semantics
 * documented in docs/correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md.
 *
 * The mock GPIO layer records every engine operation and scripts SDA levels
 * for read_pin; a wire decoder reconstructs master-driven data bits so
 * transaction tests can assert the exact bytes on the wire.
 */

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#include "software_twi/software_twi.h"

/* i2c_2 recovered pins (P1.13 / P0.28) and delay argument. */
#define I2C_2_SCL UINT32_C(45)
#define I2C_2_SDA UINT32_C(28)
#define I2C_2_DELAY UINT32_C(1)
/* i2c_3 recovered pins (P0.11 / P0.12) and delay argument. */
#define I2C_3_SCL UINT32_C(11)
#define I2C_3_SDA UINT32_C(12)
#define I2C_3_DELAY UINT32_C(5)
/* i2c_4 recovered pins (P1.09 / P0.31). */
#define I2C_4_SCL UINT32_C(41)
#define I2C_4_SDA UINT32_C(31)
/* i2c_5 recovered pins (P1.14 / P1.11). */
#define I2C_5_SCL UINT32_C(46)
#define I2C_5_SDA UINT32_C(43)

#define MOCK_PULL UINT32_C(3)

typedef enum {
    EV_DRIVE_LOW,
    EV_RELEASE_HIGH,
    EV_SET_OUTPUT,
    EV_SET_INPUT,
    EV_UDELAY,
    EV_READ_PIN
} event_kind;

typedef struct {
    event_kind kind;
    uint32_t pin;
    uint32_t arg;
} mock_event;

static mock_event events[16384];
static size_t event_count;
static uint8_t sda_script[8192];
static size_t sda_script_count;
static size_t sda_script_index;
static uint32_t configure_log[4][6];
static size_t configure_count;

static void mock_reset(void) {
    event_count = 0u;
    sda_script_count = 0u;
    sda_script_index = 0u;
    configure_count = 0u;
}

static void record_event(event_kind kind, uint32_t pin, uint32_t arg) {
    assert(event_count < sizeof(events) / sizeof(events[0]));
    events[event_count].kind = kind;
    events[event_count].pin = pin;
    events[event_count].arg = arg;
    ++event_count;
}

static void mock_drive_low(uint32_t pin) {
    record_event(EV_DRIVE_LOW, pin, 0u);
}

static void mock_release_high(uint32_t pin) {
    record_event(EV_RELEASE_HIGH, pin, 0u);
}

static void mock_set_output(uint32_t pin) {
    record_event(EV_SET_OUTPUT, pin, 0u);
}

static void mock_set_input(uint32_t pin, uint32_t pull) {
    record_event(EV_SET_INPUT, pin, pull);
}

static void mock_udelay(uint32_t context) {
    record_event(EV_UDELAY, 0u, context);
}

static uint32_t mock_read_pin(uint32_t pin) {
    record_event(EV_READ_PIN, pin, 0u);
    if (sda_script_index < sda_script_count) {
        uint32_t level = sda_script[sda_script_index];
        ++sda_script_index;
        return level;
    }
    return 0u; /* default: slave pulls SDA low (ACK) / reads as zero */
}

static void mock_configure(uint32_t pin, uint32_t direction, uint32_t input,
                           uint32_t pull, uint32_t drive, uint32_t sense) {
    assert(configure_count < sizeof(configure_log) / sizeof(configure_log[0]));
    configure_log[configure_count][0] = pin;
    configure_log[configure_count][1] = direction;
    configure_log[configure_count][2] = input;
    configure_log[configure_count][3] = pull;
    configure_log[configure_count][4] = drive;
    configure_log[configure_count][5] = sense;
    ++configure_count;
}

static const software_twi_providers full_providers = {
    mock_drive_low,  mock_release_high, mock_set_output, mock_set_input,
    mock_udelay,     mock_read_pin,     mock_configure,  (uint8_t)MOCK_PULL
};

static void script_bits(const uint8_t *bits, size_t count) {
    assert(count <= sizeof(sda_script));
    for (size_t index = 0u; index < count; ++index) {
        sda_script[index] = bits[index];
    }
    sda_script_count = count;
    sda_script_index = 0u;
}

/* Scripts the three ACK samples (address, register[, register], address|1)
 * of a read transaction, then `count` data bytes MSB-first. */
static void script_read_transfer(size_t ack_samples, const uint8_t *bytes,
                                 size_t count) {
    size_t out = 0u;
    for (size_t index = 0u; index < ack_samples; ++index) {
        sda_script[out++] = 0u;
    }
    for (size_t byte = 0u; byte < count; ++byte) {
        for (uint32_t bit = 0u; bit < 8u; ++bit) {
            sda_script[out++] =
                (uint8_t)((bytes[byte] >> (7u - bit)) & 1u);
        }
    }
    assert(out <= sizeof(sda_script));
    sda_script_count = out;
    sda_script_index = 0u;
}

static void expect_events(const mock_event *expected, size_t count) {
    assert(event_count == count);
    for (size_t index = 0u; index < count; ++index) {
        assert(events[index].kind == expected[index].kind);
        assert(events[index].pin == expected[index].pin);
        assert(events[index].arg == expected[index].arg);
    }
}

static size_t count_kind(event_kind kind) {
    size_t count = 0u;
    for (size_t index = 0u; index < event_count; ++index) {
        if (events[index].kind == kind) {
            ++count;
        }
    }
    return count;
}

static size_t count_kind_pin(event_kind kind, uint32_t pin) {
    size_t count = 0u;
    for (size_t index = 0u; index < event_count; ++index) {
        if (events[index].kind == kind && events[index].pin == pin) {
            ++count;
        }
    }
    return count;
}

/* Wire decoder: a master data bit commits when an SCL release is followed by
 * an SCL drive-low while SDA is in output mode with a valid driven level.
 * The trailing SCL release inside STOP is dropped because no SCL drive-low
 * follows it. */
static uint8_t master_bits[8192];
static size_t master_bit_count;

static void decode_master_bits(uint32_t sda_pin, uint32_t scl_pin) {
    master_bit_count = 0u;
    /* After `open` both pins are outputs in stock; start from that state so
     * standalone write_byte calls decode as well. */
    bool sda_output = true;
    int32_t sda_level = -1;
    int32_t armed = -1;
    for (size_t index = 0u; index < event_count; ++index) {
        const mock_event *event = &events[index];
        if (event->kind == EV_SET_OUTPUT && event->pin == sda_pin) {
            sda_output = true;
            sda_level = -1;
        } else if (event->kind == EV_SET_INPUT && event->pin == sda_pin) {
            sda_output = false;
            sda_level = -1;
        } else if (event->kind == EV_DRIVE_LOW && event->pin == sda_pin &&
                   sda_output) {
            sda_level = 0;
        } else if (event->kind == EV_RELEASE_HIGH && event->pin == sda_pin &&
                   sda_output) {
            sda_level = 1;
        } else if (event->kind == EV_RELEASE_HIGH && event->pin == scl_pin) {
            if (sda_output && sda_level >= 0) {
                armed = sda_level;
            }
        } else if (event->kind == EV_DRIVE_LOW && event->pin == scl_pin) {
            if (armed >= 0) {
                assert(master_bit_count <
                       sizeof(master_bits) / sizeof(master_bits[0]));
                master_bits[master_bit_count] = (uint8_t)armed;
                ++master_bit_count;
                armed = -1;
            }
        }
    }
}

static uint8_t decoded_byte(size_t byte_index) {
    uint8_t value = 0u;
    for (size_t bit = 0u; bit < 8u; ++bit) {
        value = (uint8_t)(value << 1);
        value = (uint8_t)(value | master_bits[byte_index * 8u + bit]);
    }
    return value;
}

static void expect_wire_bytes(uint32_t sda_pin, uint32_t scl_pin,
                              const uint8_t *expected, size_t byte_count,
                              size_t spare_bits) {
    decode_master_bits(sda_pin, scl_pin);
    assert(master_bit_count == byte_count * 8u + spare_bits);
    for (size_t index = 0u; index < byte_count; ++index) {
        assert(decoded_byte(index) == expected[index]);
    }
}

static void test_open(void) {
    software_twi_initialize(&full_providers);
    mock_reset();

    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_OK);
    static const mock_event expected_open[] = {
        {EV_SET_OUTPUT, I2C_2_SCL, 0u},
        {EV_SET_OUTPUT, I2C_2_SDA, 0u},
        {EV_RELEASE_HIGH, I2C_2_SCL, 0u},
        {EV_RELEASE_HIGH, I2C_2_SDA, 0u},
    };
    expect_events(expected_open, sizeof(expected_open) / sizeof(expected_open[0]));

    /* Idempotent: the second open drives nothing and returns OK. */
    mock_reset();
    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_OK);
    assert(event_count == 0u);

    /* i2c_3 / i2c_5 share the byte-identical body. */
    assert(software_twi_i2c_3_open() == SOFTWARE_TWI_STATUS_OK);
    assert(software_twi_i2c_5_open() == SOFTWARE_TWI_STATUS_OK);

    /* i2c_4 adds the two recovered gpio-configure calls (pin, 1, 1, 0, 0, 0)
     * after the shared four-op sequence. */
    mock_reset();
    assert(software_twi_i2c_4_open() == SOFTWARE_TWI_STATUS_OK);
    assert(configure_count == 2u);
    assert(configure_log[0][0] == I2C_4_SCL);
    assert(configure_log[1][0] == I2C_4_SDA);
    for (size_t call = 0u; call < 2u; ++call) {
        assert(configure_log[call][1] == 1u);
        assert(configure_log[call][2] == 1u);
        assert(configure_log[call][3] == 0u);
        assert(configure_log[call][4] == 0u);
        assert(configure_log[call][5] == 0u);
    }
    static const mock_event expected_open4[] = {
        {EV_SET_OUTPUT, I2C_4_SCL, 0u},
        {EV_SET_OUTPUT, I2C_4_SDA, 0u},
        {EV_RELEASE_HIGH, I2C_4_SCL, 0u},
        {EV_RELEASE_HIGH, I2C_4_SDA, 0u},
    };
    expect_events(expected_open4,
                  sizeof(expected_open4) / sizeof(expected_open4[0]));

    /* Recovered record/binding state. */
    const software_twi_record *record =
        software_twi_bus_record(SOFTWARE_TWI_BUS_I2C_2);
    assert(record != NULL);
    assert(record->opened == 1u);
    assert(record->name[0] == 'i' && record->name[1] == '2' &&
           record->name[4] == '2');
    assert(record->engine.scl_pin == I2C_2_SCL);
    assert(record->engine.sda_pin == I2C_2_SDA);
    assert(record->engine.delay_context == I2C_2_DELAY);
    assert(software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_3)->delay_context ==
           I2C_3_DELAY);
    assert(software_twi_bus_record(SOFTWARE_TWI_BUS_COUNT) == NULL);
    assert(software_twi_bus_engine(SOFTWARE_TWI_BUS_COUNT) == NULL);
}

static void test_open_unbound(void) {
    /* No providers at all: every open fails explicitly with the recovered
     * bad-argument code instead of faulting on a NULL vtable slot. */
    software_twi_initialize(NULL);
    mock_reset();
    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(software_twi_i2c_4_open() == SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(event_count == 0u);

    /* gpio_configure missing: only i2c_4 is affected. */
    software_twi_providers no_configure = full_providers;
    no_configure.gpio_configure = NULL;
    software_twi_initialize(&no_configure);
    mock_reset();
    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_OK);
    assert(software_twi_i2c_4_open() == SOFTWARE_TWI_STATUS_BAD_ARGUMENT);

    /* A single missing GPIO op unbinds the engine. */
    software_twi_providers no_udelay = full_providers;
    no_udelay.udelay = NULL;
    software_twi_initialize(&no_udelay);
    mock_reset();
    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
}

static void test_start_stop(void) {
    software_twi_initialize(&full_providers);
    mock_reset();
    software_twi_engine *engine = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_2);

    software_twi_start(engine);
    static const mock_event expected_start[] = {
        {EV_SET_OUTPUT, I2C_2_SCL, 0u},
        {EV_SET_OUTPUT, I2C_2_SDA, 0u},
        {EV_RELEASE_HIGH, I2C_2_SCL, 0u},
        {EV_RELEASE_HIGH, I2C_2_SDA, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_DRIVE_LOW, I2C_2_SDA, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_DRIVE_LOW, I2C_2_SCL, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
    };
    expect_events(expected_start,
                  sizeof(expected_start) / sizeof(expected_start[0]));

    mock_reset();
    software_twi_stop(engine);
    static const mock_event expected_stop[] = {
        {EV_SET_OUTPUT, I2C_2_SCL, 0u},
        {EV_SET_OUTPUT, I2C_2_SDA, 0u},
        {EV_DRIVE_LOW, I2C_2_SDA, 0u},
        {EV_RELEASE_HIGH, I2C_2_SCL, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_RELEASE_HIGH, I2C_2_SDA, 0u},
    };
    expect_events(expected_stop, sizeof(expected_stop) / sizeof(expected_stop[0]));

    /* Per-bus delay context travels with the engine (i2c_3: 5). */
    mock_reset();
    software_twi_start(software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_3));
    assert(count_kind(EV_UDELAY) == 3u);
    for (size_t index = 0u; index < event_count; ++index) {
        if (events[index].kind == EV_UDELAY) {
            assert(events[index].arg == I2C_3_DELAY);
        }
    }

    /* Unbound engine: explicit no-op, no events. */
    mock_reset();
    software_twi_start(NULL);
    software_twi_stop(NULL);
    assert(event_count == 0u);
}

static void test_wait_ack(void) {
    software_twi_initialize(&full_providers);
    software_twi_engine *engine = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_2);

    /* SDA low during the sample window: ACK, returns 0. */
    mock_reset();
    static const uint8_t ack_bit[] = {0u};
    script_bits(ack_bit, sizeof(ack_bit));
    assert(software_twi_wait_ack(engine) == 0u);
    static const mock_event expected_ack[] = {
        {EV_RELEASE_HIGH, I2C_2_SDA, 0u},
        {EV_SET_INPUT, I2C_2_SDA, MOCK_PULL},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_RELEASE_HIGH, I2C_2_SCL, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_READ_PIN, I2C_2_SDA, 0u},
        {EV_DRIVE_LOW, I2C_2_SCL, 0u},
        {EV_SET_OUTPUT, I2C_2_SDA, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
    };
    expect_events(expected_ack, sizeof(expected_ack) / sizeof(expected_ack[0]));

    /* SDA high: NACK, returns 1 (recovered error polarity). */
    mock_reset();
    static const uint8_t nack_bit[] = {1u};
    script_bits(nack_bit, sizeof(nack_bit));
    assert(software_twi_wait_ack(engine) == 1u);

    /* Unbound engine reports the error polarity. */
    assert(software_twi_wait_ack(NULL) == 1u);
}

static void test_write_byte(void) {
    software_twi_initialize(&full_providers);
    software_twi_engine *engine = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_2);

    /* 0xA5 = 1010 0101: MSB-first release/drive pattern on SDA. */
    mock_reset();
    software_twi_write_byte(0xA5u, engine);
    static const uint8_t expected_a5[] = {0xA5u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_a5, 1u, 0u);
    /* Per bit: data set, udelay, SCL release, udelay, SCL drive, udelay. */
    assert(count_kind(EV_UDELAY) == 24u);
    assert(count_kind_pin(EV_RELEASE_HIGH, I2C_2_SCL) == 8u);
    assert(count_kind_pin(EV_DRIVE_LOW, I2C_2_SCL) == 8u);
    /* Four set bits plus the recovered in-loop SDA release after bit 7. */
    assert(count_kind_pin(EV_RELEASE_HIGH, I2C_2_SDA) == 5u);
    assert(count_kind_pin(EV_DRIVE_LOW, I2C_2_SDA) == 4u);

    mock_reset();
    software_twi_write_byte(0x00u, engine);
    static const uint8_t expected_00[] = {0u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_00, 1u, 0u);
    assert(count_kind_pin(EV_DRIVE_LOW, I2C_2_SDA) == 8u);
    assert(count_kind_pin(EV_RELEASE_HIGH, I2C_2_SDA) == 1u); /* bit 7 only */

    mock_reset();
    software_twi_write_byte(0xFFu, engine);
    static const uint8_t expected_ff[] = {0xFFu};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_ff, 1u, 0u);
    assert(count_kind_pin(EV_DRIVE_LOW, I2C_2_SDA) == 0u);
    assert(count_kind_pin(EV_RELEASE_HIGH, I2C_2_SDA) == 9u);

    mock_reset();
    software_twi_write_byte(0x55u, NULL);
    assert(event_count == 0u);
}

static void test_read_byte(void) {
    software_twi_initialize(&full_providers);
    software_twi_engine *engine = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_2);

    /* 0x3C = 0011 1100, ACK trailing pulse (drive SDA low). */
    mock_reset();
    static const uint8_t bits_3c[] = {0u, 0u, 1u, 1u, 1u, 1u, 0u, 0u};
    script_bits(bits_3c, sizeof(bits_3c));
    assert(software_twi_read_byte(1u, engine) == 0x3Cu);
    /* Initial set_input + udelay, then per bit: SCL release, udelay, sample,
     * SCL drive, udelay. */
    assert(count_kind(EV_READ_PIN) == 8u);
    assert(count_kind(EV_UDELAY) == 21u);
    assert(count_kind_pin(EV_SET_INPUT, I2C_2_SDA) == 1u);
    /* The master drives one ACK bit (0) after the byte. */
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, NULL, 0u, 1u);
    assert(master_bits[0] == 0u);

    /* NACK trailing pulse leaves SDA released (one released bit). */
    mock_reset();
    script_bits(bits_3c, sizeof(bits_3c));
    assert(software_twi_read_byte(0u, engine) == 0x3Cu);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, NULL, 0u, 1u);
    assert(master_bits[0] == 1u);

    /* Exact ACK tail: set_output(SDA), udelay, drive SDA low, udelay,
     * release SCL, udelay, drive SCL low, udelay, release SDA. */
    mock_reset();
    script_bits(bits_3c, sizeof(bits_3c));
    (void)software_twi_read_byte(1u, engine);
    assert(event_count == 51u);
    static const mock_event expected_tail[] = {
        {EV_SET_OUTPUT, I2C_2_SDA, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_DRIVE_LOW, I2C_2_SDA, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_RELEASE_HIGH, I2C_2_SCL, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_DRIVE_LOW, I2C_2_SCL, 0u},
        {EV_UDELAY, 0u, I2C_2_DELAY},
        {EV_RELEASE_HIGH, I2C_2_SDA, 0u},
    };
    const size_t tail = sizeof(expected_tail) / sizeof(expected_tail[0]);
    for (size_t index = 0u; index < tail; ++index) {
        const mock_event *actual = &events[event_count - tail + index];
        assert(actual->kind == expected_tail[index].kind);
        assert(actual->pin == expected_tail[index].pin);
        assert(actual->arg == expected_tail[index].arg);
    }

    mock_reset();
    assert(software_twi_read_byte(1u, NULL) == 0u);
    assert(event_count == 0u);
}

static void test_read_transaction(void) {
    software_twi_initialize(&full_providers);
    software_twi_engine *engine = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_2);
    uint8_t buffer[8];

    /* Happy path: start / 0x50(W) / 0x10 / repeated-start / 0x51 / two
     * ACKed bytes + one NACKed byte / stop. */
    mock_reset();
    static const uint8_t payload[] = {0x11u, 0x22u, 0x80u};
    script_read_transfer(3u, payload, sizeof(payload));
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, buffer, 3u,
                                              engine) ==
           SOFTWARE_TWI_STATUS_OK);
    assert(buffer[0] == 0x11u && buffer[1] == 0x22u && buffer[2] == 0x80u);
    static const uint8_t expected_phase[] = {0x50u, 0x10u, 0x51u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_phase,
                      sizeof(expected_phase), 3u);
    /* ACK, ACK, NACK trailing drives for the three read bytes. */
    assert(master_bits[24] == 0u);
    assert(master_bits[25] == 0u);
    assert(master_bits[26] == 1u);

    /* NACK on the address byte aborts with 11 and issues no STOP and no
     * further write bits. */
    mock_reset();
    static const uint8_t nack_first[] = {1u};
    script_bits(nack_first, sizeof(nack_first));
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, buffer, 3u,
                                              engine) ==
           SOFTWARE_TWI_STATUS_WRITE_NACK);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_phase, 1u, 0u);
    assert(count_kind(EV_READ_PIN) == 1u);

    /* NACK on the register byte aborts after two written bytes. */
    mock_reset();
    static const uint8_t nack_second[] = {0u, 1u};
    script_bits(nack_second, sizeof(nack_second));
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, buffer, 3u,
                                              engine) ==
           SOFTWARE_TWI_STATUS_WRITE_NACK);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_phase, 2u, 0u);

    /* Recovered count-0 quirk: the ACK loop wraps and exactly one byte is
     * still read (with NACK). */
    mock_reset();
    static const uint8_t one[] = {0x7Eu};
    script_read_transfer(3u, one, sizeof(one));
    buffer[0] = 0u;
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, buffer, 0u,
                                              engine) ==
           SOFTWARE_TWI_STATUS_OK);
    assert(buffer[0] == 0x7Eu);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_phase,
                      sizeof(expected_phase), 1u);
    assert(master_bits[24] == 1u); /* single byte always NACKed */

    /* Count 1: no ACKed bytes, one NACKed byte. */
    mock_reset();
    script_read_transfer(3u, one, sizeof(one));
    buffer[0] = 0u;
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, buffer, 1u,
                                              engine) ==
           SOFTWARE_TWI_STATUS_OK);
    assert(buffer[0] == 0x7Eu);

    /* 16-bit register form (i2c_5 engine): register goes MSB-first. */
    mock_reset();
    static const uint8_t payload16[] = {0x01u, 0x02u};
    script_read_transfer(4u, payload16, sizeof(payload16));
    software_twi_engine *engine5 = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_5);
    assert(software_twi_read_transaction_reg16(0x28u, 0x1234u, buffer, 2u,
                                               engine5) ==
           SOFTWARE_TWI_STATUS_OK);
    assert(buffer[0] == 0x01u && buffer[1] == 0x02u);
    static const uint8_t expected_phase16[] = {0x28u, 0x12u, 0x34u, 0x29u};
    expect_wire_bytes(I2C_5_SDA, I2C_5_SCL, expected_phase16,
                      sizeof(expected_phase16), 2u);
    assert(master_bits[32] == 0u);
    assert(master_bits[33] == 1u);

    /* Bad arguments return the family's recovered bad-argument code. */
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, NULL, 3u,
                                              engine) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(software_twi_read_transaction_reg8(0x50u, 0x10u, buffer, 3u,
                                              NULL) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
}

static void test_write_transactions(void) {
    software_twi_initialize(&full_providers);
    software_twi_engine *engine = software_twi_bus_engine(SOFTWARE_TWI_BUS_I2C_2);

    /* 0x000560DC form: address + 16-bit register MSB-first + one byte. */
    mock_reset();
    assert(software_twi_write_transaction_reg16_byte(0x28u, 0x00FFu, 0x5Au,
                                                     engine) ==
           SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_single[] = {0x28u, 0x00u, 0xFFu, 0x5Au};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_single,
                      sizeof(expected_single), 0u);

    /* NACK on the register low byte aborts with 11 before the data byte. */
    mock_reset();
    static const uint8_t nack_third[] = {0u, 0u, 1u};
    script_bits(nack_third, sizeof(nack_third));
    assert(software_twi_write_transaction_reg16_byte(0x28u, 0x00FFu, 0x5Au,
                                                     engine) ==
           SOFTWARE_TWI_STATUS_WRITE_NACK);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_single, 3u, 0u);

    /* 0x0005613E form: address + 8-bit register + N data bytes. */
    mock_reset();
    static const uint8_t data3[] = {0x01u, 0x02u, 0x03u};
    assert(software_twi_write_transaction_reg8(0x50u, 0x10u, data3, 3u,
                                               engine) ==
           SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_multi[] = {0x50u, 0x10u, 0x01u, 0x02u, 0x03u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_multi,
                      sizeof(expected_multi), 0u);

    /* Zero count: address + register + stop, no data bytes. */
    mock_reset();
    assert(software_twi_write_transaction_reg8(0x50u, 0x10u, data3, 0u,
                                               engine) ==
           SOFTWARE_TWI_STATUS_OK);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_multi, 2u, 0u);

    /* 0x00056202 form: address + 16-bit register + N data bytes. */
    mock_reset();
    static const uint8_t data2[] = {0xAAu, 0xBBu};
    assert(software_twi_write_transaction_reg16(0x28u, 0x1234u, data2, 2u,
                                                engine) ==
           SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_multi16[] = {0x28u, 0x12u, 0x34u, 0xAAu, 0xBBu};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_multi16,
                      sizeof(expected_multi16), 0u);

    /* NACK mid-data aborts without STOP; the NACKed byte itself is already
     * on the wire (the ACK is sampled after the byte is driven). */
    mock_reset();
    static const uint8_t nack_data[] = {0u, 0u, 0u, 0u, 1u};
    script_bits(nack_data, sizeof(nack_data));
    assert(software_twi_write_transaction_reg16(0x28u, 0x1234u, data2, 2u,
                                                engine) ==
           SOFTWARE_TWI_STATUS_WRITE_NACK);
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_multi16, 5u, 0u);

    /* Bad arguments. */
    assert(software_twi_write_transaction_reg8(0x50u, 0x10u, NULL, 2u,
                                               engine) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(software_twi_write_transaction_reg8(0x50u, 0x10u, NULL, 0u,
                                               engine) ==
           SOFTWARE_TWI_STATUS_OK); /* count 0 never dereferences (stock) */
    assert(software_twi_write_transaction_reg16_byte(0x28u, 0u, 0u, NULL) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
}

static void test_read_adapters(void) {
    software_twi_initialize(&full_providers);
    mock_reset();
    uint8_t buffer[4];
    software_twi_read_request request = {
        0x50u, 0u, 0x10u, {0u, 0u}, buffer, 2u, 0u
    };

    /* Not open: 10 for i2c_2..4; i2c_5 merges the failure into 4. */
    assert(software_twi_i2c_2_read(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_READ_NOT_OPEN);
    assert(software_twi_i2c_4_read(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_READ_NOT_OPEN);
    assert(software_twi_i2c_5_read(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    /* NULL request: 4 everywhere (i2c_5 merged code coincides). */
    assert(software_twi_i2c_2_read(0u, 0u, NULL) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(software_twi_i2c_5_read(0u, 0u, NULL) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(event_count == 0u);

    /* Happy path through the i2c_2 adapter; the device/operation dispatch
     * arguments are ignored. */
    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    static const uint8_t payload[] = {0x9Au, 0x55u};
    script_read_transfer(3u, payload, sizeof(payload));
    assert(software_twi_i2c_2_read(0xDEADBEEFu, 0x14u, &request) ==
           SOFTWARE_TWI_STATUS_OK);
    assert(buffer[0] == 0x9Au && buffer[1] == 0x55u);
    static const uint8_t expected_phase[] = {0x50u, 0x10u, 0x51u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_phase,
                      sizeof(expected_phase), 2u);

    /* The u8 buses truncate the register address to its low byte. */
    mock_reset();
    script_read_transfer(3u, payload, sizeof(payload));
    request.register_address = 0x1ABu;
    assert(software_twi_i2c_2_read(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_trunc[] = {0x50u, 0xABu, 0x51u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_trunc,
                      sizeof(expected_trunc), 2u);

    /* Transaction failure maps to 12. */
    mock_reset();
    static const uint8_t nack_first[] = {1u};
    script_bits(nack_first, sizeof(nack_first));
    request.register_address = 0x10u;
    assert(software_twi_i2c_2_read(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_READ_NACK);

    /* NULL buffer is rejected instead of faulted (documented divergence). */
    request.buffer = NULL;
    assert(software_twi_i2c_2_read(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    request.buffer = buffer;

    /* i2c_4 adapter: full 16-bit register, MSB-first. */
    assert(software_twi_i2c_4_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    script_read_transfer(4u, payload, sizeof(payload));
    request.register_address = 0xBEEFu;
    assert(software_twi_i2c_4_read(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_phase4[] = {0x50u, 0xBEu, 0xEFu, 0x51u};
    expect_wire_bytes(I2C_4_SDA, I2C_4_SCL, expected_phase4,
                      sizeof(expected_phase4), 2u);

    /* i2c_5 adapter: 16-bit register, 8-bit count truncation (0x102 -> 2). */
    assert(software_twi_i2c_5_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    script_read_transfer(4u, payload, sizeof(payload));
    request.register_address = 0x0102u;
    request.length = 0x102u;
    assert(software_twi_i2c_5_read(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_phase5[] = {0x50u, 0x01u, 0x02u, 0x51u};
    expect_wire_bytes(I2C_5_SDA, I2C_5_SCL, expected_phase5,
                      sizeof(expected_phase5), 2u);
    assert(buffer[0] == 0x9Au && buffer[1] == 0x55u);
}

static void test_write_adapters(void) {
    software_twi_initialize(&full_providers);
    mock_reset();
    static const uint8_t data3[] = {0x01u, 0x02u, 0x03u};
    software_twi_write_request request = {
        0x50u, 0u, 0x10u, data3, 3u, 0u
    };

    /* Not open: 8; NULL request: 4. */
    assert(software_twi_i2c_2_write(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN);
    assert(software_twi_i2c_2_write(0u, 0u, NULL) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
    assert(event_count == 0u);

    /* i2c_2 single-byte path: address + 8-bit register + one data byte. */
    assert(software_twi_i2c_2_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    request.length = 1u;
    assert(software_twi_i2c_2_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_single[] = {0x50u, 0x10u, 0x01u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_single,
                      sizeof(expected_single), 0u);

    /* Multi-byte path. */
    mock_reset();
    request.length = 3u;
    assert(software_twi_i2c_2_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_multi[] = {0x50u, 0x10u, 0x01u, 0x02u, 0x03u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_multi,
                      sizeof(expected_multi), 0u);

    /* Length 0x101 takes the multi-byte path with the count truncated to
     * 8 bits (one data byte). */
    mock_reset();
    request.length = 0x101u;
    assert(software_twi_i2c_2_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_trunc[] = {0x50u, 0x10u, 0x01u};
    expect_wire_bytes(I2C_2_SDA, I2C_2_SCL, expected_trunc,
                      sizeof(expected_trunc), 0u);

    /* Transaction failure maps to 11. */
    mock_reset();
    static const uint8_t nack_first[] = {1u};
    script_bits(nack_first, sizeof(nack_first));
    request.length = 3u;
    assert(software_twi_i2c_2_write(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_WRITE_NACK);

    /* i2c_3 shares the byte-identical adapter shape. */
    mock_reset();
    assert(software_twi_i2c_3_write(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN);
    assert(software_twi_i2c_3_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    assert(software_twi_i2c_3_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    expect_wire_bytes(I2C_3_SDA, I2C_3_SCL, expected_multi,
                      sizeof(expected_multi), 0u);

    /* i2c_4: no register byte in either path (address + data only). */
    assert(software_twi_i2c_4_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    request.length = 1u;
    assert(software_twi_i2c_4_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_4_single[] = {0x50u, 0x01u};
    expect_wire_bytes(I2C_4_SDA, I2C_4_SCL, expected_4_single,
                      sizeof(expected_4_single), 0u);

    mock_reset();
    request.length = 3u;
    assert(software_twi_i2c_4_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_4_multi[] = {0x50u, 0x01u, 0x02u, 0x03u};
    expect_wire_bytes(I2C_4_SDA, I2C_4_SCL, expected_4_multi,
                      sizeof(expected_4_multi), 0u);

    /* i2c_5 single byte: address + 16-bit register MSB-first + one byte. */
    assert(software_twi_i2c_5_open() == SOFTWARE_TWI_STATUS_OK);
    mock_reset();
    request.length = 1u;
    request.register_address = 0x1234u;
    assert(software_twi_i2c_5_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_5_single[] = {0x50u, 0x12u, 0x34u, 0x01u};
    expect_wire_bytes(I2C_5_SDA, I2C_5_SCL, expected_5_single,
                      sizeof(expected_5_single), 0u);

    /* i2c_5 multi-byte. */
    mock_reset();
    request.length = 3u;
    assert(software_twi_i2c_5_write(0u, 0u, &request) == SOFTWARE_TWI_STATUS_OK);
    static const uint8_t expected_5_multi[] =
        {0x50u, 0x12u, 0x34u, 0x01u, 0x02u, 0x03u};
    expect_wire_bytes(I2C_5_SDA, I2C_5_SCL, expected_5_multi,
                      sizeof(expected_5_multi), 0u);

    /* i2c_5 errors: not open 8, NULL request 4. */
    software_twi_initialize(&full_providers);
    mock_reset();
    assert(software_twi_i2c_5_write(0u, 0u, &request) ==
           SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN);
    assert(software_twi_i2c_5_write(0u, 0u, NULL) ==
           SOFTWARE_TWI_STATUS_BAD_ARGUMENT);
}

void test_reconstructed_software_twi(void) {
    test_open();
    test_open_unbound();
    test_start_stop();
    test_wait_ack();
    test_write_byte();
    test_read_byte();
    test_read_transaction();
    test_write_transactions();
    test_read_adapters();
    test_write_adapters();
}
