/*
 * Provenance banner
 * -----------------
 * Family:         unknown_software_twi_provider_candidate (Bravechip B210
 *                 "ChipletRing" platform GPIO-driven two-wire engine,
 *                 compiler-instantiated for buses `i2c_2`..`i2c_5`).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       fresh Thumb-2 disassembly (arm-none-eabi-objdump) of all
 *                 forty bodies from the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin;
 *                 the region is absent from the Ghidra corpus.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  Reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Per-function mapping (stock extent, end-exclusive / size -> symbol here):
 *
 *   0x00055330..<0x0005535C   44 -> software_twi_i2c_2_open
 *   0x00055360..<0x0005538C   44 -> software_twi_i2c_3_open
 *   0x00055390..<0x000553DE   78 -> software_twi_i2c_4_open
 *   0x000553E4..<0x00055410   44 -> software_twi_i2c_5_open
 *   0x0005547C..<0x000554AA   46 -> software_twi_i2c_2_read
 *   0x000554B0..<0x000554DE   46 -> software_twi_i2c_3_read
 *   0x000554E4..<0x00055512   46 -> software_twi_i2c_4_read
 *   0x00055518..<0x00055542   42 -> software_twi_i2c_5_read
 *   0x00055548..<0x000555F4  172 -> software_twi_read_byte (i2c_2 copy)
 *   0x000555F4..<0x000556A0  172 -> software_twi_read_byte (i2c_3 copy)
 *   0x000556A0..<0x0005574C  172 -> software_twi_read_byte (i2c_4 copy)
 *   0x0005574C..<0x000557F8  172 -> software_twi_read_byte (i2c_5 copy)
 *   0x000557F8..<0x00055878  128 -> software_twi_read_transaction_reg8 (i2c_2)
 *   0x00055878..<0x000558F8  128 -> software_twi_read_transaction_reg8 (i2c_3)
 *   0x000558F8..<0x00055988  144 -> software_twi_read_transaction_reg16 (i2c_4)
 *   0x00055988..<0x00055A18  144 -> software_twi_read_transaction_reg16 (i2c_5)
 *   0x00055A18..<0x00055A56   62 -> software_twi_start (i2c_2 copy)
 *   0x00055A56..<0x00055A94   62 -> software_twi_start (i2c_3 copy)
 *   0x00055A94..<0x00055AD2   62 -> software_twi_start (i2c_4 copy)
 *   0x00055AD2..<0x00055B10   62 -> software_twi_start (i2c_5 copy)
 *   0x00055B10..<0x00055B3C   44 -> software_twi_stop (i2c_2 copy)
 *   0x00055B3C..<0x00055B68   44 -> software_twi_stop (i2c_3 copy)
 *   0x00055B68..<0x00055B94   44 -> software_twi_stop (i2c_4 copy)
 *   0x00055B94..<0x00055BC0   44 -> software_twi_stop (i2c_5 copy)
 *   0x00055BC0..<0x00055C08   72 -> software_twi_wait_ack (i2c_2 copy)
 *   0x00055C08..<0x00055C50   72 -> software_twi_wait_ack (i2c_3 copy)
 *   0x00055C50..<0x00055C98   72 -> software_twi_wait_ack (i2c_4 copy)
 *   0x00055C98..<0x00055CE0   72 -> software_twi_wait_ack (i2c_5 copy)
 *   0x00055DBC..<0x00055E3C  128 -> software_twi_i2c_2_write
 *   0x00055E40..<0x00055EC0  128 -> software_twi_i2c_3_write
 *   0x00055EC4..<0x00055F58  148 -> software_twi_i2c_4_write
 *   0x00055F5C..<0x00055F9E   66 -> software_twi_i2c_5_write
 *   0x00055FA4..<0x00055FF2   78 -> software_twi_write_byte (i2c_2 copy)
 *   0x00055FF2..<0x00056040   78 -> software_twi_write_byte (i2c_3 copy)
 *   0x00056040..<0x0005608E   78 -> software_twi_write_byte (i2c_4 copy)
 *   0x0005608E..<0x000560DC   78 -> software_twi_write_byte (i2c_5 copy)
 *   0x000560DC..<0x0005613E   98 -> software_twi_write_transaction_reg16_byte
 *   0x0005613E..<0x000561A0   98 -> software_twi_write_transaction_reg8 (copy 1)
 *   0x000561A0..<0x00056202   98 -> software_twi_write_transaction_reg8 (copy 2)
 *   0x00056202..<0x00056274  114 -> software_twi_write_transaction_reg16
 *
 * Observable behavior is preserved (op order, udelay placement, NACK error
 * polarity, status codes, count-width truncations, the count-0 read quirk,
 * and the cross-instance call folding being behaviorally transparent).
 * Restructuring is limited to explicit provider bindings (GPIO/delay ops and
 * the i2c_4 gpio-configure wrapper), pointer/bounds validation returning the
 * recovered bad-argument code 4, and folding the byte-identical per-bus
 * primitive copies into one generic body each (stock passes the engine
 * pointer, so the copies are already generic).  Every divergence is listed
 * in docs/correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md.
 */

