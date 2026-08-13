#include <string.h>

#include "chg_bq27427_host.h"

open_cfw_test_bq27427_runtime_type open_cfw_test_bq27427_runtime;
uint8_t open_cfw_test_bq27427_registers[256];
uint8_t open_cfw_test_bq27427_dm[256][32];
uint8_t open_cfw_test_bq27427_current_subclass;
uint8_t open_cfw_test_bq27427_current_block;
uint8_t open_cfw_test_bq27427_last_bus;
uint8_t open_cfw_test_bq27427_last_address;
uint32_t open_cfw_test_bq27427_read_count;
uint32_t open_cfw_test_bq27427_write_count;
uint32_t open_cfw_test_bq27427_delay_count;
uint32_t open_cfw_test_bq27427_delay_total;

static uint8_t open_cfw_test_bq27427_checksum(void)
{
    unsigned sum = 0;
    size_t index;
    for (index = 0; index < 32; ++index) {
        sum += open_cfw_test_bq27427_dm[
            open_cfw_test_bq27427_current_subclass
        ][index];
    }
    return (uint8_t)(0xffu - (sum & 0xffu));
}

int open_cfw_test_bq27427_read(
    uint8_t bus, uint8_t address, const uint8_t *command,
    size_t command_length, uint8_t *data, size_t data_length
)
{
    size_t index;
    uint8_t reg;
    (void)command_length;
    open_cfw_test_bq27427_last_bus = bus;
    open_cfw_test_bq27427_last_address = address;
    ++open_cfw_test_bq27427_read_count;
    reg = command[0];
    if (reg == 0x40u) {
        memcpy(data, open_cfw_test_bq27427_dm[
            open_cfw_test_bq27427_current_subclass
        ], data_length);
    } else if (reg == 0x60u && data_length != 0u) {
        data[0] = open_cfw_test_bq27427_checksum();
    } else {
        for (index = 0; index < data_length; ++index) {
            data[index] = open_cfw_test_bq27427_registers[(uint8_t)(reg + index)];
        }
    }
    return 0;
}

int open_cfw_test_bq27427_write(
    uint8_t bus, uint8_t address, const uint8_t *command,
    size_t command_length, const uint8_t *data, size_t data_length
)
{
    size_t index;
    uint8_t reg;
    uint16_t value = 0u;
    (void)command_length;
    open_cfw_test_bq27427_last_bus = bus;
    open_cfw_test_bq27427_last_address = address;
    ++open_cfw_test_bq27427_write_count;
    reg = command[0];
    if (data_length != 0u) value = data[0];
    if (data_length > 1u) value |= (uint16_t)data[1] << 8;
    if (reg == 0x3eu && data_length != 0u) {
        open_cfw_test_bq27427_current_subclass = data[0];
    } else if (reg == 0x3fu && data_length != 0u) {
        open_cfw_test_bq27427_current_block = data[0];
    } else if (reg == 0x40u) {
        memcpy(open_cfw_test_bq27427_dm[
            open_cfw_test_bq27427_current_subclass
        ], data, data_length);
    } else {
        for (index = 0; index < data_length; ++index) {
            open_cfw_test_bq27427_registers[(uint8_t)(reg + index)] = data[index];
        }
    }
    if (reg == 0x00u && value == 0x0013u) {
        open_cfw_test_bq27427_registers[0x06] |= 0x10u;
    } else if (reg == 0x00u && value == 0x0042u) {
        open_cfw_test_bq27427_registers[0x06] &= (uint8_t)~0x10u;
    }
    return 0;
}

void open_cfw_test_bq27427_delay(uint32_t delay_ms)
{
    ++open_cfw_test_bq27427_delay_count;
    open_cfw_test_bq27427_delay_total += delay_ms;
}

void open_cfw_test_bq27427_reset(void)
{
    memset(&open_cfw_test_bq27427_runtime, 0,
        sizeof(open_cfw_test_bq27427_runtime));
    memset(open_cfw_test_bq27427_registers, 0,
        sizeof(open_cfw_test_bq27427_registers));
    memset(open_cfw_test_bq27427_dm, 0,
        sizeof(open_cfw_test_bq27427_dm));
    open_cfw_test_bq27427_current_subclass = 0;
    open_cfw_test_bq27427_current_block = 0;
    open_cfw_test_bq27427_last_bus = 0;
    open_cfw_test_bq27427_last_address = 0;
    open_cfw_test_bq27427_read_count = 0;
    open_cfw_test_bq27427_write_count = 0;
    open_cfw_test_bq27427_delay_count = 0;
    open_cfw_test_bq27427_delay_total = 0;
}
