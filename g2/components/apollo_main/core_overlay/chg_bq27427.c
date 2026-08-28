/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of driver/chg/drv_bq27427.c. */

#include <stddef.h>
#include <stdint.h>

void *memcpy(void *destination, const void *source, size_t length);
void *memset(void *destination, int value, size_t length);

enum {
    OPEN_CFW_BQ27427_BUS = 7,
    OPEN_CFW_BQ27427_ADDRESS = 0x55,
    OPEN_CFW_BQ27427_BLOCK_SIZE = 32,
};

typedef struct {
    uint8_t subclass;
    uint8_t offset;
    uint8_t width;
    uint8_t reserved;
    uint16_t minimum;
    uint16_t maximum;
} open_cfw_bq27427_dm_descriptor;

typedef struct {
    uint8_t subclass;
    uint8_t block;
    uint8_t data[OPEN_CFW_BQ27427_BLOCK_SIZE];
    uint8_t valid;
    uint8_t dirty;
} open_cfw_bq27427_dm_block;

typedef struct {
    uint32_t energy_full_design;
    uint32_t charge_full_design;
    uint32_t voltage_min_design;
} open_cfw_bq27427_settings;

typedef struct {
    uint32_t reserved;
    int32_t state_of_charge;
    int32_t voltage_mv;
    int32_t average_current_ma;
    int32_t temperature_centi_c;
} open_cfw_bq27427_runtime;

_Static_assert(sizeof(open_cfw_bq27427_dm_descriptor) == 8,
    "stock DM descriptor must remain eight bytes");
_Static_assert(sizeof(open_cfw_bq27427_dm_block) == 36,
    "stock DM block must remain 36 bytes");
_Static_assert(offsetof(open_cfw_bq27427_runtime, state_of_charge) == 4,
    "stock SOC offset changed");
_Static_assert(offsetof(open_cfw_bq27427_runtime, temperature_centi_c) == 0x10,
    "stock temperature offset changed");

#ifndef OPEN_CFW_BQ27427_TRANSFER_READ
int open_cfw_bq27427_transfer_read(
    uint8_t bus, uint8_t address, const uint8_t *command,
    size_t command_length, uint8_t *data, size_t data_length
);
#define OPEN_CFW_BQ27427_TRANSFER_READ(bus, address, command, command_length, data, data_length) \
    open_cfw_bq27427_transfer_read((bus), (address), (command), \
        (command_length), (data), (data_length))
#endif

#ifndef OPEN_CFW_BQ27427_TRANSFER_WRITE
int open_cfw_bq27427_transfer_write(
    uint8_t bus, uint8_t address, const uint8_t *command,
    size_t command_length, const uint8_t *data, size_t data_length
);
#define OPEN_CFW_BQ27427_TRANSFER_WRITE(bus, address, command, command_length, data, data_length) \
    open_cfw_bq27427_transfer_write((bus), (address), (command), \
        (command_length), (data), (data_length))
#endif

#ifndef OPEN_CFW_BQ27427_DELAY_MS
void open_cfw_bq27427_delay_ms(uint32_t delay_ms);
#define OPEN_CFW_BQ27427_DELAY_MS(delay_ms) \
    open_cfw_bq27427_delay_ms((delay_ms))
#endif

#ifndef OPEN_CFW_BQ27427_DIAGNOSTIC
#define OPEN_CFW_BQ27427_DIAGNOSTIC(code) ((void)(code))
#endif

#ifndef OPEN_CFW_BQ27427_RUNTIME_ADDRESS
#define OPEN_CFW_BQ27427_RUNTIME_ADDRESS 0x20073b18u
#endif

#ifndef OPEN_CFW_BQ27427_RUNTIME
#define OPEN_CFW_BQ27427_RUNTIME \
    (*(open_cfw_bq27427_runtime *)(uintptr_t)OPEN_CFW_BQ27427_RUNTIME_ADDRESS)
#endif

#ifndef OPEN_CFW_BQ27427_UNSEAL_KEY
#define OPEN_CFW_BQ27427_UNSEAL_KEY 0x80008000u
#endif