#include "software_twi/software_twi.h"

/* The recovered field offsets are a property of the 32-bit target ABI; on
 * wider host pointer ABIs the C layout legitimately differs, so the exact
 * layout asserts apply to the target ABI only. */
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(software_twi_engine, scl_pin) == 0x04u, "engine +0x04");
_Static_assert(offsetof(software_twi_engine, sda_pin) == 0x08u, "engine +0x08");
_Static_assert(offsetof(software_twi_engine, drive_low) == 0x0Cu, "engine +0x0C");
_Static_assert(offsetof(software_twi_engine, release_high) == 0x10u, "engine +0x10");
_Static_assert(offsetof(software_twi_engine, set_output) == 0x14u, "engine +0x14");
_Static_assert(offsetof(software_twi_engine, set_input) == 0x18u, "engine +0x18");
_Static_assert(offsetof(software_twi_engine, input_pull) == 0x1Cu, "engine +0x1C");
_Static_assert(offsetof(software_twi_engine, udelay) == 0x20u, "engine +0x20");
_Static_assert(offsetof(software_twi_engine, read_pin) == 0x24u, "engine +0x24");
_Static_assert(sizeof(software_twi_engine) == 0x28u, "recovered engine is 40 bytes");
_Static_assert(offsetof(software_twi_record, opened) == 0x04u, "record +0x04");
_Static_assert(offsetof(software_twi_record, engine) == 0x08u, "record +0x08");
_Static_assert(offsetof(software_twi_record, pin_release) == 0x30u, "record +0x30");
_Static_assert(offsetof(software_twi_record, registry_record) == 0x34u, "record +0x34");
_Static_assert(sizeof(software_twi_record) == 0x70u, "recovered record is 112 bytes");
_Static_assert(offsetof(software_twi_read_request, register_address) == 0x02u,
               "read request +0x02");
_Static_assert(offsetof(software_twi_read_request, buffer) == 0x0Cu,
               "read request +0x0C");
_Static_assert(offsetof(software_twi_read_request, length) == 0x10u,
               "read request +0x10");
_Static_assert(offsetof(software_twi_write_request, register_address) == 0x02u,
               "write request +0x02");
_Static_assert(offsetof(software_twi_write_request, buffer) == 0x04u,
               "write request +0x04");
_Static_assert(offsetof(software_twi_write_request, length) == 0x08u,
               "write request +0x08");
#endif

/* Recovered board bindings (boundary doc "Recovered instances and board
 * bindings").  Pins are absolute nRF52840 GPIO numbers: P0.n = n,
 * P1.n = 32 + n.  The delay context is the recovered per-bus delay argument;
 * the stock i2c_5 delay callback has no observable delay effect, which is a
 * property of the runtime-installed callback (outside this family), not of
 * this engine — the engine passes the context through unchanged. */
typedef struct {
    const char *name;
    uint32_t scl_pin;
    uint32_t sda_pin;
    uint32_t delay_context;
} software_twi_board_config;

static const software_twi_board_config board_configs[SOFTWARE_TWI_BUS_COUNT] = {
    {"i2c_2", 32u + 13u, 28u, 1u}, /* SCL P1.13, SDA P0.28 (GXT310) */
    {"i2c_3", 11u, 12u, 5u},       /* SCL P0.11, SDA P0.12 (dormant) */
    {"i2c_4", 32u + 9u, 31u, 1u},  /* SCL P1.09, SDA P0.31 (Goodix) */
    {"i2c_5", 32u + 14u, 32u + 11u, 1u}, /* SCL P1.14, SDA P1.11 (ST25DV/YHM2710) */
};

/* Recovered fixed arguments of the two gpio_configure calls in the i2c_4
 * open: (pin, direction 1, input 1, pull 0, drive 0, sense 0). */
#define SOFTWARE_TWI_I2C_4_CFG_DIRECTION UINT32_C(1)
#define SOFTWARE_TWI_I2C_4_CFG_INPUT UINT32_C(1)
#define SOFTWARE_TWI_I2C_4_CFG_PULL UINT32_C(0)
#define SOFTWARE_TWI_I2C_4_CFG_DRIVE UINT32_C(0)
#define SOFTWARE_TWI_I2C_4_CFG_SENSE UINT32_C(0)

static software_twi_record bus_records[SOFTWARE_TWI_BUS_COUNT];
static software_twi_gpio_configure_fn gpio_configure_provider;

static bool engine_operational(const software_twi_engine *engine) {
    return engine != NULL && engine->drive_low != NULL &&
           engine->release_high != NULL && engine->set_output != NULL &&
           engine->set_input != NULL && engine->udelay != NULL &&
           engine->read_pin != NULL;
}

void software_twi_initialize(const software_twi_providers *providers) {
    uint8_t *bytes = (uint8_t *)bus_records;
    for (size_t index = 0u; index < sizeof(bus_records); ++index) {
        bytes[index] = 0u;
    }
    gpio_configure_provider = NULL;
    for (size_t bus = 0u; bus < (size_t)SOFTWARE_TWI_BUS_COUNT; ++bus) {
        software_twi_record *record = &bus_records[bus];
        record->name = board_configs[bus].name;
        record->engine.scl_pin = board_configs[bus].scl_pin;
        record->engine.sda_pin = board_configs[bus].sda_pin;
        record->engine.delay_context = board_configs[bus].delay_context;
        if (providers != NULL) {
            record->engine.drive_low = providers->drive_low;
            record->engine.release_high = providers->release_high;
            record->engine.set_output = providers->set_output;
            record->engine.set_input = providers->set_input;
            record->engine.udelay = providers->udelay;
            record->engine.read_pin = providers->read_pin;
            record->engine.input_pull = providers->input_pull;
        }
    }
    if (providers != NULL) {
        gpio_configure_provider = providers->gpio_configure;
    }
}

software_twi_engine *software_twi_bus_engine(software_twi_bus_id bus) {
    if (bus >= SOFTWARE_TWI_BUS_COUNT) {
        return NULL;
    }
    return &bus_records[bus].engine;
}

software_twi_record *software_twi_bus_record(software_twi_bus_id bus) {
    if (bus >= SOFTWARE_TWI_BUS_COUNT) {
        return NULL;
    }
    return &bus_records[bus];
}

void software_twi_start(software_twi_engine *engine) {
    if (!engine_operational(engine)) {
        return; /* fail explicit: stock would fault on the NULL vtable slot */
    }
    engine->set_output(engine->scl_pin);
    engine->set_output(engine->sda_pin);
    engine->release_high(engine->scl_pin);
    engine->release_high(engine->sda_pin);
    engine->udelay(engine->delay_context);
    engine->drive_low(engine->sda_pin);
    engine->udelay(engine->delay_context);
    engine->drive_low(engine->scl_pin);
    engine->udelay(engine->delay_context);
}

void software_twi_stop(software_twi_engine *engine) {
    if (!engine_operational(engine)) {
        return;
    }
    engine->set_output(engine->scl_pin);
    engine->set_output(engine->sda_pin);
    engine->drive_low(engine->sda_pin);
    engine->release_high(engine->scl_pin);
    engine->udelay(engine->delay_context);
    engine->release_high(engine->sda_pin);
}