static const open_cfw_bq27427_dm_descriptor open_cfw_bq27427_dm_map[] = {
    {82u, 6u, 2u, 0u, 0u, 8000u},
    {82u, 8u, 2u, 0u, 0u, 32767u},
    {82u, 10u, 2u, 0u, 3000u, 4400u},
    {64u, 4u, 1u, 0u, 0u, 255u},
    {82u, 2u, 1u, 0u, 0u, 255u},
    {81u, 0u, 2u, 0u, 0u, 2000u},
    {105u, 5u, 1u, 0u, 0u, 32767u},
};

static const open_cfw_bq27427_settings open_cfw_bq27427_defaults = {
    240u, 80u, 3100u,
};

static int open_cfw_bq27427_i2c_read_reg(uint8_t reg, uint8_t single_byte)
{
    uint8_t command;
    uint8_t data[2] = {0u, 0u};

    command = reg;
    (void)OPEN_CFW_BQ27427_TRANSFER_READ(
        OPEN_CFW_BQ27427_BUS, OPEN_CFW_BQ27427_ADDRESS,
        &command, 1u, &data[0], 1u
    );
    if (single_byte == 0u) {
        command = (uint8_t)(reg + 1u);
        (void)OPEN_CFW_BQ27427_TRANSFER_READ(
            OPEN_CFW_BQ27427_BUS, OPEN_CFW_BQ27427_ADDRESS,
            &command, 1u, &data[1], 1u
        );
    }
    return (int)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static int open_cfw_bq27427_i2c_write_reg(
    uint8_t reg, uint16_t value, uint8_t single_byte
)
{
    uint8_t command = reg;
    uint8_t data[2] = {(uint8_t)value, (uint8_t)(value >> 8)};
    return OPEN_CFW_BQ27427_TRANSFER_WRITE(
        OPEN_CFW_BQ27427_BUS, OPEN_CFW_BQ27427_ADDRESS,
        &command, 1u, data, single_byte != 0u ? 1u : 2u
    );
}

static int open_cfw_bq27427_i2c_read_block(
    uint8_t reg, uint8_t *data, size_t length
)
{
    uint8_t command = reg;
    return OPEN_CFW_BQ27427_TRANSFER_READ(
        OPEN_CFW_BQ27427_BUS, OPEN_CFW_BQ27427_ADDRESS,
        &command, 1u, data, length
    );
}

static int open_cfw_bq27427_i2c_write_block(
    uint8_t reg, const uint8_t *data, size_t length
)
{
    uint8_t command = reg;
    uint8_t copy[35];
    int status;

    if (length > sizeof(copy)) {
        length = sizeof(copy);
    }
    memcpy(copy, data, length);
    status = OPEN_CFW_BQ27427_TRANSFER_WRITE(
        OPEN_CFW_BQ27427_BUS, OPEN_CFW_BQ27427_ADDRESS,
        &command, 1u, copy, length
    );
    if (status != 0) {
        OPEN_CFW_BQ27427_DIAGNOSTIC(1u);
    }
    /* The stock block-write wrapper logs, but deliberately returns success. */
    return 0;
}

int open_cfw_bq27427_read_flags(void)
{
    return open_cfw_bq27427_i2c_read_reg(0x06u, 0u);
}

int open_cfw_bq27427_read_soc(void)
{
    return open_cfw_bq27427_i2c_read_reg(0x1cu, 0u);
}

int open_cfw_bq27427_read_temperature(void)
{
    return open_cfw_bq27427_i2c_read_reg(0x02u, 0u) - 2731;
}

int open_cfw_bq27427_read_battery_voltage(void)
{
    return open_cfw_bq27427_i2c_read_reg(0x04u, 0u);
}

int open_cfw_bq27427_read_charge(uint8_t reg)
{
    return open_cfw_bq27427_i2c_read_reg(reg, 0u);
}

int open_cfw_bq27427_read_nom_capacity(void) { return open_cfw_bq27427_read_charge(0x08u); }
int open_cfw_bq27427_read_avail_capacity(void) { return open_cfw_bq27427_read_charge(0x0au); }
int open_cfw_bq27427_read_rem_capacity(void) { return open_cfw_bq27427_read_charge(0x0cu); }
int open_cfw_bq27427_read_full_capacity(void) { return open_cfw_bq27427_read_charge(0x0eu); }

int open_cfw_bq27427_read_ai(void)
{
    return (int16_t)open_cfw_bq27427_i2c_read_reg(0x10u, 0u);
}

int open_cfw_bq27427_read_ap(void)
{
    return (int16_t)open_cfw_bq27427_i2c_read_reg(0x18u, 0u);
}

int open_cfw_bq27427_read_int_temp(void) { return open_cfw_bq27427_read_charge(0x1eu); }
int open_cfw_bq27427_read_rem_cap_unfl(void) { return open_cfw_bq27427_read_charge(0x28u); }
int open_cfw_bq27427_read_rem_cap_fil(void) { return open_cfw_bq27427_read_charge(0x2au); }
int open_cfw_bq27427_read_full_cap_unfl(void) { return open_cfw_bq27427_read_charge(0x2cu); }
int open_cfw_bq27427_read_full_cap_fil(void) { return open_cfw_bq27427_read_charge(0x2eu); }
int open_cfw_bq27427_read_soc_unfl(void) { return open_cfw_bq27427_read_charge(0x30u); }

int open_cfw_bq27427_seal(void)
{
    return open_cfw_bq27427_i2c_write_reg(0x00u, 0x0020u, 0u);
}

int open_cfw_bq27427_unseal(void)
{
    int status;
    uint32_t key = OPEN_CFW_BQ27427_UNSEAL_KEY;

    if (key == 0u) {
        return -1;
    }
    status = open_cfw_bq27427_i2c_write_reg(
        0x00u, (uint16_t)(key >> 16), 0u
    );
    if (status == 0) {
        status = open_cfw_bq27427_i2c_write_reg(
            0x00u, (uint16_t)key, 0u
        );
    }
    return status;
}

uint8_t open_cfw_bq27427_checksum_dm_block(
    const open_cfw_bq27427_dm_block *block
)
{
    uint32_t sum = 0u;
    size_t index;
    for (index = 0u; index < OPEN_CFW_BQ27427_BLOCK_SIZE; ++index) {
        sum += block->data[index];
    }
    return (uint8_t)(0xffu - (sum & 0xffu));
}

int open_cfw_bq27427_read_dm_block(open_cfw_bq27427_dm_block *block)
{
    int status;
    int checksum;

    block->valid = 0u;
    status = open_cfw_bq27427_i2c_write_reg(0x3eu, block->subclass, 1u);
    if (status == 0) {
        status = open_cfw_bq27427_i2c_write_reg(0x3fu, block->block, 1u);
    }
    if (status == 0) {
        OPEN_CFW_BQ27427_DELAY_MS(1u);
        status = open_cfw_bq27427_i2c_read_block(
            0x40u, block->data, OPEN_CFW_BQ27427_BLOCK_SIZE
        );
    }
    if (status == 0) {
        checksum = open_cfw_bq27427_i2c_read_reg(0x60u, 1u);
        if (checksum < 0 || (uint8_t)checksum !=
                open_cfw_bq27427_checksum_dm_block(block)) {
            status = -1;
        }
    }
    if (status == 0) {
        block->valid = 1u;
        block->dirty = 0u;
    }
    return status;
}

void open_cfw_bq27427_update_dm_block(
    open_cfw_bq27427_dm_block *block, uint8_t descriptor_index,
    uint32_t value
)
{
    const open_cfw_bq27427_dm_descriptor *descriptor;
    uint8_t offset;

    if (descriptor_index >= sizeof(open_cfw_bq27427_dm_map) /
            sizeof(open_cfw_bq27427_dm_map[0]) || block->valid == 0u) {
        return;
    }
    descriptor = &open_cfw_bq27427_dm_map[descriptor_index];
    offset = (uint8_t)(descriptor->offset % OPEN_CFW_BQ27427_BLOCK_SIZE);
    if (descriptor->width == 1u) {
        block->data[offset] = (uint8_t)value;
    } else if (descriptor->width == 2u) {
        block->data[offset] = (uint8_t)(value >> 8);
        block->data[(uint8_t)(offset + 1u)] = (uint8_t)value;
    } else {
        return;
    }
    block->dirty = 1u;
}

static int open_cfw_bq27427_cfgupdate_priv(uint8_t active)
{
    int status;
    unsigned retries = 100u;
    uint8_t expected = active != 0u;

    status = open_cfw_bq27427_i2c_write_reg(
        0x00u, active != 0u ? 0x0013u : 0x0042u, 0u
    );
    while (status == 0 && retries != 0u) {
        OPEN_CFW_BQ27427_DELAY_MS(25u);
        status = open_cfw_bq27427_i2c_read_reg(0x06u, 0u);
        if (status < 0 || (((uint8_t)status >> 4) & 1u) == expected) {
            break;
        }
        --retries;
    }
    return status < 0 ? status : 0;
}

int open_cfw_bq27427_set_cfgupdate(void)
{
    return open_cfw_bq27427_cfgupdate_priv(1u);
}

int open_cfw_bq27427_soft_reset(void)
{
    return open_cfw_bq27427_cfgupdate_priv(0u);
}

int open_cfw_bq27427_execute_control_word(uint8_t control_word)
{
    int status = open_cfw_bq27427_i2c_write_reg(
        0x00u, control_word, 0u
    );
    if (status == 0) {
        OPEN_CFW_BQ27427_DELAY_MS(100u);
    }
    return status;
}

int open_cfw_bq27427_write_dm_block(open_cfw_bq27427_dm_block *block)
{
    int status;

    if (block->dirty == 0u) {
        return 0;
    }
    status = open_cfw_bq27427_set_cfgupdate();
    if (status == 0) status = open_cfw_bq27427_i2c_write_reg(0x61u, 0u, 1u);
    if (status == 0) status = open_cfw_bq27427_i2c_write_reg(0x3eu, block->subclass, 1u);
    if (status == 0) status = open_cfw_bq27427_i2c_write_reg(0x3fu, block->block, 1u);
    if (status == 0) {
        OPEN_CFW_BQ27427_DELAY_MS(1u);
        status = open_cfw_bq27427_i2c_write_block(
            0x40u, block->data, OPEN_CFW_BQ27427_BLOCK_SIZE
        );
    }
    if (status == 0) {
        status = open_cfw_bq27427_i2c_write_reg(
            0x60u, open_cfw_bq27427_checksum_dm_block(block), 1u
        );
    }
    if (status == 0) {
        OPEN_CFW_BQ27427_DELAY_MS(1u);
        status = open_cfw_bq27427_soft_reset();
    } else {
        (void)open_cfw_bq27427_soft_reset();
    }
    if (status == 0) {
        block->dirty = 0u;
    }
    return status;
}

static void open_cfw_bq27427_init_block(
    open_cfw_bq27427_dm_block *block, uint8_t descriptor_index
)
{
    const open_cfw_bq27427_dm_descriptor *descriptor =
        &open_cfw_bq27427_dm_map[descriptor_index];
    memset(block, 0, sizeof(*block));
    block->subclass = descriptor->subclass;
    block->block = (uint8_t)(descriptor->offset / OPEN_CFW_BQ27427_BLOCK_SIZE);
}

void open_cfw_bq27427_configure_from_params(
    const open_cfw_bq27427_settings *settings
)
{
    open_cfw_bq27427_dm_block design;
    open_cfw_bq27427_dm_block voltage;
    open_cfw_bq27427_dm_block state;
    open_cfw_bq27427_dm_block unused;
    open_cfw_bq27427_dm_block taper;
    open_cfw_bq27427_dm_block *voltage_target;

    open_cfw_bq27427_init_block(&design, 0u);
    open_cfw_bq27427_init_block(&voltage, 2u);
    open_cfw_bq27427_init_block(&state, 3u);
    open_cfw_bq27427_init_block(&unused, 5u);
    open_cfw_bq27427_init_block(&taper, 6u);
    if (open_cfw_bq27427_unseal() < 0) return;

    if (settings->charge_full_design > 0u && settings->energy_full_design > 0u) {
        (void)open_cfw_bq27427_read_dm_block(&design);
        open_cfw_bq27427_update_dm_block(&design, 0u, settings->charge_full_design);
        open_cfw_bq27427_update_dm_block(&design, 1u, settings->energy_full_design);
        open_cfw_bq27427_update_dm_block(&design, 4u, 3u);
    }
    if (settings->voltage_min_design > 0u) {
        if (design.subclass == voltage.subclass && design.block == voltage.block) {
            voltage_target = &design;
        } else {
            (void)open_cfw_bq27427_read_dm_block(&voltage);
            voltage_target = &voltage;
        }
        open_cfw_bq27427_update_dm_block(
            voltage_target, 2u, settings->voltage_min_design
        );
    }
    (void)open_cfw_bq27427_read_dm_block(&state);
    open_cfw_bq27427_update_dm_block(&state, 3u, 43u);
    (void)open_cfw_bq27427_read_dm_block(&unused);
    (void)open_cfw_bq27427_read_dm_block(&taper);
    open_cfw_bq27427_update_dm_block(&taper, 6u, 40u);
    (void)open_cfw_bq27427_write_dm_block(&design);
    (void)open_cfw_bq27427_write_dm_block(&voltage);
    (void)open_cfw_bq27427_write_dm_block(&state);
    (void)open_cfw_bq27427_write_dm_block(&taper);
    (void)open_cfw_bq27427_seal();
}

int open_cfw_bq27427_change_chemistry_profile(void)
{
    int status;
    if (open_cfw_bq27427_unseal() < 0) return -1;
    (void)open_cfw_bq27427_i2c_write_reg(0x00u, 0x0008u, 0u);
    (void)open_cfw_bq27427_i2c_read_reg(0x00u, 0u);
    status = open_cfw_bq27427_set_cfgupdate();
    if (status == 0) {
        (void)open_cfw_bq27427_execute_control_word(0x31u);
        OPEN_CFW_BQ27427_DELAY_MS(1u);
        status = open_cfw_bq27427_soft_reset();
    }
    if (status == 0) {
        (void)open_cfw_bq27427_i2c_write_reg(0x00u, 0x0008u, 0u);
        (void)open_cfw_bq27427_i2c_read_reg(0x00u, 0u);
        (void)open_cfw_bq27427_seal();
    }
    return status;
}

void open_cfw_bq27427_apply_settings(
    const open_cfw_bq27427_settings *settings
)
{
    if (settings->energy_full_design >= 37500u ||
        settings->charge_full_design >= 8001u ||
        settings->voltage_min_design < 2500u ||
        settings->voltage_min_design > 3700u) {
        return;
    }
    open_cfw_bq27427_configure_from_params(settings);
    (void)open_cfw_bq27427_change_chemistry_profile();
}

void open_cfw_bq27427_settings_apply_defaults(void)
{
    open_cfw_bq27427_apply_settings(&open_cfw_bq27427_defaults);
}

int open_cfw_bq27427_status_update(void)
{
    int flags = open_cfw_bq27427_read_flags();
    int soc;
    int temperature;
    int voltage;
    int current;
    if (flags == 0 || (uint8_t)flags == 0xffu) return -1;
    if (flags < 0) return 0;
    soc = open_cfw_bq27427_read_soc();
    temperature = open_cfw_bq27427_read_temperature();
    voltage = open_cfw_bq27427_read_battery_voltage();
    (void)open_cfw_bq27427_read_nom_capacity();
    (void)open_cfw_bq27427_read_avail_capacity();
    (void)open_cfw_bq27427_read_rem_capacity();
    (void)open_cfw_bq27427_read_full_capacity();
    current = open_cfw_bq27427_read_ai();
    (void)open_cfw_bq27427_read_ap();
    (void)open_cfw_bq27427_read_int_temp();
    (void)open_cfw_bq27427_read_rem_cap_unfl();
    (void)open_cfw_bq27427_read_rem_cap_fil();
    (void)open_cfw_bq27427_read_full_cap_unfl();
    (void)open_cfw_bq27427_read_full_cap_fil();
    (void)open_cfw_bq27427_read_soc_unfl();
    OPEN_CFW_BQ27427_RUNTIME.state_of_charge = soc;
    OPEN_CFW_BQ27427_RUNTIME.voltage_mv = voltage;
    OPEN_CFW_BQ27427_RUNTIME.average_current_ma = current;
    OPEN_CFW_BQ27427_RUNTIME.temperature_centi_c = temperature * 10;
    return 0;
}

int open_cfw_bq27427_init_wrapper(void)
{
    (void)open_cfw_bq27427_status_update();
    return 0;
}

int open_cfw_bq27427_hardware_init(void)
{
    open_cfw_bq27427_settings_apply_defaults();
    return open_cfw_bq27427_status_update() == 0 ? 0 : -1;
}