uint32_t software_twi_wait_ack(software_twi_engine *engine) {
    if (!engine_operational(engine)) {
        return 1u; /* error polarity: report NACK when the engine is unbound */
    }
    engine->release_high(engine->sda_pin);
    engine->set_input(engine->sda_pin, engine->input_pull);
    engine->udelay(engine->delay_context);
    engine->release_high(engine->scl_pin);
    engine->udelay(engine->delay_context);
    uint32_t nack = engine->read_pin(engine->sda_pin) != 0u ? 1u : 0u;
    engine->drive_low(engine->scl_pin);
    engine->set_output(engine->sda_pin);
    engine->udelay(engine->delay_context);
    return nack;
}

uint8_t software_twi_read_byte(uint32_t send_ack, software_twi_engine *engine) {
    if (!engine_operational(engine)) {
        return 0u;
    }
    engine->set_input(engine->sda_pin, engine->input_pull);
    engine->udelay(engine->delay_context);
    uint8_t value = 0u;
    for (uint32_t bit = 0u; bit < 8u; ++bit) {
        value = (uint8_t)(value << 1);
        engine->release_high(engine->scl_pin);
        engine->udelay(engine->delay_context);
        if (engine->read_pin(engine->sda_pin) != 0u) {
            value = (uint8_t)(value + 1u);
        }
        engine->drive_low(engine->scl_pin);
        engine->udelay(engine->delay_context);
    }
    engine->set_output(engine->sda_pin);
    engine->udelay(engine->delay_context);
    /* ACK and NACK paths differ only in the first SDA drive; both converge on
     * the shared trailing release_high(SDA). */
    if (send_ack != 0u) {
        engine->drive_low(engine->sda_pin);
    } else {
        engine->release_high(engine->sda_pin);
    }
    engine->udelay(engine->delay_context);
    engine->release_high(engine->scl_pin);
    engine->udelay(engine->delay_context);
    engine->drive_low(engine->scl_pin);
    engine->udelay(engine->delay_context);
    engine->release_high(engine->sda_pin);
    return value;
}

void software_twi_write_byte(uint8_t value, software_twi_engine *engine) {
    if (!engine_operational(engine)) {
        return;
    }
    for (uint32_t bit = 0u; bit < 8u; ++bit) {
        if ((value & 0x80u) != 0u) {
            engine->release_high(engine->sda_pin);
        } else {
            engine->drive_low(engine->sda_pin);
        }
        engine->udelay(engine->delay_context);
        engine->release_high(engine->scl_pin);
        engine->udelay(engine->delay_context);
        engine->drive_low(engine->scl_pin);
        if (bit == 7u) {
            /* Recovered in-loop ACK-window prep after bit 7. */
            engine->release_high(engine->sda_pin);
        }
        value = (uint8_t)(value << 1);
        engine->udelay(engine->delay_context);
    }
}

/* Shared body of the four stock read transactions.  `wide_register` selects
 * the 16-bit register form (i2c_4/i2c_5 copies); the count is pre-truncated
 * by the caller to the recovered per-bus width. */
static uint32_t read_transaction(uint8_t address, uint16_t reg,
                                 bool wide_register, uint8_t *buffer,
                                 uint32_t count,
                                 software_twi_engine *engine) {
    if (!engine_operational(engine) || buffer == NULL) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    software_twi_start(engine);
    software_twi_write_byte(address, engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    if (wide_register) {
        software_twi_write_byte((uint8_t)(reg >> 8), engine);
        if (software_twi_wait_ack(engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
    }
    software_twi_write_byte((uint8_t)(reg & 0xFFu), engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    software_twi_start(engine); /* repeated start */
    software_twi_write_byte((uint8_t)(address | 0x01u), engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    /* Recovered loop shape: count-1 bytes with ACK, then one byte with NACK.
     * The stock comparison is signed (blt) against the 32-bit count-1, so a
     * zero count wraps to -1, skips the ACK loop, and still reads exactly
     * one byte. */
    int32_t ack_reads = (int32_t)(count - 1u);
    uint32_t index = 0u;
    while ((int32_t)index < ack_reads) {
        buffer[index] = software_twi_read_byte(1u, engine);
        ++index;
    }
    buffer[index] = software_twi_read_byte(0u, engine);
    software_twi_stop(engine);
    return SOFTWARE_TWI_STATUS_OK;
}

uint32_t software_twi_read_transaction_reg8(uint8_t address, uint8_t reg,
                                            uint8_t *buffer, uint8_t count,
                                            software_twi_engine *engine) {
    return read_transaction(address, reg, false, buffer, count, engine);
}

uint32_t software_twi_read_transaction_reg16(uint8_t address, uint16_t reg,
                                             uint8_t *buffer, uint16_t count,
                                             software_twi_engine *engine) {
    return read_transaction(address, reg, true, buffer, count, engine);
}

uint32_t software_twi_write_transaction_reg16_byte(uint8_t address,
                                                   uint16_t reg, uint8_t data,
                                                   software_twi_engine *engine) {
    if (!engine_operational(engine)) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    software_twi_start(engine);
    software_twi_write_byte(address, engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    software_twi_write_byte((uint8_t)(reg >> 8), engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    software_twi_write_byte((uint8_t)(reg & 0xFFu), engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    software_twi_write_byte(data, engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    software_twi_stop(engine);
    return SOFTWARE_TWI_STATUS_OK;
}

/* Shared body of the three multi-byte write transactions. */
static uint32_t write_transaction(uint8_t address, uint16_t reg,
                                  bool wide_register, const uint8_t *buffer,
                                  uint32_t count,
                                  software_twi_engine *engine) {
    if (!engine_operational(engine) || (count != 0u && buffer == NULL)) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    software_twi_start(engine);
    software_twi_write_byte(address, engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    if (wide_register) {
        software_twi_write_byte((uint8_t)(reg >> 8), engine);
        if (software_twi_wait_ack(engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
    }
    software_twi_write_byte((uint8_t)(reg & 0xFFu), engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    for (uint32_t index = 0u; index < count; ++index) {
        software_twi_write_byte(buffer[index], engine);
        if (software_twi_wait_ack(engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
    }
    software_twi_stop(engine);
    return SOFTWARE_TWI_STATUS_OK;
}

uint32_t software_twi_write_transaction_reg8(uint8_t address, uint8_t reg,
                                             const uint8_t *buffer,
                                             uint8_t count,
                                             software_twi_engine *engine) {
    return write_transaction(address, reg, false, buffer, count, engine);
}

uint32_t software_twi_write_transaction_reg16(uint8_t address, uint16_t reg,
                                              const uint8_t *buffer,
                                              uint8_t count,
                                              software_twi_engine *engine) {
    return write_transaction(address, reg, true, buffer, count, engine);
}

/* Shared body of the i2c_2/i2c_3/i2c_5 opens (byte-identical in stock). */
static uint32_t bus_open(software_twi_record *record) {
    if (record->opened != 0u) {
        return SOFTWARE_TWI_STATUS_OK;
    }
    if (!engine_operational(&record->engine)) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    record->engine.set_output(record->engine.scl_pin);
    record->engine.set_output(record->engine.sda_pin);
    record->engine.release_high(record->engine.scl_pin);
    record->engine.release_high(record->engine.sda_pin);
    record->opened = 1u;
    return SOFTWARE_TWI_STATUS_OK;
}

uint32_t software_twi_i2c_2_open(void) {
    return bus_open(&bus_records[SOFTWARE_TWI_BUS_I2C_2]);
}

uint32_t software_twi_i2c_3_open(void) {
    return bus_open(&bus_records[SOFTWARE_TWI_BUS_I2C_3]);
}

uint32_t software_twi_i2c_5_open(void) {
    return bus_open(&bus_records[SOFTWARE_TWI_BUS_I2C_5]);
}

uint32_t software_twi_i2c_4_open(void) {
    software_twi_record *record = &bus_records[SOFTWARE_TWI_BUS_I2C_4];
    if (record->opened != 0u) {
        return SOFTWARE_TWI_STATUS_OK;
    }
    if (!engine_operational(&record->engine) || gpio_configure_provider == NULL) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    record->engine.set_output(record->engine.scl_pin);
    record->engine.set_output(record->engine.sda_pin);
    record->engine.release_high(record->engine.scl_pin);
    record->engine.release_high(record->engine.sda_pin);
    /* Recovered in-house HAL special-casing (stock calls the nrf_gpio_cfg
     * wrapper at 0x00078EE6 twice with the fixed arguments below). */
    gpio_configure_provider(record->engine.scl_pin,
                            SOFTWARE_TWI_I2C_4_CFG_DIRECTION,
                            SOFTWARE_TWI_I2C_4_CFG_INPUT,
                            SOFTWARE_TWI_I2C_4_CFG_PULL,
                            SOFTWARE_TWI_I2C_4_CFG_DRIVE,
                            SOFTWARE_TWI_I2C_4_CFG_SENSE);
    gpio_configure_provider(record->engine.sda_pin,
                            SOFTWARE_TWI_I2C_4_CFG_DIRECTION,
                            SOFTWARE_TWI_I2C_4_CFG_INPUT,
                            SOFTWARE_TWI_I2C_4_CFG_PULL,
                            SOFTWARE_TWI_I2C_4_CFG_DRIVE,
                            SOFTWARE_TWI_I2C_4_CFG_SENSE);
    record->opened = 1u;
    return SOFTWARE_TWI_STATUS_OK;
}

/* Shared read-adapter body.  `merged_errors` reproduces the i2c_5 copy,
 * which returns 4 for both a NULL request and a not-open bus. */
static uint32_t read_adapter(software_twi_record *record, bool wide_register,
                             bool wide_count, bool merged_errors,
                             const software_twi_read_request *request) {
    if (request == NULL) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    if (record->opened == 0u) {
        return merged_errors ? SOFTWARE_TWI_STATUS_BAD_ARGUMENT
                             : SOFTWARE_TWI_STATUS_READ_NOT_OPEN;
    }
    if (request->buffer == NULL) {
        /* Stock dereferences the buffer unchecked; fail explicit instead. */
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    uint32_t status;
    if (wide_register) {
        uint16_t count = wide_count ? request->length
                                    : (uint16_t)(uint8_t)request->length;
        status = software_twi_read_transaction_reg16(request->address,
                                                     request->register_address,
                                                     request->buffer, count,
                                                     &record->engine);
    } else {
        status = software_twi_read_transaction_reg8(request->address,
                                                    (uint8_t)request->register_address,
                                                    request->buffer,
                                                    (uint8_t)request->length,
                                                    &record->engine);
    }
    return status == SOFTWARE_TWI_STATUS_OK ? SOFTWARE_TWI_STATUS_OK
                                            : SOFTWARE_TWI_STATUS_READ_NACK;
}

uint32_t software_twi_i2c_2_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request) {
    (void)device;     /* ignored in stock (ops-table dispatch slot) */
    (void)operation;  /* ignored in stock */
    return read_adapter(&bus_records[SOFTWARE_TWI_BUS_I2C_2], false, false,
                        false, request);
}

uint32_t software_twi_i2c_3_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request) {
    (void)device;
    (void)operation;
    return read_adapter(&bus_records[SOFTWARE_TWI_BUS_I2C_3], false, false,
                        false, request);
}

uint32_t software_twi_i2c_4_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request) {
    (void)device;
    (void)operation;
    return read_adapter(&bus_records[SOFTWARE_TWI_BUS_I2C_4], true, true,
                        false, request);
}

uint32_t software_twi_i2c_5_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request) {
    (void)device;
    (void)operation;
    return read_adapter(&bus_records[SOFTWARE_TWI_BUS_I2C_5], true, false,
                        true, request);
}

/* Shared i2c_2/i2c_3 write-adapter body: single-byte transfers take an
 * inline start/address/register-byte/data/stop path; anything else forwards
 * to the multi-byte transaction with the count truncated to 8 bits. */
static uint32_t write_adapter_reg8(software_twi_record *record,
                                   const software_twi_write_request *request) {
    if (request == NULL) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    if (record->opened == 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN;
    }
    uint8_t address = request->address;
    uint8_t reg = (uint8_t)request->register_address;
    if (request->length == 1u) {
        if (request->buffer == NULL) {
            return SOFTWARE_TWI_STATUS_BAD_ARGUMENT; /* stock dereferences */
        }
        if (!engine_operational(&record->engine)) {
            return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
        }
        uint8_t data = request->buffer[0];
        software_twi_start(&record->engine);
        software_twi_write_byte(address, &record->engine);
        if (software_twi_wait_ack(&record->engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
        software_twi_write_byte(reg, &record->engine);
        if (software_twi_wait_ack(&record->engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
        software_twi_write_byte(data, &record->engine);
        if (software_twi_wait_ack(&record->engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
        software_twi_stop(&record->engine);
        return SOFTWARE_TWI_STATUS_OK;
    }
    uint32_t status = software_twi_write_transaction_reg8(
        address, reg, request->buffer, (uint8_t)request->length,
        &record->engine);
    return status == SOFTWARE_TWI_STATUS_OK ? SOFTWARE_TWI_STATUS_OK
                                            : SOFTWARE_TWI_STATUS_WRITE_NACK;
}

uint32_t software_twi_i2c_2_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request) {
    (void)device;
    (void)operation;
    return write_adapter_reg8(&bus_records[SOFTWARE_TWI_BUS_I2C_2], request);
}

uint32_t software_twi_i2c_3_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request) {
    (void)device;
    (void)operation;
    return write_adapter_reg8(&bus_records[SOFTWARE_TWI_BUS_I2C_3], request);
}

/* i2c_4 write adapter (0x00055EC4): no register byte in either path; the
 * single-byte path sends address + one data byte, the multi-byte path loops
 * over the full 16-bit length. */
uint32_t software_twi_i2c_4_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request) {
    (void)device;
    (void)operation;
    software_twi_record *record = &bus_records[SOFTWARE_TWI_BUS_I2C_4];
    if (request == NULL) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    if (record->opened == 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN;
    }
    if (request->buffer == NULL || !engine_operational(&record->engine)) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT; /* stock dereferences */
    }
    software_twi_engine *engine = &record->engine;
    software_twi_start(engine);
    software_twi_write_byte(request->address, engine);
    if (software_twi_wait_ack(engine) != 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NACK;
    }
    if (request->length == 1u) {
        software_twi_write_byte(request->buffer[0], engine);
        if (software_twi_wait_ack(engine) != 0u) {
            return SOFTWARE_TWI_STATUS_WRITE_NACK;
        }
    } else {
        for (uint32_t index = 0u; index < (uint32_t)request->length; ++index) {
            software_twi_write_byte(request->buffer[index], engine);
            if (software_twi_wait_ack(engine) != 0u) {
                return SOFTWARE_TWI_STATUS_WRITE_NACK;
            }
        }
    }
    software_twi_stop(engine);
    return SOFTWARE_TWI_STATUS_OK;
}

/* i2c_5 write adapter (0x00055F5C): length 1 tail-calls the u16-register
 * single-byte transaction (stock body 0x000560DC); anything else forwards to
 * the u16-register multi-byte transaction with an 8-bit count. */
uint32_t software_twi_i2c_5_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request) {
    (void)device;
    (void)operation;
    software_twi_record *record = &bus_records[SOFTWARE_TWI_BUS_I2C_5];
    if (request == NULL) {
        return SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
    }
    if (record->opened == 0u) {
        return SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN;
    }
    uint32_t status;
    if (request->length == 1u) {
        if (request->buffer == NULL) {
            return SOFTWARE_TWI_STATUS_BAD_ARGUMENT; /* stock dereferences */
        }
        status = software_twi_write_transaction_reg16_byte(
            request->address, request->register_address, request->buffer[0],
            &record->engine);
    } else {
        status = software_twi_write_transaction_reg16(
            request->address, request->register_address, request->buffer,
            (uint8_t)request->length, &record->engine);
    }
    return status == SOFTWARE_TWI_STATUS_OK ? SOFTWARE_TWI_STATUS_OK
                                            : SOFTWARE_TWI_STATUS_WRITE_NACK;
}
